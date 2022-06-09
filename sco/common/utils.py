import sys
import os

import torch
import numpy as np
from logbook import Logger

sys.path.append('/Users/minh/Documents/2022/smart_contract/mando/ge-sc/')
from sco_models.model_node_classification import MANDONodeClassifier

logger = Logger(__name__)


def check_gpu():
    return torch.cuda.is_available()


def init_line_node_classificator(ckpt, compressed_graph, dataset, feature_extractor, device):
    model = MANDONodeClassifier(compressed_graph, dataset, feature_extractor, node_feature='nodetype', device=device)
    model.load_state_dict(torch.load(ckpt, map_location=torch.device(device)))
    model.to(device)
    smart_contracts = [f for f in os.listdir(dataset) if f.endswith('.sol')]
    return model, smart_contracts



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
