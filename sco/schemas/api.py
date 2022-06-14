import base64
import binascii
from dis import disco
from typing import Any, List, Dict, Optional

from uuid import UUID, uuid4
from pydantic import Field
from logbook import Logger
from pydantic import Field, validator, BaseModel

from ..consts import BugType


logger = Logger(__name__)


class NodeRequest(BaseModel):
    filename: str = Field(description='The file name of smart contracts included dataset')


class ContractRequest(BaseModel):
    smart_contract: bytes = Field(description='The file content in base64 encoded format.')

    @validator('smart_contract')
    def decode_b64_content(cls, v):
        try:
            return base64.b64decode(v)
        except binascii.Error as e:
            logger.debug('Received content: {}', v[:5])
            raise ValueError(str(e))


class NodeDetectReponse(BaseModel):
    id: UUID = uuid4()
    message: str
    results: Optional[List]
    graph: Optional[Dict]


class MultiBuggyNodeDetectReponse(BaseModel):
    id: UUID = uuid4()
    summaries: List
    smart_contract_length: int
    heatmap_categories: int


class MultiBuggyGraphDetectReponse(BaseModel):
    id: UUID = uuid4()
    summaries: List
    smart_contract_length: int


class Graph(BaseModel):
    nodes:Optional[Any]
    links:Optional[Any]


class NodeResponse(BaseModel):
    message: str
    results: Optional[List]
    graph: Graph
