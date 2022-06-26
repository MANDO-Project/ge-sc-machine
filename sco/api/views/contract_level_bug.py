from os.path import join
from time import time

import networkx as nx
import torch
from torch import nn
from logbook import Logger
from fastapi import APIRouter, Security

from ...auth import get_api_key
from ...schemas.api import ContractRequest, CoarseGrainedDetectReponse
from ...common.process_graphs.call_graph_generator import generate_cg
from ...common.process_graphs.control_flow_graph_generator import generate_cfg
from ...common.process_graphs.combination_call_graph_and_control_flow_graph_helper import combine_cfg_cg
from ...consts import BugType, Message
from ...config import GRAPH_MODEL_OPTS



torch.manual_seed(1)
logger = Logger(__name__)
router = APIRouter()


@router.post('/graph/{bug_type}', response_model=CoarseGrainedDetectReponse, dependencies=[Security(get_api_key)])
async def coarse_grained_detection(data: ContractRequest,
                                   bug_type: BugType = BugType.REENTRANCY):
    # Init reponse
    bug_report = {}
    # Get models
    graph_classifier = GRAPH_MODEL_OPTS[bug_type]
    # Generate graph for comming contract
    sm_content = data.smart_contract.decode("utf-8")
    sm_name = 'contract_graph.sol'
    sm_path = join('./sco/_static', sm_name)
    with open(sm_path, 'w') as f:
        f.write(sm_content)
    sm_length = len(sm_content.split('\n'))
    bug_report['smart_contract_length'] = sm_length
    cfg_graph = generate_cfg(sm_path)
    if cfg_graph is None:
        bug_report.update({'message': Message.ILLEGAL_CONTRACT})
        return CoarseGrainedDetectReponse.parse_obj(bug_report)
    cg_graph = generate_cg(sm_path)
    if cfg_graph is None:
        bug_report.update({'message': Message.ILLEGAL_CONTRACT})
        return CoarseGrainedDetectReponse.parse_obj(bug_report)
    cfg_cg_graph = combine_cfg_cg(cfg_graph, cg_graph)
    bug_report['bug_type'] = bug_type
    original_graph = graph_classifier.nx_graph
    extra_graph = nx.disjoint_union(original_graph, cfg_cg_graph)
    # Inference
    begin_time = time()
    try:
        with torch.no_grad():
            logits = graph_classifier.extend_forward(extra_graph, [sm_name])
    except Exception as e:
        logger.info(e)
        return CoarseGrainedDetectReponse.parse_obj({'messages': Message.STRANGE_GRAPH})
    preds = nn.functional.softmax(logits, dim=1)
    _, indices = torch.max(preds, dim=1)
    preds = indices.long().cpu().tolist()
    bug_report['runtime'] = int((time() - begin_time) * 1000)
    bug_report['vulnerability'] = preds[0]
    bug_report['message'] = Message.OK
    logger.info(bug_report)
    return bug_report
