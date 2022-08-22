import torch
from logbook import Logger

# from ..sco_models.model_hgt import HGTVulNodeClassifier
from ..sco_models.model_mando import MANDONodeClassifier as NodeClassifier
from ..sco_models.model_mando import MANDOGraphClassifier as GraphClassifier

logger = Logger(__name__)
torch.manual_seed(1)


def check_gpu():
    return torch.cuda.is_available()


def init_node_classificator(ckpt, compressed_graph, device):
    model = NodeClassifier(compressed_graph, node_feature='nodetype', device=device)
    model.load_state_dict(torch.load(ckpt))
    model.to(device)
    return model


def init_graph_classificator(ckpt, compressed_graph, device):
    model = GraphClassifier(compressed_graph, node_feature='nodetype', device=device)
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


def get_bug_lines(preds, lines):
    bug_lines = []
    for i in range(len(preds)):
        if preds[i]:
            bug_lines += lines[i]
    return list(set(bug_lines))


def get_color_node(graph,source_files):
    color_node=[]
    nodeTypes=['ENTRY_POINT', 'NEW VARIABLE', 'EXPRESSION', 'IF', 'END_IF',
    'FUNCTION_NAME', 'OTHER_ENTRYPOINT', 'THROW', '_', 'RETURN', 'INLINE ASM',
     'BEGIN_LOOP', 'END_LOOP', 'IF_LOOP', 'CONTINUE','CONTRACT_FUNCTION','FALLBACK_FUNCTION']
    for node_ids,node_data in graph.nodes(data=True):
        filename=node_data['source_file']
        type=node_data['node_type']
        if filename in source_files:
            if type==nodeTypes[0]:
               color_node.append('#0E38E3')
            elif type==nodeTypes[1]:
               color_node.append('#1c71c7')
            elif type==nodeTypes[2]:
                color_node.append('#2AAAAA')
            elif type==nodeTypes[3]:
                color_node.append('#38E38E')
            elif type==nodeTypes[4]:
                color_node.append('#471C71')
            elif type==nodeTypes[5]:
                color_node.append('#555555')
            elif type==nodeTypes[6]:
                color_node.append('#638E38')
            elif type==nodeTypes[7]:
                color_node.append('#71C71C')
            elif type==nodeTypes[8]:
                color_node.append('#7FFFFF')
            elif type==nodeTypes[9]:
                color_node.append('#8E38E3')
            elif type==nodeTypes[10]:
                color_node.append('#9C71C6')
            elif type==nodeTypes[11]:
                color_node.append('#AAAAAA')
            elif type==nodeTypes[12]:
                color_node.append('#B8E38D')
            elif type==nodeTypes[13]:
                color_node.append('#C71C71')
            elif type==nodeTypes[14]:
                color_node.append('#D5554D')
            elif type==nodeTypes[15]:
                color_node.append('#E38E30')
            elif type==nodeTypes[16]:
                color_node.append('#F1C713')
            
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
    
            
                

