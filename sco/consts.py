from enum import Enum


class BugType(str, Enum):
    ACCESS_CONTROL = 'access_control'
    ARITHMETIC = 'arithmetic'
    DENIAL_OF_SERVICE = 'denial_of_service'
    FRONT_RUNNING = 'front_running'
    REENTRANCY = 'reentrancy'
    TIME_MANIPULATION = 'time_manipulation'
    UNCHECKED_LOW_LEVEL_CALLS = 'unchecked_low_level_calls'


class NodeFeature(str, Enum):
    NODE_TYPE = 'nodetype'
    METAPATH2VEC = 'metapath2vec'


class Message(str, Enum):
    ILLEGAL_CONTRACT = 'Found a illegal solidity smart contract'
    STRANGE_GRAPH = 'Found non-existent nodes/edges in the graph'
    UNSUPPORTED = 'Bug type is unsupported'
    OK = 'Successful'
