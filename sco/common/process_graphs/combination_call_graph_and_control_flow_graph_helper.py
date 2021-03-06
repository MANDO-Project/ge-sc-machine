
def mapping_cfg_and_cg_node_labels(cfg, call_graph):
    dict_node_label_cfg_and_cg = {}
    for node, node_data in cfg.nodes(data=True):
        if node_data['node_type'] == 'FUNCTION_NAME':
            if node_data['label'] not in dict_node_label_cfg_and_cg:
                dict_node_label_cfg_and_cg[node_data['label']] = None
            # else:
            #     print(node_data['label'], 'is existing.')

            dict_node_label_cfg_and_cg[node_data['label']] = {
                'cfg_node_id': node,
                'cfg_node_type': node_data['node_type']
            }
    for node, node_data in call_graph.nodes(data=True):
        if node_data['label'] in dict_node_label_cfg_and_cg:
            dict_node_label_cfg_and_cg[node_data['label']]['call_graph_node_id'] = node
            dict_node_label_cfg_and_cg[node_data['label']]['call_graph_node_type'] = node_data['node_type'].upper()

    # remove node labels are not existing in the call graph
    temp_dict = dict(dict_node_label_cfg_and_cg)
    for key, value in temp_dict.items():
        if 'call_graph_node_id' not in value or 'call_graph_node_type' not in value:
            dict_node_label_cfg_and_cg.pop(key, None)

    return dict_node_label_cfg_and_cg


def add_new_cfg_edges_from_call_graph(cfg, dict_node_label, call_graph):
    list_new_edges_cfg = []
    for source, target, edge_data in call_graph.edges(data=True):
        source_cfg = None
        target_cfg = None
        edge_data_cfg = edge_data
        for value in dict_node_label.values():
            if value['call_graph_node_id'] == source:
                source_cfg = value['cfg_node_id']
            
            if value['call_graph_node_id'] == target:
                target_cfg = value['cfg_node_id']
        
        if source_cfg is not None and target_cfg is not None:
            list_new_edges_cfg.append((source_cfg, target_cfg, edge_data_cfg))
    cfg.add_edges_from(list_new_edges_cfg)
    return cfg


def update_cfg_node_types_by_call_graph_node_types(cfg, dict_node_label):
    for value in dict_node_label.values():
        cfg_node_id = value['cfg_node_id']
        cfg.nodes[cfg_node_id]['node_type'] = value['call_graph_node_type']


def combine_cfg_cg(cfg_graph, cg_graph):
    dict_node_label_cfg_and_cg = mapping_cfg_and_cg_node_labels(cfg_graph, cg_graph)
    merged_graph = add_new_cfg_edges_from_call_graph(cfg_graph, dict_node_label_cfg_and_cg, cg_graph)
    update_cfg_node_types_by_call_graph_node_types(merged_graph, dict_node_label_cfg_and_cg)
    return merged_graph
