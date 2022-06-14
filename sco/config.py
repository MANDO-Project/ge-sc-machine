import os
from os.path import join
from enum import Enum

from pydantic import BaseSettings

from .common.utils import check_gpu


BASE_PATH = os.path.dirname(__file__)


class NODE_CLASSIFIER_CONFIG_ACCESS_CONTROL(str, Enum):
    CHECKPOINT = join(BASE_PATH, './models/node_detection/nodetype/access_control_hgt.pth')
    COMPRESSED_GRAPH = join(BASE_PATH, './graphs/node_detection/access_control_cfg_cg_compressed_graphs.gpickle')


class NODE_CLASSIFIER_CONFIG_ARITHMETIC(str, Enum):
    CHECKPOINT = join(BASE_PATH, './models/node_detection/nodetype/arithmetic_hgt.pth')
    COMPRESSED_GRAPH = join(BASE_PATH, './graphs/node_detection/arithmetic_cfg_cg_compressed_graphs.gpickle')

class NODE_CLASSIFIER_CONFIG_DENIAL_OF_SERVICE(str, Enum):
    CHECKPOINT = join(BASE_PATH, './models/node_detection/nodetype/denial_of_service_hgt.pth')
    COMPRESSED_GRAPH = join(BASE_PATH, './graphs/node_detection/denial_of_service_cfg_cg_compressed_graphs.gpickle')

class NODE_CLASSIFIER_CONFIG_FRONT_RUNNING(str, Enum):
    CHECKPOINT = join(BASE_PATH, './models/node_detection/nodetype/front_running_hgt.pth')
    COMPRESSED_GRAPH = join(BASE_PATH, './graphs/node_detection/front_running_cfg_cg_compressed_graphs.gpickle')


class NODE_CLASSIFIER_CONFIG_REENTRANCY(str, Enum):
    CHECKPOINT = join(BASE_PATH, './models/node_detection/nodetype/reentrancy_hgt.pth')
    COMPRESSED_GRAPH = join(BASE_PATH, './graphs/node_detection/reentrancy_cfg_cg_compressed_graphs.gpickle')


class NODE_CLASSIFIER_CONFIG_TIME_MANIPULATION(str, Enum):
    CHECKPOINT = join(BASE_PATH, './models/node_detection/nodetype/time_manipulation_hgt.pth')
    COMPRESSED_GRAPH = join(BASE_PATH, './graphs/node_detection/time_manipulation_cfg_cg_compressed_graphs.gpickle')


class NODE_CLASSIFIER_CONFIG_UNCHECKED_LOW_LEVEL_CALLS(str, Enum):
    CHECKPOINT = join(BASE_PATH, './models/node_detection/nodetype/reentrancy_hgt.pth')
    COMPRESSED_GRAPH = join(BASE_PATH, './graphs/node_detection/reentrancy_cfg_cg_compressed_graphs.gpickle')


class Settings(BaseSettings):
    SERVER_NAME = 'sco'
    VERSION: str = 'v1.0.0'
    DEVICE: str = 'GPU' if check_gpu() else 'CPU'
    SERVER_TAG: str = f'{SERVER_NAME}-{VERSION}-{DEVICE}'
    SERVICE: str = 'vulnerability'
    TASK: str = 'detection'
    PREFIX: str = f'/{VERSION}/{SERVICE}/{TASK}'
    API_KEY = 'MqQVfJ6Fq1umZnUI7ZuaycciCjxi3gM0'
    DEVICE: str = 'cuda:0' if check_gpu() else 'cpu'
    class Config:
        env_file = '.env'

settings = Settings()
