from os.path import join
from time import time

import networkx as nx
import torch
from torch import nn
from logbook import Logger
from fastapi import APIRouter, Security

from ...auth import get_api_key
from ...config import settings
from ...schemas.api import ContractRequest, FineGrainedDetectReponse
from ...schemas.fields import Node, Edge, GraphStructure
from ...consts import BugType, Message
from ...common.utils import check_gpu
from ...common.utils import get_node_ids, get_binary_mask, \
                            get_line_numbers, get_edges, \
                            get_color_node, get_node_type, \
                            get_bug_lines
from ...common.process_graphs.call_graph_generator import generate_cg
from ...common.process_graphs.control_flow_graph_generator import generate_cfg
from ...common.process_graphs.combination_call_graph_and_control_flow_graph_helper import combine_cfg_cg
from ...config import NODE_MODEL_OPTS

torch.manual_seed(1)
logger = Logger(__name__)
router = APIRouter()



@router.post('/node/{bug_type}', response_model=FineGrainedDetectReponse, dependencies=[Security(get_api_key)])
async def fine_graind_detection(data: ContractRequest,
                                                  bug_type: BugType = BugType.REENTRANCY,
                                                  get_graph: bool = True):
    # Init reponse
    bug_report = {}
    # Get models
    node_classifier = NODE_MODEL_OPTS[bug_type]
    # Generate graph for comming contract
    sm_content = data.smart_contract.decode("utf-8")
    sm_name = data.contract_name
    sm_path = join(settings.STORAGE, sm_name)
    with open(sm_path, 'w') as f:
        f.write(sm_content)
    sm_length = len(sm_content.split('\n'))
    bug_report['smart_contract_length'] = sm_length
    cfg_graph = generate_cfg(sm_path)
    if cfg_graph is None:
        bug_report.update({'message': Message.ILLEGAL_CONTRACT})
        return FineGrainedDetectReponse.parse_obj(bug_report)
    cg_graph = generate_cg(sm_path)
    if cfg_graph is None:
        bug_report.update({'message': Message.ILLEGAL_CONTRACT})
        return FineGrainedDetectReponse.parse_obj(bug_report)
    cg_graph = generate_cg(sm_path)
    cfg_cg_graph = combine_cfg_cg(cfg_graph, cg_graph)
    bug_report['bug_type'] = bug_type
    original_graph = node_classifier.nx_graph
    extra_graph = nx.disjoint_union(original_graph, cfg_cg_graph)
    file_ids = get_node_ids(extra_graph, [sm_name])
    line_numbers = get_line_numbers(extra_graph, [sm_name])
    file_edges=get_edges(extra_graph, [sm_name],file_ids)
    node_type=get_node_type(extra_graph, [sm_name])
    # Inference
    begin_time = time()
    try:
        with torch.no_grad():
            logits, _ = node_classifier.extend_forward(extra_graph)
    except Exception as e:
        logger.info(e)
        return FineGrainedDetectReponse.parse_obj({'messages': Message.STRANGE_GRAPH})
    file_mask = get_binary_mask(len(extra_graph), file_ids)
    preds = logits[file_mask]
    preds = nn.functional.softmax(preds, dim=1)
    _, indices = torch.max(preds, dim=1)
    preds = indices.long().cpu().tolist()
    nodes=[]
    for i in range(len(line_numbers)):
        string=''
        for item in line_numbers[i]:
            string=string+"%s"%str(item)+' '
        node_name = f'id: {i}, node type: {node_type[i]} \ncode lines: {str(line_numbers[i])}'
        string="id:%s,"%str(i)+ "node type: %s,"%str(node_type[i])+"\ncode lines: "+ string +"."
        node = Node(id=i, name=node_name, vulnerability=preds[i], code_lines=line_numbers[i])
        nodes.append(node)
    bug_report['results'] = nodes
    if get_graph:
        edges=[Edge(source=file_edges[i][0], target=file_edges[i][1]) for i in range(len(file_edges))]
        graph = GraphStructure(nodes=nodes, edges=edges)
        bug_report['graph'] = graph
    bug_report['runtime'] = int((time() - begin_time) * 1000)
    bug_report['number_of_bug_node'] = preds.count(1)
    bug_report['number_of_normal_node'] = preds.count(0)
    bug_report['vulnerability'] = 0 if bug_report['number_of_bug_node'] == 0 else 1
    bug_report['message'] = Message.OK
    logger.info(bug_report)
    return bug_report

