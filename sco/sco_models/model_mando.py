
from cProfile import label
import json
import dgl
from sklearn.semi_supervised import SelfTrainingClassifier
import torch
import networkx as nx
import torch.nn as nn
import torch.nn.functional as F
from dgl.nn.pytorch import GATConv

from .graph_utils import add_hetero_ids, \
                         load_hetero_nx_graph, \
                         generate_hetero_graph_data, \
                         get_number_of_nodes, add_cfg_mapping, \
                         get_node_label, get_node_ids_dict, \
                         map_node_embedding, get_symmatrical_metapaths, \
                         get_length_2_metapath, \
                         reflect_graph, get_node_ids_by_filename, \
                         generate_random_node_features, generate_zeros_node_features, \
                         generate_filename_ids, get_node_tracker
class SemanticAttention(nn.Module):
    def __init__(self, in_size, hidden_size=128):
        super(SemanticAttention, self).__init__()

        self.project = nn.Sequential(
            nn.Linear(in_size, hidden_size),
            nn.Tanh(),
            nn.Linear(hidden_size, 1, bias=False)
        )

    def forward(self, z):
        w = self.project(z).mean(0)                    # (M, 1)
        beta = torch.softmax(w, dim=0)                 # (M, 1)
        beta = beta.expand((z.shape[0],) + beta.shape) # (N, M, 1)

        return (beta * z).sum(1)                       # (N, D * K)


class HANLayer(nn.Module):
    """
    We used custom HAN layer for self-attention layer per node type in our paper.

    Arguments
    ---------
    meta_paths : list of metapaths, each as a list of edge types
    in_size : input feature dimension
    out_size : output feature dimension
    layer_num_heads : number of attention heads
    dropout : Dropout probability

    Inputs
    ------
    g : DGLHeteroGraph
        The heterogeneous graph
    h : tensor
        Input features

    Outputs
    -------
    tensor
        The output feature
    """
    def __init__(self, meta_paths, in_size, out_size, layer_num_heads, dropout):
        super(HANLayer, self).__init__()

        # One GAT layer for each meta path based adjacency matrix
        self.gat_layers = nn.ModuleList()
        for i in range(len(meta_paths)):
            self.gat_layers.append(GATConv(in_size, out_size, layer_num_heads,
                                           dropout, dropout, activation=F.elu,
                                           allow_zero_in_degree=True))
        self.semantic_attention = SemanticAttention(in_size=out_size * layer_num_heads)
        self.meta_paths = list(tuple(meta_path) for meta_path in meta_paths)

        self._cached_graph = None
        self._cached_coalesced_graph = {}

    def forward(self, g, h):
        semantic_embeddings = []

        if self._cached_graph is None or self._cached_graph is not g:
            self._cached_graph = g
            self._cached_coalesced_graph.clear()
            for meta_path in self.meta_paths:
                self._cached_coalesced_graph[meta_path] = dgl.metapath_reachable_graph(
                        g, meta_path)

        for i, meta_path in enumerate(self.meta_paths):
            new_g = self._cached_coalesced_graph[meta_path]
            semantic_embeddings.append(self.gat_layers[i](new_g, h).flatten(1))
        semantic_embeddings = torch.stack(semantic_embeddings, dim=1)                  # (N, M, D * K)

        return self.semantic_attention(semantic_embeddings)                            # (N, D * K)


