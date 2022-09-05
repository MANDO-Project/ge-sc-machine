import os
from os.path import join
from enum import Enum

from pydantic import BaseSettings

from .common.utils import check_gpu
from .common.utils import init_node_classificator
from .common.utils import init_graph_classificator
from .consts import BugType


BASE_PATH = os.path.dirname(__file__)


# Node config ============================================
class NODE_CLASSIFIER_CONFIG_ACCESS_CONTROL(str, Enum):
    CHECKPOINT = join(BASE_PATH, './models/node_detection/nodetype/access_control_han.pth')
    COMPRESSED_GRAPH = join(BASE_PATH, './graphs/node_detection/access_control_cfg_cg_compressed_graphs.gpickle')


class NODE_CLASSIFIER_CONFIG_ARITHMETIC(str, Enum):
    CHECKPOINT = join(BASE_PATH, './models/node_detection/nodetype/arithmetic_han.pth')
    COMPRESSED_GRAPH = join(BASE_PATH, './graphs/node_detection/arithmetic_cfg_cg_compressed_graphs.gpickle')

class NODE_CLASSIFIER_CONFIG_DENIAL_OF_SERVICE(str, Enum):
    CHECKPOINT = join(BASE_PATH, './models/node_detection/nodetype/denial_of_service_han.pth')
    COMPRESSED_GRAPH = join(BASE_PATH, './graphs/node_detection/denial_of_service_cfg_cg_compressed_graphs.gpickle')

class NODE_CLASSIFIER_CONFIG_FRONT_RUNNING(str, Enum):
    CHECKPOINT = join(BASE_PATH, './models/node_detection/nodetype/front_running_han.pth')
    COMPRESSED_GRAPH = join(BASE_PATH, './graphs/node_detection/front_running_cfg_cg_compressed_graphs.gpickle')


class NODE_CLASSIFIER_CONFIG_REENTRANCY(str, Enum):
    CHECKPOINT = join(BASE_PATH, './models/node_detection/nodetype/reentrancy_han.pth')
    COMPRESSED_GRAPH = join(BASE_PATH, './graphs/node_detection/reentrancy_cfg_cg_compressed_graphs.gpickle')


class NODE_CLASSIFIER_CONFIG_TIME_MANIPULATION(str, Enum):
    CHECKPOINT = join(BASE_PATH, './models/node_detection/nodetype/time_manipulation_han.pth')
    COMPRESSED_GRAPH = join(BASE_PATH, './graphs/node_detection/time_manipulation_cfg_cg_compressed_graphs.gpickle')


class NODE_CLASSIFIER_CONFIG_UNCHECKED_LOW_LEVEL_CALLS(str, Enum):
    CHECKPOINT = join(BASE_PATH, './models/node_detection/nodetype/unchecked_low_level_calls_han.pth')
    COMPRESSED_GRAPH = join(BASE_PATH, './graphs/node_detection/unchecked_low_level_calls_cfg_cg_compressed_graphs.gpickle')
#==========================================================


# Graph config ============================================
class GRAPH_CLASSIFIER_CONFIG_ACCESS_CONTROL(str, Enum):
    CHECKPOINT = join(BASE_PATH, './models/graph_detection/nodetype/access_control_han.pth')
    COMPRESSED_GRAPH = join(BASE_PATH, './graphs/graph_detection/access_control_cfg_cg_compressed_graphs.gpickle')


class GRAPH_CLASSIFIER_CONFIG_ARITHMETIC(str, Enum):
    CHECKPOINT = join(BASE_PATH, './models/graph_detection/nodetype/arithmetic_han.pth')
    COMPRESSED_GRAPH = join(BASE_PATH, './graphs/graph_detection/arithmetic_cfg_cg_compressed_graphs.gpickle')

class GRAPH_CLASSIFIER_CONFIG_DENIAL_OF_SERVICE(str, Enum):
    CHECKPOINT = join(BASE_PATH, './models/graph_detection/nodetype/denial_of_service_han.pth')
    COMPRESSED_GRAPH = join(BASE_PATH, './graphs/graph_detection/denial_of_service_cfg_cg_compressed_graphs.gpickle')

