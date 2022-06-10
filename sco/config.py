import os
from os.path import join
from typing import Union
from logbook import base

from pydantic import BaseSettings
from pydantic.main import BaseModel

from .common.utils import check_gpu


BASE_PATH = os.path.dirname(__file__)


class NODE_CLASSIFIER_CONFIG_ACCESS_CONTROL(BaseSettings):
    CHECKPOINT = join(BASE_PATH, '../models/node_classification/cfg_cg/line/reentrancy/han_fold_0.pth')
    COMPRESSED_GRAPH = join(BASE_PATH, '../models/node_classification/cfg_cg/line/reentrancy/buggy_curated/cfg_cg_compressed_graphs.gpickle')
    DATASET = join(BASE_PATH, '../models/node_classification/cfg_cg/line/reentrancy/buggy_curated')
    feature_extractor = join(BASE_PATH, '../models/node_classification/cfg_cg/line/reentrancy/matrix_line_dim128_of_core_graph_of_reentrancy_cfg_cg_buggy_curated.pkl')


class NODE_CLASSIFIER_CONFIG_ARITHMETIC(BaseSettings):
    CHECKPOINT = join(BASE_PATH, '../models/node_classification/cfg_cg/line/reentrancy/han_fold_0.pth')
    COMPRESSED_GRAPH = join(BASE_PATH, '../models/node_classification/cfg_cg/line/reentrancy/buggy_curated/cfg_cg_compressed_graphs.gpickle')
    DATASET = join(BASE_PATH, '../models/node_classification/cfg_cg/line/reentrancy/buggy_curated')
    feature_extractor = join(BASE_PATH, '../models/node_classification/cfg_cg/line/reentrancy/matrix_line_dim128_of_core_graph_of_reentrancy_cfg_cg_buggy_curated.pkl')


class NODE_CLASSIFIER_CONFIG_DENIAL_OF_SERVICE(BaseSettings):
    CHECKPOINT = join(BASE_PATH, '../models/node_classification/cfg_cg/line/reentrancy/han_fold_0.pth')
    COMPRESSED_GRAPH = join(BASE_PATH, '../models/node_classification/cfg_cg/line/reentrancy/buggy_curated/cfg_cg_compressed_graphs.gpickle')
    DATASET = join(BASE_PATH, '../models/node_classification/cfg_cg/line/reentrancy/buggy_curated')
    feature_extractor = join(BASE_PATH, '../models/node_classification/cfg_cg/line/reentrancy/matrix_line_dim128_of_core_graph_of_reentrancy_cfg_cg_buggy_curated.pkl')


class NODE_CLASSIFIER_CONFIG_FRONT_RUNNING(BaseSettings):
    CHECKPOINT = join(BASE_PATH, '../models/node_classification/cfg_cg/line/reentrancy/han_fold_0.pth')
    COMPRESSED_GRAPH = join(BASE_PATH, '../models/node_classification/cfg_cg/line/reentrancy/buggy_curated/cfg_cg_compressed_graphs.gpickle')
    DATASET = join(BASE_PATH, '../models/node_classification/cfg_cg/line/reentrancy/buggy_curated')
    feature_extractor = join(BASE_PATH, '../models/node_classification/cfg_cg/line/reentrancy/matrix_line_dim128_of_core_graph_of_reentrancy_cfg_cg_buggy_curated.pkl')


class NODE_CLASSIFIER_CONFIG_REENTRANCY(BaseSettings):
    CHECKPOINT = join(BASE_PATH, '/Users/minh/Documents/2022/smart_contract/mando/ge-sc/models/node_classification/hgt/cfg_cg/nodetype/reentrancy/han_fold_0.pth')
    COMPRESSED_GRAPH = join(BASE_PATH, '/Users/minh/Documents/2022/smart_contract/mando/ge-sc/experiments/ge-sc-data/source_code/reentrancy/buggy_curated/cfg_cg_compressed_graphs.gpickle')
    DATASET = join(BASE_PATH, '../models/node_classification/cfg_cg/line/reentrancy/buggy_curated')
    feature_extractor = join(BASE_PATH, '../models/node_classification/cfg_cg/line/reentrancy/matrix_line_dim128_of_core_graph_of_reentrancy_cfg_cg_buggy_curated.pkl')