class MANDONodeClassifier(nn.Module):
    def __init__(self, compressed_global_graph_path, feature_extractor=None, node_feature='han', hidden_size=32, num_heads=8, dropout=0.6, device='cpu'):
        super(MANDONodeClassifier, self).__init__()
        self.compressed_global_graph_path = compressed_global_graph_path
        self.hidden_size = hidden_size
        self.num_heads = num_heads
        # self.source_path = source_path
        # self.extracted_graph = [f for f in os.listdir(self.source_path) if f.endswith('.sol')]
        self.device = device
        # Get Global graph
        nx_graph = load_hetero_nx_graph(compressed_global_graph_path)
        self.nx_graph = nx_graph
        nx_g_data = generate_hetero_graph_data(nx_graph)
        self.total_nodes = len(nx_graph)

        # Get Node Labels
        self.node_labels, self.labeled_node_ids, self.label_ids = get_node_label(nx_graph)
        self.node_ids_dict = get_node_ids_dict(nx_graph)

        # Reflect graph data
        self.symmetrical_global_graph_data = reflect_graph(nx_g_data)
        self.number_of_nodes = get_number_of_nodes(nx_graph)
        self.symmetrical_global_graph = dgl.heterograph(self.symmetrical_global_graph_data, num_nodes_dict=self.number_of_nodes)
        # self.meta_paths = get_symmatrical_metapaths(self.symmetrical_global_graph)
        self.meta_paths = get_length_2_metapath(self.symmetrical_global_graph)
        # self.meta_paths = load_meta_paths('./metapath_length_2.txt')
        # Concat the metapaths have the same begin nodetype
        self.full_metapath = {}
        for metapath in self.meta_paths:
            ntype = metapath[0][0]
            if ntype not in self.full_metapath:
                self.full_metapath[ntype] = [metapath]
            else:
                self.full_metapath[ntype].append(metapath)
        # print(len(set([meta_path[0][0] for meta_path in self.meta_paths])))
        # print(len(self.symmetrical_global_graph.ntypes))
        self.node_types = set([meta_path[0][0] for meta_path in self.meta_paths])
        # self.node_types = self.symmetrical_global_graph.ntypes
        self.ntypes_dict = {k: v for v, k in enumerate(self.node_types)}

        self.node_feature = node_feature
        features = {}
        if node_feature == 'nodetype':
            for ntype in self.node_types:
                features[ntype] = self._nodetype2onehot(ntype).repeat(self.symmetrical_global_graph.num_nodes(ntype), 1).to(self.device)
            self.in_size = len(self.node_types)

        self.symmetrical_global_graph = self.symmetrical_global_graph.to(self.device)
        self.symmetrical_global_graph.ndata['feat'] = features

        # Init Model
        self.layers = nn.ModuleList()
        self.layers.append(HANLayer([self.meta_paths[0]], self.in_size, hidden_size, num_heads, dropout))
        for meta_path in self.meta_paths[1:]:
            self.layers.append(HANLayer([meta_path], self.in_size, hidden_size, num_heads, dropout))
        
        self.layers_dict = nn.ModuleDict()
        for ntype, metapath in self.full_metapath.items():
            self.layers_dict.update({ntype: (HANLayer(metapath, self.in_size, hidden_size, num_heads, dropout))})
        
        # self.out_size = len(self.label_ids)
        self.out_size = 2
        self.last_hidden_size = hidden_size * num_heads
        self.classify = nn.Linear(self.last_hidden_size, self.out_size)


    def _nodetype2onehot(self, ntype):
        feature = torch.zeros(len(self.ntypes_dict), dtype=torch.float)
        feature[self.ntypes_dict[ntype]] = 1
        return feature

    def get_assemble_node_features(self):
        features = {}
        for han in self.layers:
            ntype = han.meta_paths[0][0][0]
            feature = han(self.symmetrical_global_graph, self.symmetrical_global_graph.ndata['feat'][ntype].to(self.device))
            if ntype not in features.keys():
                features[ntype] = feature.unsqueeze(0)
            else:
                features[ntype] = torch.cat((features[ntype], feature.unsqueeze(0)))
        # Use mean for aggregate node hidden features
        return {k: torch.mean(v, dim=0) for k, v in features.items()}

    def get_node_features(self):
        features = {}
        for ntype in self.node_types:
            features[ntype] = self.layers_dict[ntype](self.symmetrical_global_graph, self.symmetrical_global_graph.ndata['feat'][ntype].to(self.device))
        return features

    def reset_parameters(self):
        for model in self.layers:
            for layer in model.children():
                if hasattr(layer, 'reset_parameters'):
                    layer.reset_parameters()
        for layer in self.classify.children():
            if hasattr(layer, 'reset_parameters'):
                    layer.reset_parameters()

    def forward(self):
        features = self.get_assemble_node_features()
        hiddens = torch.zeros((self.symmetrical_global_graph.number_of_nodes(), self.last_hidden_size), device=self.device)
        for ntype, feature in features.items():
            assert len(self.node_ids_dict[ntype]) == feature.shape[0]
            hiddens[self.node_ids_dict[ntype]] = feature
        output = self.classify(hiddens)
        return output

    def extend_forward(self, new_graph):
        nx_graph = new_graph
        nx_graph = nx.convert_node_labels_to_integers(nx_graph)
        nx_graph = add_hetero_ids(nx_graph)
        nx_g_data = generate_hetero_graph_data(nx_graph)

        # Get Node Labels
        node_labels, labeled_node_ids, label_ids = get_node_label(nx_graph)
        node_ids_dict = get_node_ids_dict(nx_graph)

        # Reflect graph data
        symmetrical_global_graph_data = reflect_graph(nx_g_data)
        number_of_nodes = get_number_of_nodes(nx_graph)
        symmetrical_global_graph = dgl.heterograph(symmetrical_global_graph_data, num_nodes_dict=number_of_nodes, device=self.device)
        # Create input node features
        features = {}
        if self.node_feature == 'nodetype':
            for ntype in symmetrical_global_graph.ntypes:
                features[ntype] = self._nodetype2onehot(ntype).repeat(symmetrical_global_graph.num_nodes(ntype), 1).to(self.device)
            self.in_size = len(self.node_types)
        symmetrical_global_graph = symmetrical_global_graph.to(self.device)
        symmetrical_global_graph.ndata['feat'] = features
        # Assemble features
        _features = {}
        for han in self.layers:
            ntype = han.meta_paths[0][0][0]
            feature = han(symmetrical_global_graph, symmetrical_global_graph.ndata['feat'][ntype].to(self.device))
            if ntype not in _features.keys():
                _features[ntype] = feature.unsqueeze(0)
            else:
                _features[ntype] = torch.cat((_features[ntype], feature.unsqueeze(0)))
        # Use mean for aggregate node hidden features
        features =  {k: torch.mean(v, dim=0) for k, v in _features.items()}
        hiddens = torch.zeros((symmetrical_global_graph.number_of_nodes(), self.last_hidden_size), device=self.device)
        for ntype, feature in features.items():
            hiddens[node_ids_dict[ntype]] = feature
        output = self.classify(hiddens)
        return output, node_labels


