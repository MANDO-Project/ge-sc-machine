from collections import defaultdict

import networkx as nx
from slither.slither import Slither
from logbook import Logger

from slither.printers.abstract_printer import AbstractPrinter
from slither.core.declarations.solidity_variables import SolidityFunction
from slither.core.declarations.function import Function
from slither.core.variables.variable import Variable

from .slither_reader import get_solc_compiler


logger = Logger(__name__)


# return graph edge with edge type
def _edge(from_node, to_node, edge_type, label):
    return (from_node, to_node, edge_type, label)


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


def revert_vulnerabilities_in_sc_from_tuple(tuple_vulnerabilities_in_sc):
    vulnerabilities_in_sc = list(tuple_vulnerabilities_in_sc)
    vul_info = []
    if len(vulnerabilities_in_sc) > 0:
        for vul in vulnerabilities_in_sc:
            dct = dict((x, y) for x, y in vul)
            for key, val in dct.items():
                if key == 'lines':
                    dct[key] = list(val)
            vul_info.append(dct)
    return vul_info


def _render_external_calls(nx_graph, external_calls):
    if len(external_calls) > 0:
        for external_call in external_calls:
            _add_edge_info_to_nxgraph(external_call, nx_graph)


def _process_external_call(
    contract,
    function,
    external_call,
    contract_functions,
    external_calls,
    all_contracts,
    filename_input,
    vulnerabilities_in_sc=[]
):
    tuple_vulnerabilities_in_sc = parse_vulnerabilities_in_sc_to_tuple(vulnerabilities_in_sc)
    external_contract, external_function = external_call

    if not external_contract in all_contracts:
        return

    # add variable as node to respective contract
    if isinstance(external_function, (Variable)):
        contract_functions[external_contract].add(tuple(
                _function_node(external_contract, external_function, filename_input, tuple_vulnerabilities_in_sc).items()))


    external_calls.add(
        _edge(
            tuple(_function_node(contract, function, filename_input, tuple_vulnerabilities_in_sc).items()),
            tuple(_function_node(external_contract, external_function, filename_input, tuple_vulnerabilities_in_sc).items()),
            edge_type='external_call',
            label='external_call'
        )
    )


def _process_internal_call(
    contract,
    function,
    internal_call,
    contract_calls,
    solidity_functions,
    solidity_calls,
    filename_input,
    vulnerabilities_in_sc=[]
):
    tuple_vulnerabilities_in_sc = parse_vulnerabilities_in_sc_to_tuple(vulnerabilities_in_sc)
    if isinstance(internal_call, (Function)):
        # print('tuple:', tuple(_function_node(contract, function, filename_input).items()))
        contract_calls[contract].add(
            _edge(
                tuple(_function_node(contract, function, filename_input, tuple_vulnerabilities_in_sc).items()),
                tuple(_function_node(contract, internal_call, filename_input, tuple_vulnerabilities_in_sc).items()),
                edge_type='internal_call',
                label='internal_call'
            )
        )

    elif isinstance(internal_call, (SolidityFunction)):
        solidity_functions.add(tuple(_solidity_function_node(internal_call).items()))
        solidity_calls.add(
            _edge(
                tuple(_function_node(contract, function, filename_input, tuple_vulnerabilities_in_sc).items()),
                tuple(_solidity_function_node(internal_call).items()),
                edge_type='solidity_call',
                label='solidity_call'
            )
        )


# return edge info from a contract call tuple
def _add_edge_info_to_nxgraph(contract_call, nx_graph):
    source = contract_call[0]
    source_node_id, source_label, source_type, source_function_fullname, source_contract_name, \
    source_source_file, source_node_function_info_vulnerabilities, source_node_function_source_code_lines = _get_node_info(source)

    if source_node_id not in nx_graph.nodes():
        nx_graph.add_node(source_node_id, label=source_label, node_type=source_type,
                          node_info_vulnerabilities=source_node_function_info_vulnerabilities,
                          node_source_code_lines=source_node_function_source_code_lines,
                          function_fullname=source_function_fullname, contract_name=source_contract_name,
                          source_file=source_source_file)

    target = contract_call[1]
    target_node_id, target_label, target_type, target_function_fullname, target_contract_name, \
    target_source_file, target_node_function_info_vulnerabilities, target_node_function_source_code_lines = _get_node_info(target)

    if target_node_id not in nx_graph.nodes():
        nx_graph.add_node(target_node_id, label=target_label, node_type=target_type,
                          node_info_vulnerabilities=target_node_function_info_vulnerabilities,
                          node_source_code_lines=target_node_function_source_code_lines,
                          function_fullname=target_function_fullname, contract_name=target_contract_name,
                          source_file=target_source_file)

    edge_type = contract_call[2]
    edge_label = contract_call[3]
    nx_graph.add_edge(source_node_id, target_node_id, label=edge_label, edge_type=edge_type)