class NODE_CLASSIFIER_CONFIG_TIME_MANIPULATION(BaseSettings):
    CHECKPOINT = join(BASE_PATH, '../models/node_classification/cfg_cg/line/reentrancy/han_fold_0.pth')
    COMPRESSED_GRAPH = join(BASE_PATH, '../models/node_classification/cfg_cg/line/reentrancy/buggy_curated/cfg_cg_compressed_graphs.gpickle')
    DATASET = join(BASE_PATH, '../models/node_classification/cfg_cg/line/reentrancy/buggy_curated')
    feature_extractor = join(BASE_PATH, '../models/node_classification/cfg_cg/line/reentrancy/matrix_line_dim128_of_core_graph_of_reentrancy_cfg_cg_buggy_curated.pkl')


class NODE_CLASSIFIER_CONFIG_UNCHECKED_LOW_LEVEL_CALLS(BaseSettings):
    CHECKPOINT = join(BASE_PATH, '../models/node_classification/cfg_cg/line/reentrancy/han_fold_0.pth')
    COMPRESSED_GRAPH = join(BASE_PATH, '../models/node_classification/cfg_cg/line/reentrancy/buggy_curated/cfg_cg_compressed_graphs.gpickle')
    DATASET = join(BASE_PATH, '../models/node_classification/cfg_cg/line/reentrancy/buggy_curated')
    feature_extractor = join(BASE_PATH, '../models/node_classification/cfg_cg/line/reentrancy/matrix_line_dim128_of_core_graph_of_reentrancy_cfg_cg_buggy_curated.pkl')


class Settings_ACCESS_CONTROL(BaseSettings):
    SERVER_NAME = 'sco'
    VERSION: str = 'v1.0.0'
    DEVICE: str = 'GPU' if check_gpu() else 'CPU'
    SERVER_TAG: str = f'{SERVER_NAME}-{VERSION}-{DEVICE}'
    SERVICE: str = 'vulnerability'
    TASK: str = 'detection'
    PREFIX: str = f'/{VERSION}/{SERVICE}/{TASK}'
    LINE = NODE_CLASSIFIER_CONFIG_ACCESS_CONTROL()
    API_KEY = 'MqQVfJ6Fq1umZnUI7ZuaycciCjxi3gM0'
    DEVICE: str = 'cuda:0' if check_gpu() else 'cpu'
    class Config:
        env_file = '.env'


class Settings_ARITHMETIC(BaseSettings):
    SERVER_NAME = 'sco'
    VERSION: str = 'v1.0.0'
    DEVICE: str = 'GPU' if check_gpu() else 'CPU'
    SERVER_TAG: str = f'{SERVER_NAME}-{VERSION}-{DEVICE}'
    SERVICE: str = 'vulnerability'
    TASK: str = 'detection'
    PREFIX: str = f'/{VERSION}/{SERVICE}/{TASK}'
    LINE = NODE_CLASSIFIER_CONFIG_ARITHMETIC()
    API_KEY = 'MqQVfJ6Fq1umZnUI7ZuaycciCjxi3gM0'
    DEVICE: str = 'cuda:0' if check_gpu() else 'cpu'
    class Config:
        env_file = '.env'


class Settings_DENIAL_OF_SERVICE(BaseSettings):
    SERVER_NAME = 'sco'
    VERSION: str = 'v1.0.0'
    DEVICE: str = 'GPU' if check_gpu() else 'CPU'
    SERVER_TAG: str = f'{SERVER_NAME}-{VERSION}-{DEVICE}'
    SERVICE: str = 'vulnerability'
    TASK: str = 'detection'
    PREFIX: str = f'/{VERSION}/{SERVICE}/{TASK}'
    LINE = NODE_CLASSIFIER_CONFIG_DENIAL_OF_SERVICE()
    API_KEY = 'MqQVfJ6Fq1umZnUI7ZuaycciCjxi3gM0'
    DEVICE: str = 'cuda:0' if check_gpu() else 'cpu'
    class Config:
        env_file = '.env'


