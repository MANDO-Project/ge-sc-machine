from dataclasses import field
from unittest import result
from logbook import Logger
from fastapi import APIRouter, Security

import torch
from torch._C import device

from ...auth import get_api_key
from ...config import settings_access_control,settings_arithmetic,settings_denial_of_service,settings_front_running,settings_reentrancy,settings_time_manipulation,settings_unchecked_low_level_calls
from ...common.utils import check_gpu
from ...common.utils import init_line_node_classificator
from ...common.utils import get_node_ids, get_binary_mask, get_line_numbers, get_edges,get_color_node,get_node_type
from ...schemas.api import NodeRequest, NodeResponse 


logger = Logger(__name__)
router = APIRouter()

is_gpu = check_gpu()
# node_classifier_access_control = init_line_node_classificator(settings_access_control.LINE.CHECKPOINT,
#                                           settings_access_control.LINE.COMPRESSED_GRAPH,
#                                           settings_access_control.LINE.DATASET,
#                                           settings_access_control.LINE.feature_extractor,
#                                           settings_access_control.DEVICE)
# node_classifier_arithmetic = init_line_node_classificator(settings_arithmetic.LINE.CHECKPOINT,
#                                           settings_arithmetic.LINE.COMPRESSED_GRAPH,
#                                           settings_arithmetic.LINE.DATASET,
#                                           settings_arithmetic.LINE.feature_extractor,
#                                           settings_arithmetic.DEVICE)
# node_classifier_denial_of_service = init_line_node_classificator(settings_denial_of_service.LINE.CHECKPOINT,
#                                           settings_denial_of_service.LINE.COMPRESSED_GRAPH,
#                                           settings_denial_of_service.LINE.DATASET,
#                                           settings_denial_of_service.LINE.feature_extractor,
#                                           settings_denial_of_service.DEVICE)   
# node_classifier_front_running = init_line_node_classificator(settings_front_running.LINE.CHECKPOINT,
#                                           settings_front_running.LINE.COMPRESSED_GRAPH,
#                                           settings_front_running.LINE.DATASET,
#                                           settings_front_running.LINE.feature_extractor,
#                                           settings_front_running.DEVICE)                                     
node_classifier_reentrancy = init_line_node_classificator(settings_reentrancy.LINE.CHECKPOINT,
                                          settings_reentrancy.LINE.COMPRESSED_GRAPH,
                                          settings_reentrancy.LINE.feature_extractor,
                                          settings_reentrancy.DEVICE)
# node_classifier_time_manipulation = init_line_node_classificator(settings_time_manipulation.LINE.CHECKPOINT,
#                                           settings_time_manipulation.LINE.COMPRESSED_GRAPH,
#                                           settings_time_manipulation.LINE.DATASET,
#                                           settings_time_manipulation.LINE.feature_extractor,
#                                           settings_time_manipulation.DEVICE)
# node_classifier_unchecked_low_level_calls = init_line_node_classificator(settings_unchecked_low_level_calls.LINE.CHECKPOINT,
#                                           settings_unchecked_low_level_calls.LINE.COMPRESSED_GRAPH,
#                                           settings_unchecked_low_level_calls.LINE.DATASET,
#                                           settings_unchecked_low_level_calls.LINE.feature_extractor,
#                                           settings_unchecked_low_level_calls.DEVICE)


@router.post('/check_device', dependencies=[Security(get_api_key)])
async def check_device():
    if is_gpu:
        device = torch.cuda.current_device()
        device_name = torch.cuda.get_device_name(0)
    else:
        device_name = 'cpu'
    return {'device': device_name}


@router.post('/line/unchecked_low_level_calls', response_model=NodeResponse, dependencies=[Security(get_api_key)])
async def detect_line_level_bugs(item: NodeRequest):
    node_classifier_unchecked_low_level_calls.eval()
    file_ids = get_node_ids(node_classifier_unchecked_low_level_calls.nx_graph, [item.filename])
    line_numbers = get_line_numbers(node_classifier_unchecked_low_level_calls.nx_graph, [item.filename])
    file_edges=get_edges(node_classifier_unchecked_low_level_calls.nx_graph, [item.filename],file_ids)
    color_nodes=get_color_node(node_classifier_unchecked_low_level_calls.nx_graph, [item.filename])
    with torch.no_grad():
        logits = node_classifier_unchecked_low_level_calls()
        logits = logits.to(settings_unchecked_low_level_calls.DEVICE)
        file_mask = get_binary_mask(node_classifier_unchecked_low_level_calls.total_nodes, file_ids)
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


