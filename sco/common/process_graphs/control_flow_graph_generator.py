import re
from copy import deepcopy

import networkx as nx
from slither.slither import Slither
from slither.core.cfg.node import NodeType
from logbook import Logger

from .slither_reader import get_solc_compiler


logger = Logger(__name__)


def get_node_info(node, list_vulnerabilities_info_in_sc):
    node_label = "Node Type: {}\n".format(str(node.type))
    node_type = str(node.type)
    if node.expression:
        node_label += "\nEXPRESSION:\n{}\n".format(node.expression)
        node_expression = str(node.expression)
    else:
        node_expression = None
    if node.irs:
        node_label += "\nIRs:\n" + "\n".join([str(ir) for ir in node.irs])
        node_irs = "\n".join([str(ir) for ir in node.irs])
    else:
        node_irs = None

    node_source_code_lines = node.source_mapping['lines']
    node_info_vulnerabilities = get_vulnerabilities_of_node_by_source_code_line(node_source_code_lines, list_vulnerabilities_info_in_sc)
    
    return node_label, node_type, node_expression, node_irs, node_info_vulnerabilities, node_source_code_lines


def get_vulnerabilities(file_name_sc, vulnerabilities):
    list_vulnerability_in_sc = None
    if vulnerabilities is not None:
        for vul_item in vulnerabilities:
            if file_name_sc == vul_item['name']:
                list_vulnerability_in_sc = vul_item['vulnerabilities']
            
    return list_vulnerability_in_sc


def get_vulnerabilities_of_node_by_source_code_line(source_code_lines, list_vul_info_sc):
    if list_vul_info_sc is not None:
        list_vulnerability = []
        for vul_info_sc in list_vul_info_sc:
            vulnerabilities_lines = vul_info_sc['lines']
            interset_lines = set(vulnerabilities_lines).intersection(set(source_code_lines))
            if len(interset_lines) > 0:
                list_vulnerability.append(vul_info_sc)
    else:
        list_vulnerability = None
    
    if list_vulnerability is None or len(list_vulnerability) == 0:
        node_info_vulnerabilities = None
    else:
        node_info_vulnerabilities = list_vulnerability
    return node_info_vulnerabilities


def generate_cfg(smart_contract):
    file_name_sc = smart_contract.split('/')[-1]
    solc_compiler = get_solc_compiler(smart_contract)
    try:
        slither = Slither(smart_contract, solc=solc_compiler)
    except Exception as e:
        logger.debug(e)
        return None
    list_vul_info_sc = None
    merge_contract_graph = None
    for contract in slither.contracts:
        merged_graph = None
        for idx, function in enumerate(contract.functions + contract.modifiers):  
            nx_g = nx.MultiDiGraph()
            for _, node in enumerate(function.nodes):             
                node_label, node_type, node_expression, node_irs, node_info_vulnerabilities, node_source_code_lines = get_node_info(node, list_vul_info_sc)
                nx_g.add_node(node.node_id, label=node_label,
                                node_type=node_type, node_expression=node_expression, node_irs=node_irs,
                                node_info_vulnerabilities=node_info_vulnerabilities,
                                node_source_code_lines=node_source_code_lines,
                                function_fullname=function.full_name, contract_name=contract.name, source_file=file_name_sc)
                
                if node.type in [NodeType.IF, NodeType.IFLOOP]:
                    true_node = node.son_true
                    if true_node:
                        if true_node.node_id not in nx_g.nodes():
                            node_label, node_type, node_expression, node_irs, node_info_vulnerabilities, node_source_code_lines = get_node_info(true_node, list_vul_info_sc)
                            nx_g.add_node(true_node.node_id, label=node_label,
                                            node_type=node_type, node_expression=node_expression, node_irs=node_irs,
                                            node_info_vulnerabilities=node_info_vulnerabilities,
                                            node_source_code_lines=node_source_code_lines,
                                            function_fullname=function.full_name, contract_name=contract.name, source_file=file_name_sc)
                        nx_g.add_edge(node.node_id, true_node.node_id, edge_type='if_true', label='True')

                    false_node = node.son_false
                    if false_node:
                        if false_node.node_id not in nx_g.nodes():
                            node_label, node_type, node_expression, node_irs, node_info_vulnerabilities, node_source_code_lines = get_node_info(false_node, list_vul_info_sc)
                            nx_g.add_node(false_node.node_id, label=node_label,
                                            node_type=node_type, node_expression=node_expression, node_irs=node_irs,
                                            node_info_vulnerabilities=node_info_vulnerabilities,
                                            node_source_code_lines=node_source_code_lines,
                                            function_fullname=function.full_name, contract_name=contract.name, source_file=file_name_sc)
                        nx_g.add_edge(node.node_id, false_node.node_id, edge_type='if_false', label='False')

                else:
                    for son_node in node.sons:
                        if son_node:
                            if son_node.node_id not in nx_g.nodes():
                                node_label, node_type, node_expression, node_irs, node_info_vulnerabilities, node_source_code_lines = get_node_info(son_node, list_vul_info_sc)
                                nx_g.add_node(son_node.node_id, label=node_label,
                                                node_type=node_type, node_expression=node_expression, node_irs=node_irs,
                                                node_info_vulnerabilities=node_info_vulnerabilities,
                                                node_source_code_lines=node_source_code_lines,
                                                function_fullname=function.full_name, contract_name=contract.name, source_file=file_name_sc)
                            nx_g.add_edge(node.node_id, son_node.node_id, edge_type='next', label='Next')

            nx_graph = nx_g
            # add FUNCTION_NAME node
            node_function_name = file_name_sc + '_' + contract.name + '_' + function.full_name
            node_function_source_code_lines = function.source_mapping['lines']
            node_function_info_vulnerabilities = get_vulnerabilities_of_node_by_source_code_line(node_function_source_code_lines, list_vul_info_sc)
            nx_graph.add_node(node_function_name, label=node_function_name,
                                node_type='FUNCTION_NAME', node_expression=None, node_irs=None,
                                node_info_vulnerabilities=node_function_info_vulnerabilities,
                                node_source_code_lines=node_function_source_code_lines,
                                function_fullname=function.full_name, contract_name=contract.name, source_file=file_name_sc)

            if 0 in nx_graph.nodes():
                nx_graph.add_edge(node_function_name, 0, edge_type='next', label='Next')

            nx_graph = nx.relabel_nodes(nx_graph, lambda x: contract.name + '_' + function.full_name + '_' + str(x), copy=False)

            if merged_graph is None:
                merged_graph = deepcopy(nx_graph)
            else:
                merged_graph = nx.disjoint_union(merged_graph, nx_graph)

        if merge_contract_graph is None:
            merge_contract_graph = deepcopy(merged_graph)
        elif merged_graph is not None:
            merge_contract_graph = nx.disjoint_union(merge_contract_graph, merged_graph)
    return merge_contract_graph