class Settings_FRONT_RUNNING(BaseSettings):
    SERVER_NAME = 'sco'
    VERSION: str = 'v1.0.0'
    DEVICE: str = 'GPU' if check_gpu() else 'CPU'
    SERVER_TAG: str = f'{SERVER_NAME}-{VERSION}-{DEVICE}'
    SERVICE: str = 'vulnerability'
    TASK: str = 'detection'
    PREFIX: str = f'/{VERSION}/{SERVICE}/{TASK}'
    LINE = NODE_CLASSIFIER_CONFIG_FRONT_RUNNING()
    API_KEY = 'MqQVfJ6Fq1umZnUI7ZuaycciCjxi3gM0'
    DEVICE: str = 'cuda:0' if check_gpu() else 'cpu'
    class Config:
        env_file = '.env'


class Settings_REENTRANCY(BaseSettings):
    SERVER_NAME = 'sco'
    VERSION: str = 'v1.0.0'
    DEVICE: str = 'GPU' if check_gpu() else 'CPU'
    SERVER_TAG: str = f'{SERVER_NAME}-{VERSION}-{DEVICE}'
    SERVICE: str = 'vulnerability'
    TASK: str = 'detection'
    PREFIX: str = f'/{VERSION}/{SERVICE}/{TASK}'
    LINE = NODE_CLASSIFIER_CONFIG_REENTRANCY()
    API_KEY = 'MqQVfJ6Fq1umZnUI7ZuaycciCjxi3gM0'
    DEVICE: str = 'cuda:0' if check_gpu() else 'cpu'
    class Config:
        env_file = '.env'


class Settings_TIME_MANIPULATION(BaseSettings):
    SERVER_NAME = 'sco'
    VERSION: str = 'v1.0.0'
    DEVICE: str = 'GPU' if check_gpu() else 'CPU'
    SERVER_TAG: str = f'{SERVER_NAME}-{VERSION}-{DEVICE}'
    SERVICE: str = 'vulnerability'
    TASK: str = 'detection'
    PREFIX: str = f'/{VERSION}/{SERVICE}/{TASK}'
    LINE = NODE_CLASSIFIER_CONFIG_TIME_MANIPULATION()
    API_KEY = 'MqQVfJ6Fq1umZnUI7ZuaycciCjxi3gM0'
    DEVICE: str = 'cuda:0' if check_gpu() else 'cpu'
    class Config:
        env_file = '.env'


class Settings_UNCHECKED_LOW_LEVEL_CALLS(BaseSettings):
    SERVER_NAME = 'sco'
    VERSION: str = 'v1.0.0'
    DEVICE: str = 'GPU' if check_gpu() else 'CPU'
    SERVER_TAG: str = f'{SERVER_NAME}-{VERSION}-{DEVICE}'
    SERVICE: str = 'vulnerability'
    TASK: str = 'detection'
    PREFIX: str = f'/{VERSION}/{SERVICE}/{TASK}'
    LINE = NODE_CLASSIFIER_CONFIG_UNCHECKED_LOW_LEVEL_CALLS()
    API_KEY = 'MqQVfJ6Fq1umZnUI7ZuaycciCjxi3gM0'
    DEVICE: str = 'cuda:0' if check_gpu() else 'cpu'
    class Config:
        env_file = '.env'


settings_access_control = Settings_ACCESS_CONTROL()
settings_arithmetic = Settings_ARITHMETIC()
settings_denial_of_service = Settings_DENIAL_OF_SERVICE()
settings_front_running = Settings_FRONT_RUNNING()
settings_reentrancy = Settings_REENTRANCY()
settings_time_manipulation = Settings_TIME_MANIPULATION()
settings_unchecked_low_level_calls = Settings_UNCHECKED_LOW_LEVEL_CALLS()