@router.post('/line/access_control', response_model=NodeResponse, dependencies=[Security(get_api_key)])
async def detect_line_level_bugs(item: NodeRequest):
    node_classifier_access_control.eval()
    file_ids = get_node_ids(node_classifier_access_control.nx_graph, [item.filename])
    line_numbers = get_line_numbers(node_classifier_access_control.nx_graph, [item.filename])
    file_edges=get_edges(node_classifier_access_control.nx_graph, [item.filename],file_ids)
    color_nodes=get_color_node(node_classifier_access_control.nx_graph, [item.filename])
    node_type=get_node_type(node_classifier_access_control.nx_graph, [item.filename])
    with torch.no_grad():
        logits = node_classifier_access_control()
        logits = logits.to(settings_access_control.DEVICE)
        file_mask = get_binary_mask(node_classifier_access_control.total_nodes, file_ids)
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


@router.post('/line/arithmetic', response_model=NodeResponse, dependencies=[Security(get_api_key)])
async def detect_line_level_bugs(item: NodeRequest):
    node_classifier_arithmetic.eval()
    file_ids = get_node_ids(node_classifier_arithmetic.nx_graph, [item.filename])
    line_numbers = get_line_numbers(node_classifier_arithmetic.nx_graph, [item.filename])
    file_edges=get_edges(node_classifier_arithmetic.nx_graph, [item.filename],file_ids)
    color_nodes=get_color_node(node_classifier_arithmetic.nx_graph, [item.filename])
    node_type=get_node_type(node_classifier_arithmetic.nx_graph, [item.filename])
    with torch.no_grad():
        logits = node_classifier_arithmetic()
        logits = logits.to(settings_arithmetic.DEVICE)
        file_mask = get_binary_mask(node_classifier_arithmetic.total_nodes, file_ids)
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


@router.post('/line/denial_of_service', response_model=NodeResponse, dependencies=[Security(get_api_key)])
async def detect_line_level_bugs(item: NodeRequest):
    node_classifier_denial_of_service.eval()
    file_ids = get_node_ids(node_classifier_denial_of_service.nx_graph, [item.filename])
    line_numbers = get_line_numbers(node_classifier_denial_of_service.nx_graph, [item.filename])
    file_edges=get_edges(node_classifier_denial_of_service.nx_graph, [item.filename],file_ids)
    color_nodes=get_color_node(node_classifier_denial_of_service.nx_graph, [item.filename])
    node_type=get_node_type(node_classifier_denial_of_service.nx_graph, [item.filename])
    with torch.no_grad():
        logits = node_classifier_denial_of_service()
        logits = logits.to(settings_denial_of_service.DEVICE)
        file_mask = get_binary_mask(node_classifier_denial_of_service.total_nodes, file_ids)
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


@router.post('/line/front_running', response_model=NodeResponse, dependencies=[Security(get_api_key)])
async def detect_line_level_bugs(item: NodeRequest):
    
    node_classifier_front_running.eval()
    file_ids = get_node_ids(node_classifier_front_running.nx_graph, [item.filename])
    line_numbers = get_line_numbers(node_classifier_front_running.nx_graph, [item.filename])
    file_edges=get_edges(node_classifier_front_running.nx_graph, [item.filename],file_ids)
    color_nodes=get_color_node(node_classifier_front_running.nx_graph, [item.filename])
    node_type=get_node_type(node_classifier_front_running.nx_graph, [item.filename])
    with torch.no_grad():
        logits = node_classifier_front_running()
        logits = logits.to(settings_front_running.DEVICE)
        file_mask = get_binary_mask(node_classifier_front_running.total_nodes, file_ids)
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
        logits = logits.to(settings_reentrancy.DEVICE)
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


@router.post('/nodetype/reentrancy/extra', response_model=NodeResponse, dependencies=[Security(get_api_key)])
async def extra_detect_reentrancy_line_level_bugs(item: NodeRequest):
    
    node_classifier_reentrancy.eval()
    file_ids = get_node_ids(node_classifier_reentrancy.nx_graph, [item.filename])
    line_numbers = get_line_numbers(node_classifier_reentrancy.nx_graph, [item.filename])
    file_edges=get_edges(node_classifier_reentrancy.nx_graph, [item.filename],file_ids)
    color_nodes=get_color_node(node_classifier_reentrancy.nx_graph, [item.filename])
    node_type=get_node_type(node_classifier_reentrancy.nx_graph, [item.filename])
    with torch.no_grad():
        logits = node_classifier_reentrancy()
        logits = logits.to(settings_reentrancy.DEVICE)
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