class MANDOGraphClassifier(nn.Module):
    def __init__(self, compressed_global_graph_path, feature_extractor=None, node_feature='han', hidden_size=32, num_heads=8, dropout=0.6, device='cpu'):
        super(MANDOGraphClassifier, self).__init__()
        self.compressed_global_graph_path = compressed_global_graph_path
        self.hidden_size = hidden_size
        self.num_heads = num_heads
        # self.source_path = source_path
        # self.extracted_graph = [f for f in os.listdir(self.source_path) if f.endswith('.sol')]
        self.device = device
        # Get Global graph
        nx_graph = load_hetero_nx_graph(compressed_global_graph_path)
        self.nx_graph = nx_graph
        self.filename_mapping = generate_filename_ids(nx_graph)
        _node_tracker = get_node_tracker(nx_graph, self.filename_mapping)
        nx_g_data = generate_hetero_graph_data(nx_graph)
        self.total_nodes = len(nx_graph)

        # Get Node Labels
        self.node_labels, self.labeled_node_ids, self.label_ids = get_node_label(nx_graph)
        self.node_ids_dict = get_node_ids_dict(nx_graph)

        # Reflect graph data
        self.symmetrical_global_graph_data = reflect_graph(nx_g_data)
        self.number_of_nodes = get_number_of_nodes(nx_graph)
        self.symmetrical_global_graph = dgl.heterograph(self.symmetrical_global_graph_data, num_nodes_dict=self.number_of_nodes)
        self.symmetrical_global_graph.ndata['filename'] = _node_tracker
        # self.meta_paths = get_symmatrical_metapaths(self.symmetrical_global_graph)
        self.meta_paths = get_length_2_metapath(self.symmetrical_global_graph)
        # self.meta_paths = load_meta_paths('./metapath_length_2.txt')
        # Concat the metapaths have the same begin nodetype
        self.full_metapath = {}
        for metapath in self.meta_paths:
            ntype = metapath[0][0]
            if ntype not in self.full_metapath:
                self.full_metapath[ntype] = [metapath]
            else:
                self.full_metapath[ntype].append(metapath)
        self.node_types = set([meta_path[0][0] for meta_path in self.meta_paths])
        self.node_types = self.symmetrical_global_graph.ntypes
        self.edge_types = self.symmetrical_global_graph.etypes
        self.ntypes_dict = {k: v for v, k in enumerate(self.node_types)}

        self.node_feature = node_feature
        features = {}
        if node_feature == 'nodetype':
            for ntype in self.node_types:
                features[ntype] = self._nodetype2onehot(ntype).repeat(self.symmetrical_global_graph.num_nodes(ntype), 1).to(self.device)
            self.in_size = len(self.node_types)

        self.symmetrical_global_graph = self.symmetrical_global_graph.to(self.device)
        self.symmetrical_global_graph.ndata['feat'] = features

        # Init Model
        self.layers = nn.ModuleList()
        self.layers.append(HANLayer([self.meta_paths[0]], self.in_size, hidden_size, num_heads, dropout))
        for meta_path in self.meta_paths[1:]:
            self.layers.append(HANLayer([meta_path], self.in_size, hidden_size, num_heads, dropout))

        self.out_size = 2
        self.last_hidden_size = hidden_size * num_heads
        self.classify = nn.Linear(self.last_hidden_size, self.out_size)


    def _nodetype2onehot(self, ntype):
        feature = torch.zeros(len(self.ntypes_dict), dtype=torch.float)
        feature[self.ntypes_dict[ntype]] = 1
        return feature

    def get_assemble_node_features(self):
        features = {}
        for han in self.layers:
            ntype = han.meta_paths[0][0][0]
            feature = han(self.symmetrical_global_graph, self.symmetrical_global_graph.ndata['feat'][ntype].to(self.device))
            if ntype not in features.keys():
                features[ntype] = feature.unsqueeze(0)
            else:
                features[ntype] = torch.cat((features[ntype], feature.unsqueeze(0)))
        # Use mean for aggregate node hidden features
        return {k: torch.mean(v, dim=0) for k, v in features.items()}

    def get_node_features(self):
        features = {}
        for ntype in self.node_types:
            features[ntype] = self.layers_dict[ntype](self.symmetrical_global_graph, self.symmetrical_global_graph.ndata['feat'][ntype].to(self.device))
        return features

    def reset_parameters(self):
        for model in self.layers:
            for layer in model.children():
                if hasattr(layer, 'reset_parameters'):
                    layer.reset_parameters()
        for layer in self.classify.children():
            if hasattr(layer, 'reset_parameters'):
                    layer.reset_parameters()

    def forward(self, batched_g_name, save_featrues=None):
        features = self.get_assemble_node_features()
        batched_graph_embedded = []
        for g_name in batched_g_name:
            file_ids = self.filename_mapping[g_name]
            graph_embedded = 0
            for node_type in self.node_types:
                file_mask = self.symmetrical_global_graph.ndata['filename'][node_type] == file_ids
                if file_mask.sum().item() != 0:
                    graph_embedded += features[node_type][file_mask].mean(0)
            # if not isinstance(graph_embedded, int):
            batched_graph_embedded.append(graph_embedded.tolist())
        batched_graph_embedded = torch.tensor(batched_graph_embedded).to(self.device)
        if save_featrues:
            torch.save(batched_graph_embedded, save_featrues)
        output = self.classify(batched_graph_embedded)
        return output, batched_graph_embedded

    def extend_forward(self, new_graph, new_contracts):
        nx_graph = new_graph
        nx_graph = nx.convert_node_labels_to_integers(nx_graph)
        nx_graph = add_hetero_ids(nx_graph)
        nx_g_data = generate_hetero_graph_data(nx_graph)

        # Get Node Labels
        node_ids_dict = get_node_ids_dict(nx_graph)
        node_ids_by_filename = get_node_ids_by_filename(nx_graph)

        # Reflect graph data
        symmetrical_global_graph_data = reflect_graph(nx_g_data)
        number_of_nodes = get_number_of_nodes(nx_graph)
        symmetrical_global_graph = dgl.heterograph(symmetrical_global_graph_data, num_nodes_dict=number_of_nodes, device=self.device)
        # Create input node features
        features = {}
        if self.node_feature == 'nodetype':
            for ntype in symmetrical_global_graph.ntypes:
                features[ntype] = self._nodetype2onehot(ntype).repeat(symmetrical_global_graph.num_nodes(ntype), 1).to(self.device)
            self.in_size = len(self.node_types)
        symmetrical_global_graph = symmetrical_global_graph.to(self.device)
        symmetrical_global_graph.ndata['feat'] = features
        # Assemble features
        _features = {}
        for han in self.layers:
            ntype = han.meta_paths[0][0][0]
            feature = han(symmetrical_global_graph, symmetrical_global_graph.ndata['feat'][ntype].to(self.device))
            if ntype not in _features.keys():
                _features[ntype] = feature.unsqueeze(0)
            else:
                _features[ntype] = torch.cat((_features[ntype], feature.unsqueeze(0)))
        # Use mean for aggregate node hidden features
        features =  {k: torch.mean(v, dim=0) for k, v in _features.items()}
        hiddens = torch.zeros((symmetrical_global_graph.number_of_nodes(), self.last_hidden_size), device=self.device)
        for ntype, feature in features.items():
            assert len(node_ids_dict[ntype]) == feature.shape[0]
            hiddens[node_ids_dict[ntype]] = feature
        batched_graph_embedded = []
        for g_name in new_contracts:
            node_list = node_ids_by_filename[g_name]
            batched_graph_embedded.append(hiddens[node_list].mean(0).tolist())
        batched_graph_embedded = torch.tensor(batched_graph_embedded).to(self.device)
        output = self.classify(batched_graph_embedded)
        return output


