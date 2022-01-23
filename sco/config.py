import os
from os.path import join
from typing import Union
from logbook import base

from .common.utils import check_gpu

from pydantic import BaseSettings
from pydantic.main import BaseModel


BASE_PATH = os.path.dirname(__file__)


class LINE_NODE_CLASSIFIER_CONFIG(BaseSettings):
    CHECKPOINT = join(BASE_PATH, '../models/node_classification/cfg/line/reentrancy/han.pth')
    COMPRESSED_GRAPH = join(BASE_PATH, '../models/node_classification/cfg/line/reentrancy/buggy_curated/compressed_graphs.gpickle')
    DATASET = join(BASE_PATH, '../models/node_classification/cfg/line/reentrancy/buggy_curated')
    feature_extractor = join(BASE_PATH, '../models/node_classification/cfg/line/reentrancy/matrix_line_dim128_of_core_graph_of_reentrancy_compressed_graphs.pkl')


class Settings(BaseSettings):
    SERVER_NAME = 'sco'
    VERSION: str = 'v1.0.0'
    DEVICE: str = 'GPU' if check_gpu() else 'CPU'
    SERVER_TAG: str = f'{SERVER_NAME}-{VERSION}-{DEVICE}'
    SERVICE: str = 'vulnerability'
    TASK: str = 'detection'
    PREFIX: str = f'/{VERSION}/{SERVICE}/{TASK}'
    LINE = LINE_NODE_CLASSIFIER_CONFIG()
    API_KEY = 'MqQVfJ6Fq1umZnUI7ZuaycciCjxi3gM0'
    DEVICE: str = 'cuda:0' if check_gpu() else 'cpu'
    class Config:
        env_file = '.env'

settings = Settings()
