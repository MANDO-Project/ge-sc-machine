import sys
import os

import torch
import numpy as np
from logbook import Logger

sys.path.append("/Users/minh/Documents/2022/smart_contract/mando/ge-sc/") 
from sco_models.model_hgt import HGTVulNodeClassifier

logger = Logger(__name__)


def check_gpu():
    return torch.cuda.is_available()


def init_line_node_classificator(ckpt, compressed_graph, feature_extractor, device):
    model = HGTVulNodeClassifier(compressed_graph, feature_extractor, node_feature='nodetype', device=device)
    model.load_state_dict(torch.load(ckpt))
    model.to(device)
    return model


def get_binary_mask(total_size, indices):
    mask = torch.zeros(total_size)
    mask[indices] = 1
    return mask.byte().bool()


def get_node_ids(graph, source_files):
    file_ids = []
    for node_ids, node_data in graph.nodes(data=True):
        filename = node_data['source_file']
        if filename in source_files:
            file_ids.append(node_ids)
    return file_ids


def get_line_numbers(graph, source_files):
    line_numbers = []
    for node_ids, node_data in graph.nodes(data=True):
        line_number = node_data['node_source_code_lines']
        filename = node_data['source_file']
        if filename in source_files:
            line_numbers.append(line_number)
    return line_numbers


def get_edges(graph,source_files,file_ids):
    file_edges=[]
    if len(file_ids)>0:
        first_node=min(file_ids)
    else: first_node=0
    for node_u,node_v,label in graph.edges(data=True):
        if (node_u in file_ids) and (node_v in file_ids):
            node_u=node_u-first_node
            node_v=node_v-first_node
            file_edges.append([node_u,node_v])
    return file_edges


def get_color_node(graph,source_files):
    color_node=[]
    nodeTypes=['ENTRY_POINT', 'NEW VARIABLE', 'EXPRESSION', 'IF', 'END_IF',
    'FUNCTION_NAME', 'OTHER_ENTRYPOINT', 'THROW', '_', 'RETURN', 'INLINE ASM',
     'BEGIN_LOOP', 'END_LOOP', 'IF_LOOP', 'CONTINUE']
    for node_ids,node_data in graph.nodes(data=True):
        filename=node_data['source_file']
        type=node_data['node_type']
        if filename in source_files:
            if type==nodeTypes[0]:
               color_node.append('#CD5C5C')
            elif type==nodeTypes[1]:
               color_node.append('#FFB6C1')
            elif type==nodeTypes[2]:
                color_node.append('#FF8C00')
            elif type==nodeTypes[3]:
                color_node.append('#FFFF00')
            elif type==nodeTypes[4]:
                color_node.append('#DDA0DD')
            elif type==nodeTypes[5]:
                color_node.append('#DA70D6')
            elif type==nodeTypes[6]:
                color_node.append('#8B008B')
            elif type==nodeTypes[7]:
                color_node.append('#6A5ACD')
            elif type==nodeTypes[8]:
                color_node.append('#7FFF00')
            elif type==nodeTypes[9]:
                color_node.append('#00FF7F')
            elif type==nodeTypes[10]:
                color_node.append('#6B8E23')
            elif type==nodeTypes[11]:
                color_node.append('#008080')
            elif type==nodeTypes[12]:
                color_node.append('#ADD8E6')
            elif type==nodeTypes[13]:
                color_node.append('#5F9EA0')
            elif type==nodeTypes[14]:
                color_node.append('#150517')
            else: 
                color_node.append('#000000')       
    return color_node


def get_node_type(graph, source_files):
    file_node_type = []
    for node_ids, node_data in graph.nodes(data=True):
        filename = node_data['source_file']
        if filename in source_files:
            file_node_type.append(node_data['node_type'])
    return file_node_type
    
            
                

