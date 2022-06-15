from os.path import join
from time import time

import networkx as nx
import torch
from torch import nn
from logbook import Logger
from fastapi import APIRouter, Security

from ...schemas.api import ContractRequest, MultiBuggyGraphDetectReponse
from ...auth import get_api_key
from ...config import settings
from ...config import GRAPH_CLASSIFIER_CONFIG_ACCESS_CONTROL
from ...config import GRAPH_CLASSIFIER_CONFIG_ARITHMETIC
from ...config import GRAPH_CLASSIFIER_CONFIG_DENIAL_OF_SERVICE
from ...config import GRAPH_CLASSIFIER_CONFIG_FRONT_RUNNING
from ...config import GRAPH_CLASSIFIER_CONFIG_REENTRANCY
from ...config import GRAPH_CLASSIFIER_CONFIG_TIME_MANIPULATION
from ...config import GRAPH_CLASSIFIER_CONFIG_UNCHECKED_LOW_LEVEL_CALLS
from ...common.utils import init_graph_classificator
from ...common.utils import get_node_ids, get_binary_mask, \
                            get_line_numbers, get_edges, \
                            get_color_node, get_node_type, \
                            get_bug_lines
from ...common.process_graphs.call_graph_generator import generate_cg
from ...common.process_graphs.control_flow_graph_generator import generate_cfg
from ...common.process_graphs.combination_call_graph_and_control_flow_graph_helper import combine_cfg_cg
from ...consts import BugType, NodeFeature



torch.manual_seed(1)
logger = Logger(__name__)
router = APIRouter()


graph_classifier_access_control = init_graph_classificator(GRAPH_CLASSIFIER_CONFIG_ACCESS_CONTROL.CHECKPOINT,
                                                           GRAPH_CLASSIFIER_CONFIG_ACCESS_CONTROL.COMPRESSED_GRAPH,
                                                           settings.DEVICE)

graph_classifier_arithmetic = init_graph_classificator(GRAPH_CLASSIFIER_CONFIG_ARITHMETIC.CHECKPOINT,
                                                          GRAPH_CLASSIFIER_CONFIG_ARITHMETIC.COMPRESSED_GRAPH,
                                                          settings.DEVICE)
graph_classifier_denial_of_service = init_graph_classificator(GRAPH_CLASSIFIER_CONFIG_DENIAL_OF_SERVICE.CHECKPOINT,
                                                                 GRAPH_CLASSIFIER_CONFIG_DENIAL_OF_SERVICE.COMPRESSED_GRAPH,
                                                                 settings.DEVICE)   
graph_classifier_front_running = init_graph_classificator(GRAPH_CLASSIFIER_CONFIG_FRONT_RUNNING.CHECKPOINT,
                                                             GRAPH_CLASSIFIER_CONFIG_FRONT_RUNNING.COMPRESSED_GRAPH,
                                                             settings.DEVICE)                                     
graph_classifier_reentrancy = init_graph_classificator(GRAPH_CLASSIFIER_CONFIG_REENTRANCY.CHECKPOINT,
                                                          GRAPH_CLASSIFIER_CONFIG_REENTRANCY.COMPRESSED_GRAPH,
                                                          settings.DEVICE)
graph_classifier_time_manipulation = init_graph_classificator(GRAPH_CLASSIFIER_CONFIG_TIME_MANIPULATION.CHECKPOINT,
                                                                 GRAPH_CLASSIFIER_CONFIG_TIME_MANIPULATION.COMPRESSED_GRAPH,
                                                                 settings.DEVICE)
graph_classifier_unchecked_low_level_calls = init_graph_classificator(GRAPH_CLASSIFIER_CONFIG_UNCHECKED_LOW_LEVEL_CALLS.CHECKPOINT,
                                                                         GRAPH_CLASSIFIER_CONFIG_UNCHECKED_LOW_LEVEL_CALLS.COMPRESSED_GRAPH,
                                                                         settings.DEVICE)

MODEL_OPTS = {BugType.ACCESS_CONTROL: graph_classifier_access_control,
              BugType.ARITHMETIC: graph_classifier_arithmetic,
              BugType.DENIAL_OF_SERVICE: graph_classifier_denial_of_service,
              BugType.FRONT_RUNNING: graph_classifier_front_running,
              BugType.REENTRANCY: graph_classifier_reentrancy,
              BugType.TIME_MANIPULATION: graph_classifier_time_manipulation,
              BugType.UNCHECKED_LOW_LEVEL_CALLS: graph_classifier_unchecked_low_level_calls}


@router.post('/graph/{node_feature}', response_model=MultiBuggyGraphDetectReponse, dependencies=[Security(get_api_key)])
async def extra_detect_line_level_bugs(data: ContractRequest,
                                       node_feature: NodeFeature = NodeFeature.NODE_TYPE):
    # Generate graph for comming contract
    sm_content = data.smart_contract.decode("utf-8")
    sm_length = len(sm_content.split('\n'))
    sm_name = 'contract_graph.sol'
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
    # total_reports = {'smart_contract_length': sm_length}
    for bug, model in MODEL_OPTS.items():
        report = {'type': bug}
        original_graph = model.nx_graph
        extra_graph = nx.disjoint_union(original_graph, cfg_cg_graph)
        file_ids = get_node_ids(extra_graph, [sm_name])
        line_numbers = get_line_numbers(extra_graph, [sm_name])
        # Inference
        begin_time = time()
        with torch.no_grad():
            logits = model.extend_forward(extra_graph, [sm_name])
            preds = nn.functional.softmax(logits, dim=1)
            _, indices = torch.max(preds, dim=1)
            preds = indices.long().cpu().tolist()
            report['runtime'] = int((time() - begin_time) * 1000)
            report['vulnerability'] = preds[0]
            # results = [{'id':i , 'code_lines': line_numbers[i], 'vulnerability': preds[i]} for i in range(len(line_numbers))]
            # report['results'] = results
        total_reports.append(report)
    logger.debug(total_reports)
    response = {'summaries': total_reports,
                'smart_contract_length': sm_length}
    return response