# return unique id for contract function to use as node name
def _function_node(contract, function, filename_input, tuple_vulnerabilities_in_sc):
    node_function_source_code_lines = function.source_mapping['lines']
    vulnerabilities_in_sc = revert_vulnerabilities_in_sc_from_tuple(tuple_vulnerabilities_in_sc)
    node_function_info_vulnerabilities = get_vulnerabilities_of_node_by_source_code_line(node_function_source_code_lines, vulnerabilities_in_sc)

    node_info = {
        'node_id': f"{filename_input}_{contract.id}_{contract.name}_{function.full_name}",
        'label': f"{filename_input}_{contract.name}_{function.full_name}",
        'function_fullname': function.full_name, 
        'contract_name': contract.name, 
        'source_file': filename_input,
        'node_function_info_vulnerabilities': parse_vulnerabilities_in_sc_to_tuple(node_function_info_vulnerabilities),
        'node_source_code_lines': tuple(node_function_source_code_lines)
    }
    return node_info


# return unique id for solidity function to use as node name
def _solidity_function_node(solidity_function):
    # node_function_source_code_lines = solidity_function.source_mapping['lines']
    node_info = {
        'node_id': f"[Solidity]_{solidity_function.full_name}",
        'label': f"[Solidity]_{solidity_function.full_name}",
        'function_fullname': solidity_function.full_name,
        'contract_name': None,
        'source_file': None,
        'node_function_info_vulnerabilities': None,
        'node_source_code_lines': None
    }
    return node_info


def _get_node_info(tuple_node):
    if tuple_node[0][0] == 'node_id':
        node_id = tuple_node[0][1]
    if tuple_node[1][0] == 'label':
        node_label = tuple_node[1][1]
    if tuple_node[2][0] == 'function_fullname':
        function_fullname = tuple_node[2][1]
    if tuple_node[3][0] == 'contract_name':
        contract_name = tuple_node[3][1]
    if tuple_node[4][0] == 'source_file':
        source_file = tuple_node[4][1]
    if tuple_node[5][0] == 'node_function_info_vulnerabilities':
        node_function_info_vulnerabilities = revert_vulnerabilities_in_sc_from_tuple(tuple_node[5][1])
    if tuple_node[6][0] == 'node_source_code_lines':
        node_function_source_code_lines = list(tuple_node[6][1])
    
    if len(node_function_info_vulnerabilities) == 0:
        node_function_info_vulnerabilities = None

    if 'fallback' in node_id:
        node_type = 'fallback_function'
    elif '[Solidity]' in node_id:
        node_type = 'fallback_function'
    else:
        node_type = 'contract_function'
    
    return node_id, node_label, node_type, function_fullname, contract_name, source_file, node_function_info_vulnerabilities, node_function_source_code_lines


def _render_internal_calls(nx_graph, contract, contract_functions, contract_calls):
    if len(contract_functions[contract]) > 0:
        for contract_function in contract_functions[contract]:     
            node_id, node_label, node_type, function_fullname, contract_name, source_file, \
            node_function_info_vulnerabilities, node_function_source_code_lines = _get_node_info(contract_function)

            nx_graph.add_node(node_id, label=node_label, node_type=node_type,
                              node_info_vulnerabilities=node_function_info_vulnerabilities,
                              node_source_code_lines=node_function_source_code_lines,
                              function_fullname=function_fullname, contract_name=contract_name,
                              source_file=source_file)
    
    if len(contract_calls[contract]) > 0:
        for contract_call in contract_calls[contract]:
            _add_edge_info_to_nxgraph(contract_call, nx_graph)





