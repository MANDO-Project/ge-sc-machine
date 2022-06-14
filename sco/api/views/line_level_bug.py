from os.path import join
from time import time

import networkx as nx
import torch
from torch import nn
from logbook import Logger
from fastapi import APIRouter, Security

from ...auth import get_api_key
from ...config import settings
from ...config import NODE_CLASSIFIER_CONFIG_ACCESS_CONTROL
from ...config import NODE_CLASSIFIER_CONFIG_ARITHMETIC
from ...config import NODE_CLASSIFIER_CONFIG_DENIAL_OF_SERVICE
from ...config import NODE_CLASSIFIER_CONFIG_FRONT_RUNNING
from ...config import NODE_CLASSIFIER_CONFIG_REENTRANCY
from ...config import NODE_CLASSIFIER_CONFIG_TIME_MANIPULATION
from ...config import NODE_CLASSIFIER_CONFIG_UNCHECKED_LOW_LEVEL_CALLS
from ...schemas.api import NodeRequest, ContractRequest, NodeDetectReponse, MultiBuggyNodeDetectReponse, NodeResponse
from ...consts import BugType, NodeFeature
from ...common.utils import check_gpu
from ...common.utils import init_node_classificator
from ...common.utils import get_node_ids, get_binary_mask, \
                            get_line_numbers, get_edges, \
                            get_color_node, get_node_type, \
                            get_bug_lines
from ...common.process_graphs.call_graph_generator import generate_cg
from ...common.process_graphs.control_flow_graph_generator import generate_cfg
from ...common.process_graphs.combination_call_graph_and_control_flow_graph_helper import combine_cfg_cg


torch.manual_seed(1)
logger = Logger(__name__)
router = APIRouter()


CATEGORIES_OF_HEATMAP = 20

is_gpu = check_gpu()

# Init Node classifier models
node_classifier_access_control = init_node_classificator(NODE_CLASSIFIER_CONFIG_ACCESS_CONTROL.CHECKPOINT,
                                                              NODE_CLASSIFIER_CONFIG_ACCESS_CONTROL.COMPRESSED_GRAPH,
                                                              settings.DEVICE)
node_classifier_arithmetic = init_node_classificator(NODE_CLASSIFIER_CONFIG_ARITHMETIC.CHECKPOINT,
                                                          NODE_CLASSIFIER_CONFIG_ARITHMETIC.COMPRESSED_GRAPH,
                                                          settings.DEVICE)
node_classifier_denial_of_service = init_node_classificator(NODE_CLASSIFIER_CONFIG_DENIAL_OF_SERVICE.CHECKPOINT,
                                                                 NODE_CLASSIFIER_CONFIG_DENIAL_OF_SERVICE.COMPRESSED_GRAPH,
                                                                 settings.DEVICE)   
node_classifier_front_running = init_node_classificator(NODE_CLASSIFIER_CONFIG_FRONT_RUNNING.CHECKPOINT,
                                                             NODE_CLASSIFIER_CONFIG_FRONT_RUNNING.COMPRESSED_GRAPH,
                                                             settings.DEVICE)                                     
node_classifier_reentrancy = init_node_classificator(NODE_CLASSIFIER_CONFIG_REENTRANCY.CHECKPOINT,
                                                          NODE_CLASSIFIER_CONFIG_REENTRANCY.COMPRESSED_GRAPH,
                                                          settings.DEVICE)
node_classifier_time_manipulation = init_node_classificator(NODE_CLASSIFIER_CONFIG_TIME_MANIPULATION.CHECKPOINT,
                                                                 NODE_CLASSIFIER_CONFIG_TIME_MANIPULATION.COMPRESSED_GRAPH,
                                                                 settings.DEVICE)
node_classifier_unchecked_low_level_calls = init_node_classificator(NODE_CLASSIFIER_CONFIG_UNCHECKED_LOW_LEVEL_CALLS.CHECKPOINT,
                                                                         NODE_CLASSIFIER_CONFIG_UNCHECKED_LOW_LEVEL_CALLS.COMPRESSED_GRAPH,
                                                                         settings.DEVICE)