class GRAPH_CLASSIFIER_CONFIG_FRONT_RUNNING(str, Enum):
    CHECKPOINT = join(BASE_PATH, './models/graph_detection/nodetype/front_running_han.pth')
    COMPRESSED_GRAPH = join(BASE_PATH, './graphs/graph_detection/front_running_cfg_cg_compressed_graphs.gpickle')


class GRAPH_CLASSIFIER_CONFIG_REENTRANCY(str, Enum):
    CHECKPOINT = join(BASE_PATH, './models/graph_detection/nodetype/reentrancy_han.pth')
    COMPRESSED_GRAPH = join(BASE_PATH, './graphs/graph_detection/reentrancy_cfg_cg_compressed_graphs.gpickle')


class GRAPH_CLASSIFIER_CONFIG_TIME_MANIPULATION(str, Enum):
    CHECKPOINT = join(BASE_PATH, './models/graph_detection/nodetype/time_manipulation_han.pth')
    COMPRESSED_GRAPH = join(BASE_PATH, './graphs/graph_detection/time_manipulation_cfg_cg_compressed_graphs.gpickle')


class GRAPH_CLASSIFIER_CONFIG_UNCHECKED_LOW_LEVEL_CALLS(str, Enum):
    CHECKPOINT = join(BASE_PATH, './models/graph_detection/nodetype/unchecked_low_level_calls_han.pth')
    COMPRESSED_GRAPH = join(BASE_PATH, './graphs/graph_detection/unchecked_low_level_calls_cfg_cg_compressed_graphs.gpickle')
#==========================================================


class Settings(BaseSettings):
    SERVER_NAME = 'MANDO'
    VERSION: str = 'v1.0.0'
    DEVICE: str = 'cuda:0' if check_gpu() else 'cpu'
    SERVER_TAG: str = f'{SERVER_NAME}-{VERSION}-{DEVICE}'
    SERVICE: str = 'vulnerability'
    TASK: str = 'detection'
    PREFIX: str = f'/{VERSION}/{SERVICE}/{TASK}'
    API_KEY = 'MqQVfJ6Fq1umZnUI7ZuaycciCjxi3gM0'
    STORAGE: str = './sco/_static'
    class Config:
        env_file = '.env'

settings = Settings()


# Initial Models
## Node classifier models
node_classifier_access_control = init_node_classificator(NODE_CLASSIFIER_CONFIG_ACCESS_CONTROL.CHECKPOINT,
                                                         NODE_CLASSIFIER_CONFIG_ACCESS_CONTROL.COMPRESSED_GRAPH,
                                                         settings.DEVICE)
node_classifier_arithmetic = init_node_classificator(NODE_CLASSIFIER_CONFIG_ARITHMETIC.CHECKPOINT,
                                                     NODE_CLASSIFIER_CONFIG_ARITHMETIC.COMPRESSED_GRAPH,
                                                     settings.DEVICE)
node_classifier_denial_of_service = init_node_classificator(NODE_CLASSIFIER_CONFIG_DENIAL_OF_SERVICE.CHECKPOINT,
                                                            NODE_CLASSIFIER_CONFIG_DENIAL_OF_SERVICE.COMPRESSED_GRAPH,
                                                            settings.DEVICE)   
node_classifier_front_running = init_node_classificator(NODE_CLASSIFIER_CONFIG_FRONT_RUNNING.CHECKPOINT,
                                                        NODE_CLASSIFIER_CONFIG_FRONT_RUNNING.COMPRESSED_GRAPH,
                                                        settings.DEVICE)                                     
node_classifier_reentrancy = init_node_classificator(NODE_CLASSIFIER_CONFIG_REENTRANCY.CHECKPOINT,
                                                     NODE_CLASSIFIER_CONFIG_REENTRANCY.COMPRESSED_GRAPH,
                                                     settings.DEVICE)
node_classifier_time_manipulation = init_node_classificator(NODE_CLASSIFIER_CONFIG_TIME_MANIPULATION.CHECKPOINT,
                                                            NODE_CLASSIFIER_CONFIG_TIME_MANIPULATION.COMPRESSED_GRAPH,
                                                            settings.DEVICE)
