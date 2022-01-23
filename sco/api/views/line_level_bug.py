from logbook import Logger
from fastapi import APIRouter, Security

import torch
from torch._C import device

from ...auth import get_api_key
from ...config import settings
from ...common.utils import check_gpu
from ...common.utils import init_line_node_classificator
from ...common.utils import get_node_ids, get_binary_mask, get_line_numbers
from ...schemas.api import NodeRequest, NodeResponse 


logger = Logger(__name__)
router = APIRouter()

is_gpu = check_gpu()

node_classifier, smart_contracts = init_line_node_classificator(settings.LINE.CHECKPOINT,
                                          settings.LINE.COMPRESSED_GRAPH,
                                          settings.LINE.DATASET,
                                          settings.LINE.feature_extractor,
                                          settings.DEVICE)

@router.post('/check_device', dependencies=[Security(get_api_key)])
async def check_device():
    if is_gpu:
        device = torch.cuda.current_device()
        device_name = torch.cuda.get_device_name(0)
    else:
        device_name = 'CPU'
    return {'device': device_name}


@router.post('/line', response_model=NodeResponse, dependencies=[Security(get_api_key)])
async def detect_line_level_bugs(item: NodeRequest):
    node_classifier.eval()
    file_ids = get_node_ids(node_classifier.nx_graph, [item.filename])
    line_numbers = get_line_numbers(node_classifier.nx_graph, [item.filename])
    with torch.no_grad():
        logits = node_classifier()
        logits = logits.to(settings.DEVICE)
        file_mask = get_binary_mask(node_classifier.total_nodes, file_ids)
        preds = logits[file_mask]
        _, indices = torch.max(preds, dim=1)
        preds = indices.long().cpu().tolist()
        assert len(preds) == len(line_numbers)
        results = [{'node_id': i, 'code_lines': line_numbers[i], 'vulnerability': preds[i]} for i in range(len(line_numbers))]
    return {'message': 'Loaded model successfully',
            'results': results}