MODEL_OPTS = {BugType.ACCESS_CONTROL: node_classifier_access_control,
              BugType.ARITHMETIC: node_classifier_arithmetic,
              BugType.DENIAL_OF_SERVICE: node_classifier_denial_of_service,
              BugType.FRONT_RUNNING: node_classifier_front_running,
              BugType.REENTRANCY: node_classifier_reentrancy,
              BugType.TIME_MANIPULATION: node_classifier_time_manipulation,
              BugType.UNCHECKED_LOW_LEVEL_CALLS: node_classifier_unchecked_low_level_calls}


@router.post('/check_device', dependencies=[Security(get_api_key)])
async def check_device():
    if is_gpu:
        device = torch.cuda.current_device()
        device_name = torch.cuda.get_device_name(0)
    else:
        device_name = 'cpu'
    return {'device': device_name}


@router.post('/line/reentrancy', response_model=NodeResponse, dependencies=[Security(get_api_key)])
async def detect_reentrancy_line_level_bugs(item: NodeRequest):
    node_classifier_reentrancy.eval()
    file_ids = get_node_ids(node_classifier_reentrancy.nx_graph, [item.filename])
    line_numbers = get_line_numbers(node_classifier_reentrancy.nx_graph, [item.filename])
    file_edges=get_edges(node_classifier_reentrancy.nx_graph, [item.filename],file_ids)
    color_nodes=get_color_node(node_classifier_reentrancy.nx_graph, [item.filename])
    node_type=get_node_type(node_classifier_reentrancy.nx_graph, [item.filename])
    with torch.no_grad():
        logits = node_classifier_reentrancy()
        logits = logits.to(settings.DEVICE)
        file_mask = get_binary_mask(node_classifier_reentrancy.total_nodes, file_ids)
        preds = logits[file_mask]
        _, indices = torch.max(preds, dim=1)
        preds = indices.long().cpu().tolist()
        assert len(preds) == len(line_numbers)
        links=[{"source": "%s"%str(file_edges[i][0]), "target": "%s"%str(file_edges[i][1])} for i in range(len(file_edges))]
        results = [{'id':i , 'code_lines': line_numbers[i], 'vulnerability': preds[i]} for i in range(len(line_numbers))]
        nodes=[]
        for i in range(len(line_numbers)):
            string=''
            for item in line_numbers[i]:
                string=string+"%s"%str(item)+' '
            string="id:%s,"%str(i)+ "node type: %s,"%str(node_type[i])+"\ncode lines: "+ string +"."
            node={'id':"%s"%str(i) ,'name':string,'error':preds[i],'color':color_nodes[i],'code_lines': line_numbers[i]}
            nodes.append(node)
        graph={"nodes":nodes,"links":links}
    return {'message': 'Loaded model successfully',
            'results': results,
            'graph':graph}


@router.post('/node/{bug_type}/{node_feature}', response_model=NodeDetectReponse, dependencies=[Security(get_api_key)])
async def extra_detect_reentrancy_line_level_bugs(data: ContractRequest,
                                                  bug_type: BugType = BugType.REENTRANCY,
                                                  node_feature: NodeFeature = NodeFeature.NODE_TYPE):
    # Get models
    node_classifier = MODEL_OPTS[bug_type]
    # Generate graph for comming contract
    sm_content = data.smart_contract.decode("utf-8")
    sm_name = 'contract_0.sol'
    sm_path = join('./sco/_static', sm_name)
    with open(sm_path, 'w') as f:
        f.write(sm_content)
    cfg_graph = generate_cfg(sm_path)
    if cfg_graph is None:
        return {'message': 'Found a illegal solidity smart contract'}
    cg_graph = generate_cg(sm_path)
    if cfg_graph is None:
        return {'message': 'Found a illegal solidity smart contract'}
    cg_graph = generate_cg(sm_path)
    cfg_cg_graph = combine_cfg_cg(cfg_graph, cg_graph)
    original_graph = node_classifier.nx_graph
    extra_graph = nx.disjoint_union(original_graph, cfg_cg_graph)
    file_ids = get_node_ids(extra_graph, [sm_name])
    line_numbers = get_line_numbers(extra_graph, [sm_name])
    file_edges=get_edges(extra_graph, [sm_name],file_ids)
    color_nodes=get_color_node(extra_graph, [sm_name])
    node_type=get_node_type(extra_graph, [sm_name])
    # Inference
    with torch.no_grad():
        logits, _ = node_classifier.extend_forward(extra_graph)
        file_mask = get_binary_mask(len(extra_graph), file_ids)
        preds = logits[file_mask]
        preds = nn.functional.softmax(preds, dim=1)
        _, indices = torch.max(preds, dim=1)
        preds = indices.long().cpu().tolist()
        assert len(preds) == len(line_numbers)
        links=[{"source": "%s"%str(file_edges[i][0]), "target": "%s"%str(file_edges[i][1])} for i in range(len(file_edges))]
        results = [{'id':i , 'code_lines': line_numbers[i], 'vulnerability': preds[i]} for i in range(len(line_numbers))]
        nodes=[]
        for i in range(len(line_numbers)):
            string=''
            for item in line_numbers[i]:
                string=string+"%s"%str(item)+' '
            string="id:%s,"%str(i)+ "node type: %s,"%str(node_type[i])+"\ncode lines: "+ string +"."
            node={'id':"%s"%str(i) ,'name':string,'error':preds[i],'color':color_nodes[i],'code_lines': line_numbers[i]}
            nodes.append(node)
        graph={"nodes":nodes,"links":links}
    return {'message': 'Loaded model successfully',
            'results': results,
            'graph':graph}


