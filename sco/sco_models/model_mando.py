
import dgl
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
                         generate_random_node_features, generate_zeros_node_features


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
        self.node_types = set([meta_path[0][0] for meta_path in self.meta_paths])
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
        self.node_types = set([meta_path[0][0] for meta_path in self.meta_paths])
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

    def forward(self):
        features = self.get_assemble_node_features()
        hiddens = torch.zeros((self.symmetrical_global_graph.number_of_nodes(), self.last_hidden_size), device=self.device)
        for ntype, feature in features.items():
            assert len(self.node_ids_dict[ntype]) == feature.shape[0]
            hiddens[self.node_ids_dict[ntype]] = feature
        output = self.classify(hiddens)
        return output

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


if __name__ == '__main__':
    ckpt = './models/graph_detection/nodetype/unchecked_low_level_calls_han.pth'
    graph = './graphs/graph_detection/unchecked_low_level_calls_cfg_cg_compressed_graphs.gpickle'
    model = MANDOGraphClassifier(graph, node_feature='nodetype')
    model.load_state_dict(torch.load(ckpt))
    model.eval()
