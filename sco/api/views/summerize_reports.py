from os.path import join
from time import time

import networkx as nx
import torch
from torch import nn
from logbook import Logger
from fastapi import APIRouter, Security

from ...auth import get_api_key
from ...config import settings
from ...schemas.api import ContractRequest, MultiBuggyNodeDetectReponse
from ...consts import NodeFeature
from ...common.utils import check_gpu
from ...common.utils import get_node_ids, get_binary_mask, \
                            get_line_numbers, get_edges, \
                            get_color_node, get_node_type, \
                            get_bug_lines
from ...common.process_graphs.call_graph_generator import generate_cg
from ...common.process_graphs.control_flow_graph_generator import generate_cfg
from ...common.process_graphs.combination_call_graph_and_control_flow_graph_helper import combine_cfg_cg
from ...config import NODE_MODEL_OPTS
from ...config import GRAPH_MODEL_OPTS


torch.manual_seed(1)
logger = Logger(__name__)
router = APIRouter()
CATEGORIES_OF_HEATMAP = 15


is_gpu = check_gpu()

@router.get('/check_device', dependencies=[Security(get_api_key)])
async def check_device():
    if is_gpu:
        device_name = torch.cuda.get_device_name(0)
    else:
        device_name = 'cpu'
    return {'device': device_name, 'tag': settings.SERVER_TAG}


@router.post('/{node_feature}', response_model=MultiBuggyNodeDetectReponse, dependencies=[Security(get_api_key)], include_in_schema=False)
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
        return {'messages': 'Found an illegal solidity smart contract'}
    cg_graph = generate_cg(sm_path)
    if cg_graph is None:
        return {'messages': 'Found an illegal solidity smart contract'}
    cfg_cg_graph = combine_cfg_cg(cfg_graph, cg_graph)
    total_reports = []
    for bug in NODE_MODEL_OPTS.keys():
        node_model = NODE_MODEL_OPTS[bug]
        graph_model = GRAPH_MODEL_OPTS[bug]
        report = {'type': bug}
        # Inference Graph level
        original_graph = graph_model.nx_graph
        extra_graph = nx.disjoint_union(original_graph, cfg_cg_graph)
        begin_time = time()
        with torch.no_grad():
            try:
                logits = graph_model.extend_forward(extra_graph, [sm_name])
            except Exception as e:
                logger.info(e)
                return {'messages': 'Found non-existent nodes/edges in the graph!'}
            graph_preds = nn.functional.softmax(logits, dim=1)
            _, indices = torch.max(graph_preds, dim=1)
            graph_preds = indices.long().cpu().tolist()
            report['graph_runtime'] = int((time() - begin_time) * 1000)
        # Inference Node level
        original_graph = node_model.nx_graph
        extra_graph = nx.disjoint_union(original_graph, cfg_cg_graph)
        file_ids = get_node_ids(extra_graph, [sm_name])
        line_numbers = get_line_numbers(extra_graph, [sm_name])
        file_edges=get_edges(extra_graph, [sm_name],file_ids)
        color_nodes=get_color_node(extra_graph, [sm_name])
        node_type=get_node_type(extra_graph, [sm_name])
        begin_time = time()
        with torch.no_grad():
            try:
                logits, _ = node_model.extend_forward(extra_graph)
            except Exception as e:
                logger.info(e)
                return {'messages': 'Found non-existent nodes/edges!'}
            file_mask = get_binary_mask(len(extra_graph), file_ids)
            node_preds = logits[file_mask]
            node_preds = nn.functional.softmax(node_preds, dim=1)
            _, indices = torch.max(node_preds, dim=1)
            node_preds = indices.long().cpu().tolist()
        report['node_runtime'] = int((time() - begin_time) * 1000)
        logger.info('Graph {} detection {}'.format(bug, str(graph_preds)))
        logger.info('Node {} detection {}'.format(bug, str(node_preds)))
        if graph_preds[0] == 0:
            node_preds = [0] * len(node_preds)
        report['number_of_bug_node'] = node_preds.count(1)
        report['vulnerability'] = 0 if report['number_of_bug_node'] == 0 else 1
        report['vulnerability'] = graph_preds[0]
        report['number_of_normal_node'] = node_preds.count(0)
        assert len(node_preds) == len(line_numbers)
        # Get graph information
        links=[{"source": "%s"%str(file_edges[i][0]), "target": "%s"%str(file_edges[i][1])} for i in range(len(file_edges))]
        # results = [{'id':i , 'code_lines': line_numbers[i], 'vulnerability': node_preds[i]} for i in range(len(line_numbers))]
        results = []
        nodes=[]
        for i in range(len(line_numbers)):
            string=''
            for item in line_numbers[i]:
                string=string+"%s"%str(item)+' '
            _pred = node_preds[i]
            _pred = 0 if (node_type[i] == 'FUNCTION_NAME' 
                          or node_type[i] == 'CONTRACT_FUNCTION' 
                          or node_type[i] == 'ENTRY_POINT'
                          or node_type[i] == 'END_IF') else node_preds[i]
            string="id:%s,"%str(i)+ "node type: %s,"%str(node_type[i])+"\ncode lines: "+ string +"."
            node={'id':"%s"%str(i) ,'name':string,'error':_pred,'color':color_nodes[i],'code_lines': line_numbers[i]}
            nodes.append(node)
            results.append({'id':i , 'code_lines': line_numbers[i], 'vulnerability': _pred})
        graph={"nodes":nodes,"links":links}
        report['results'] = results
        report['graph'] = graph
        bug_lines = get_bug_lines(node_preds, line_numbers)
        # Considering checking over here
        # assert len(bug_lines) == 0 or max(bug_lines) <= sm_length
        # Generate heatmap data series
        max_line = sm_length if len(bug_lines) == 0 else max(bug_lines)
        bug_population = torch.zeros(max_line + 1)  # Cuz the begin of code lines is 1
        bug_population[bug_lines] = 1
        bug_population = bug_population[1:sm_length]
        line_per_category = sm_length/CATEGORIES_OF_HEATMAP
        bug_density = []
        for i in range(CATEGORIES_OF_HEATMAP):
            heatmap_point = {}
            heatmap_point['x'] = f'{int(i * line_per_category) + 1}-{int((i+1) * line_per_category)}'
            heatmap_point['y'] = bug_population[int(i * line_per_category) : int((i+1) * line_per_category)].tolist().count(1)
            bug_density.append(heatmap_point)
        report['bug_density'] = bug_density
        total_reports.append(report)
    logger.debug(total_reports)
    response = {'summaries': total_reports,
                'smart_contract_length': sm_length,
                'heatmap_categories': CATEGORIES_OF_HEATMAP,
                'messages': 'OK'}
    # logger.info(total_reports)
    return response