@router.post('/node/{node_feature}', response_model=MultiBuggyNodeDetectReponse, dependencies=[Security(get_api_key)])
async def extra_detect_line_level_bugs(data: ContractRequest,
                                       node_feature: NodeFeature = NodeFeature.NODE_TYPE):
    # Generate graph for comming contract
    sm_content = data.smart_contract.decode("utf-8")
    sm_length = len(sm_content.split('\n'))
    sm_name = 'contract_0.sol'
    sm_path = join('./sco/_static', sm_name)
    with open(sm_path, 'w') as f:
        f.write(sm_content)
    cfg_graph = generate_cfg(sm_path)
    if cfg_graph is None:
        return {'message': 'Found a illegal solidity smart contract'}
    cg_graph = generate_cg(sm_path)
    if cfg_graph is None:
        return {'message': 'Found a illegal solidity smart contract'}
    cfg_cg_graph = combine_cfg_cg(cfg_graph, cg_graph)
    total_reports = []
    for bug, model in MODEL_OPTS.items():
        report = {'type': bug}
        original_graph = model.nx_graph
        extra_graph = nx.disjoint_union(original_graph, cfg_cg_graph)
        file_ids = get_node_ids(extra_graph, [sm_name])
        line_numbers = get_line_numbers(extra_graph, [sm_name])
        # Inference
        begin_time = time()
        with torch.no_grad():
            logits, _ = model.extend_forward(extra_graph)
            file_mask = get_binary_mask(len(extra_graph), file_ids)
            preds = logits[file_mask]
            preds = nn.functional.softmax(preds, dim=1)
            _, indices = torch.max(preds, dim=1)
            preds = indices.long().cpu().tolist()
            report['runtime'] = int((time() - begin_time) * 1000)
            report['number_of_bug_node'] = preds.count(1)
            report['number_of_normal_node'] = preds.count(0)
            assert len(preds) == len(line_numbers)
            bug_lines = get_bug_lines(preds, line_numbers)
            # Considering checking over here
            # assert len(bug_lines) == 0 or max(bug_lines) <= sm_length
            # Generate heatmap data series
            bug_density = []
            max_line = sm_length if len(bug_lines) == 0 else max(bug_lines)
            bug_population = torch.zeros(max_line + 1)  # Cuz the begin of code lines is 1
            bug_population[bug_lines] = 1
            bug_population = bug_population[1:sm_length]
            line_per_category = sm_length/CATEGORIES_OF_HEATMAP
            for i in range(CATEGORIES_OF_HEATMAP):
                bug_density.append(bug_population[int(i * line_per_category) : int((i+1) * line_per_category)].tolist().count(1))
            report['bug_density'] = bug_density
            # results = [{'id':i , 'code_lines': line_numbers[i], 'vulnerability': preds[i]} for i in range(len(line_numbers))]
            # report['results'] = results
        total_reports.append(report)
    logger.debug(total_reports)
    response = {'summaries': total_reports,
                'smart_contract_length': sm_length,
                'heatmap_categories': CATEGORIES_OF_HEATMAP}
    return response