def _process_functions(functions, filename_input, vulnerabilities_in_sc=None):
    contract_functions = defaultdict(set)  # contract -> contract functions nodes
    contract_calls = defaultdict(set)  # contract -> contract calls edges
    solidity_functions = set()  # solidity function nodes
    solidity_calls = set()  # solidity calls edges
    external_calls = set()  # external calls edges
    all_contracts = set()

    for function in functions:
        all_contracts.add(function.contract_declarer)

    for function in functions:
        _process_function(
            function.contract_declarer,
            function,
            contract_functions,
            contract_calls,
            solidity_functions,
            solidity_calls,
            external_calls,
            all_contracts,
            filename_input,
            vulnerabilities_in_sc
        )
    all_contracts_graph = nx.MultiDiGraph()
    for contract in all_contracts:
        _render_internal_calls(all_contracts_graph, contract,
                               contract_functions, contract_calls)

    _render_external_calls(all_contracts_graph, external_calls)

    return all_contracts_graph


def _process_function(
    contract,
    function,
    contract_functions,
    contract_calls,
    solidity_functions,
    solidity_calls,
    external_calls,
    all_contracts,
    filename_input,
    vulnerabilities_in_sc=[]
):  
    tuple_vulnerabilities_in_sc = parse_vulnerabilities_in_sc_to_tuple(vulnerabilities_in_sc)
    contract_functions[contract].add(tuple(
        _function_node(contract, function, filename_input, tuple_vulnerabilities_in_sc).items())
    )

    for internal_call in function.internal_calls:
        _process_internal_call(
            contract,
            function,
            internal_call,
            contract_calls,
            solidity_functions,
            solidity_calls,
            filename_input,
            vulnerabilities_in_sc
        )

    for external_call in function.high_level_calls:
        _process_external_call(
            contract,
            function,
            external_call,
            contract_functions,
            external_calls,
            all_contracts,
            filename_input,
            vulnerabilities_in_sc
        )


def parse_vulnerabilities_in_sc_to_tuple(vulnerabilities_in_sc):
    vul_info = list()

    if vulnerabilities_in_sc is not None:
        for vul in vulnerabilities_in_sc:
            for key, value in vul.items():
                if key == 'lines':
                    vul[key] = tuple(value)
        
        for vul in vulnerabilities_in_sc:
            vul_info.append(tuple(vul.items()))

    vul_info = tuple(vul_info)
    return vul_info


def get_vulnerabilities(file_name_sc, vulnerabilities):
    list_vulnerability_in_sc = None
    if vulnerabilities is not None:
        for vul_item in vulnerabilities:
            if file_name_sc == vul_item['name']:
                list_vulnerability_in_sc = vul_item['vulnerabilities']
            
    return list_vulnerability_in_sc



class GESCPrinters(AbstractPrinter):
    ARGUMENT = 'call-graph'
    HELP = 'Export the call-graph of the contracts to a dot file and a gpickle file'
    WIKI = 'https://github.com/trailofbits/slither/wiki/Printer-documentation#call-graph'

    def __init__(self, slither, filename, logger, vulnerabilities_in_sc=None):
        super().__init__(slither, logger)
        self.filename = filename
        self.vulnerabilities_in_sc = vulnerabilities_in_sc

    def generate_all_contracts_call_graph(self):
        # Avoid dupplicate funcitons due to different compilation unit
        all_functionss = [compilation_unit.functions for compilation_unit in self.slither.compilation_units]
        all_functions = [item for sublist in all_functionss for item in sublist]
        all_functions_as_dict = {function.canonical_name: function for function in all_functions}
        all_contracts_call_graph = _process_functions(all_functions_as_dict.values(), self.filename, self.vulnerabilities_in_sc)
        return all_contracts_call_graph

    def output(self, filename):
        """
        Output the graph in filename
        Args:
            filename(string)
        """


def generate_cg(smart_contract):
    file_name_sc = smart_contract.split('/')[-1:][0]
    solc_compiler = get_solc_compiler(smart_contract)
    try:
        slither = Slither(smart_contract, solc=solc_compiler)
    except Exception as e:
        logger.debug(e)
        return None
    call_graph_printer = GESCPrinters(slither, file_name_sc, logger)
    call_graph = call_graph_printer.generate_all_contracts_call_graph()  
    return call_graph