node_classifier_unchecked_low_level_calls = init_node_classificator(NODE_CLASSIFIER_CONFIG_UNCHECKED_LOW_LEVEL_CALLS.CHECKPOINT,
                                                                    NODE_CLASSIFIER_CONFIG_UNCHECKED_LOW_LEVEL_CALLS.COMPRESSED_GRAPH,
                                                                    settings.DEVICE)
NODE_MODEL_OPTS = {
                   BugType.ACCESS_CONTROL: node_classifier_access_control,
                   BugType.ARITHMETIC: node_classifier_arithmetic,
                   BugType.DENIAL_OF_SERVICE: node_classifier_denial_of_service,
                   BugType.FRONT_RUNNING: node_classifier_front_running,
                   BugType.REENTRANCY: node_classifier_reentrancy,
                   BugType.TIME_MANIPULATION: node_classifier_time_manipulation,
                   BugType.UNCHECKED_LOW_LEVEL_CALLS: node_classifier_unchecked_low_level_calls
                  }

## Graph classifier models
graph_classifier_access_control = init_graph_classificator(GRAPH_CLASSIFIER_CONFIG_ACCESS_CONTROL.CHECKPOINT,
                                                           GRAPH_CLASSIFIER_CONFIG_ACCESS_CONTROL.COMPRESSED_GRAPH,
                                                           settings.DEVICE)
graph_classifier_arithmetic = init_graph_classificator(GRAPH_CLASSIFIER_CONFIG_ARITHMETIC.CHECKPOINT,
                                                       GRAPH_CLASSIFIER_CONFIG_ARITHMETIC.COMPRESSED_GRAPH,
                                                       settings.DEVICE)
graph_classifier_denial_of_service = init_graph_classificator(GRAPH_CLASSIFIER_CONFIG_DENIAL_OF_SERVICE.CHECKPOINT,
                                                              GRAPH_CLASSIFIER_CONFIG_DENIAL_OF_SERVICE.COMPRESSED_GRAPH,
                                                              settings.DEVICE)   
graph_classifier_front_running = init_graph_classificator(GRAPH_CLASSIFIER_CONFIG_FRONT_RUNNING.CHECKPOINT,
                                                          GRAPH_CLASSIFIER_CONFIG_FRONT_RUNNING.COMPRESSED_GRAPH,
                                                          settings.DEVICE)                                     
graph_classifier_reentrancy = init_graph_classificator(GRAPH_CLASSIFIER_CONFIG_REENTRANCY.CHECKPOINT,
                                                       GRAPH_CLASSIFIER_CONFIG_REENTRANCY.COMPRESSED_GRAPH,
                                                       settings.DEVICE)
graph_classifier_time_manipulation = init_graph_classificator(GRAPH_CLASSIFIER_CONFIG_TIME_MANIPULATION.CHECKPOINT,
                                                              GRAPH_CLASSIFIER_CONFIG_TIME_MANIPULATION.COMPRESSED_GRAPH,
                                                              settings.DEVICE)
graph_classifier_unchecked_low_level_calls = init_graph_classificator(GRAPH_CLASSIFIER_CONFIG_UNCHECKED_LOW_LEVEL_CALLS.CHECKPOINT,
                                                                      GRAPH_CLASSIFIER_CONFIG_UNCHECKED_LOW_LEVEL_CALLS.COMPRESSED_GRAPH,
                                                                      settings.DEVICE)

GRAPH_MODEL_OPTS = {
              BugType.ACCESS_CONTROL: graph_classifier_access_control,
              BugType.ARITHMETIC: graph_classifier_arithmetic,
              BugType.DENIAL_OF_SERVICE: graph_classifier_denial_of_service,
              BugType.FRONT_RUNNING: graph_classifier_front_running,
              BugType.REENTRANCY: graph_classifier_reentrancy,
              BugType.TIME_MANIPULATION: graph_classifier_time_manipulation,
              BugType.UNCHECKED_LOW_LEVEL_CALLS: graph_classifier_unchecked_low_level_calls
            }