def get_bug_node_type_list(nx_graph, node_ids, labels):
    node_types = []
    for i in node_ids:
        if labels[i] == 1:
            node_types.append(nx_graph.nodes[i]['node_type'])
    return list(set(node_types))


if __name__ == '__main__':
    import sys
    import os
    from os.path import join
    from shutil import copy
    from sklearn import metrics
    from .graph_utils import get_node_label
    from ..common.process_graphs.call_graph_generator import generate_cg
    from ..common.process_graphs.control_flow_graph_generator import generate_cfg
    from ..common.process_graphs.combination_call_graph_and_control_flow_graph_helper import combine_cfg_cg
    from ..common.utils import get_node_ids, get_binary_mask

    curated_vulnerabilities_json_files = ['/Users/minh/Documents/2022/smart_contract/mando/ge-sc/data/smartbug-dataset/vulnerabilities.json']
    data_type = 'buggy'
    device = 'cuda:0' if torch.cuda.is_available() else 'cpu'
    bug_info = {'access_control': 57, 'arithmetic': 60, 'denial_of_service': 46,
              'front_running': 44, 'reentrancy': 71, 'time_manipulation': 50, 
              'unchecked_low_level_calls': 95}
    # bug_info = {'access_control': 57,}
    # Generate graph for comming contract
    if len(sys.argv) == 2:
        bug_list = sys.argv[1].split(',')
    else:
        bug_list = list(bug_info.keys())
    total_reports = []
    for bug in bug_list:
        print(bug, ''.join(['-']*(50 - len(bug))))
        vulnerabilities_json_files = curated_vulnerabilities_json_files + [f'/Users/minh/Documents/2022/smart_contract/mando/ge-sc/data/solidifi_buggy_contracts/{bug}/vulnerabilities.json']
        dataset = f'/Users/minh/Documents/2022/smart_contract/mando/ge-sc/experiments/ge-sc-data/source_code/{bug}/{data_type}/'
        curated_files = [f for f in os.listdir(dataset) if f.endswith('.sol')]
        # curated_files = ['0x3f2ef511aa6e75231e4deafc7a3d2ecab3741de2.sol']
        graph_label = f'/Users/minh/Documents/2022/smart_contract/mando/ge-sc/experiments/ge-sc-data/source_code/{bug}/clean_{bug_info[bug]}_buggy_curated_0/graph_labels.json'
        with open(graph_label, 'r') as f:
            graph_labels = json.load(f)
        graph_label_dict = {label['contract_name']: label['targets'] for label in graph_labels}

        graph_ckpt = f'./sco/models/graph_detection/nodetype/{bug}_han.pth'
        graph_graph = f'./sco/graphs/graph_detection/{bug}_cfg_cg_compressed_graphs.gpickle'
        graph_model = MANDOGraphClassifier(graph_graph, node_feature='nodetype')
        graph_model.load_state_dict(torch.load(graph_ckpt))
        graph_model.eval()
        original_graph_graph = graph_model.nx_graph

        node_ckpt = f'./sco/models/node_detection/nodetype/{bug}_han.pth'
        node_graph = f'./sco/graphs/node_detection/{bug}_cfg_cg_compressed_graphs.gpickle'
        node_model = MANDONodeClassifier(node_graph, node_feature='nodetype')
        node_model.load_state_dict(torch.load(node_ckpt))
        node_model.eval()
        original_node_graph = node_model.nx_graph

        for sc in curated_files:
            print(join(dataset, sc), ''.join(['=']*(90 - len(sc))))
            # print(sc)
            sm_name = 'contract_test.sol'
            sm_path = join('./sco/_static', sm_name)
            copy(join(dataset, sc), sm_path)
            # sm_length = len(sm_content.split('\n'))
            cfg_graph = generate_cfg(sm_path, ori_name=sc, vulnerabilities_json_files=vulnerabilities_json_files)
            if cfg_graph is None:
                print({'messages': 'Found an illegal CFG solidity smart contract'})
                continue
            cg_graph = generate_cg(sm_path, ori_name=sc, vulnerabilities_json_files=vulnerabilities_json_files)
            if cg_graph is None:
                print({'messages': 'Found an illegal CG solidity smart contract'})
                continue
            cfg_cg_graph = combine_cfg_cg(cfg_graph, cg_graph)
            # print('length incoming graph: ', len(cfg_cg_graph))
            # print(cfg_cg_graph.nodes(data=True)[0])


            # with torch.no_grad():
            #     logits, _ = graph_model([sc])
            #     graph_preds = nn.functional.softmax(logits, dim=1)
            #     _, indices = torch.max(graph_preds, dim=1)
            #     graph_preds = indices.long().cpu().numpy()
            # print('Detecting as already in dataset: ', graph_preds[0])

            # Inference Graph level
            extra_graph = nx.disjoint_union(original_graph_graph, cfg_cg_graph)
            with torch.no_grad():
                try:
                    logits = graph_model.extend_forward(extra_graph, [sm_name])
                except Exception as e:
                    print(e)
                    print({'messages': 'Found non-existent nodes/edges in the graph!'})
                    continue
            


            graph_preds = nn.functional.softmax(logits, dim=1)
            _, indices = torch.max(graph_preds, dim=1)
            graph_preds = indices.long().cpu().numpy()
            # if graph_preds[0] == 0:
            #     continue 
            print('Detecting as new contract:       ', graph_preds[0])

            # Inference Node level
            extra_graph = nx.disjoint_union(original_node_graph, cfg_cg_graph)
            file_ids = get_node_ids(extra_graph, [sm_name])
            node_mask = get_binary_mask(len(extra_graph), file_ids)
            node_labels, labeled_node_ids, _ = get_node_label(extra_graph)
            targets = torch.tensor(node_labels, device=device).cpu().numpy()
            with torch.no_grad():
                try:
                    logits, _ = node_model.extend_forward(extra_graph)
                    assert len(targets) == len(logits)
                except Exception as e:
                    print(e)
                    print({'messages': 'Found non-existent nodes/edges in the graph!'})
            node_preds = nn.functional.softmax(logits, dim=1)
            _, indices = torch.max(node_preds, dim=1)
            node_preds = indices.long().cpu().numpy()
            prec_score = metrics.precision_score(targets[node_mask], node_preds[node_mask])
            bug_node_type_list = get_bug_node_type_list(extra_graph, file_ids, node_preds)
            if len(set(bug_node_type_list).difference(set(['CONTRACT_FUNCTION', 'ENTRY_POINT']))) == 0:
                continue
            print('Precision score: ', prec_score)
            recall_score = metrics.recall_score(targets[node_mask], node_preds[node_mask])
            print('Recall score:    ', recall_score)
            buggy_f1_score = metrics.f1_score(targets[node_mask], node_preds[node_mask], average=None)
            buggy_f1_score = 0 if len(buggy_f1_score) == 1 else buggy_f1_score[1]
            print('Buggy F1 score:  ', buggy_f1_score)
            macro_f1_score = metrics.f1_score(targets[node_mask], node_preds[node_mask], average='macro')
            print('Macro F1 score:  ', macro_f1_score)
            print(targets[node_mask])
            print(get_bug_node_type_list(extra_graph, file_ids, targets))
            print(node_preds[node_mask])
            print(get_bug_node_type_list(extra_graph, file_ids, node_preds))

