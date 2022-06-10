import base64
import binascii
from typing import Any, Optional, List
from urllib.request import BaseHandler

from logbook import Logger
from pydantic import Field, validator, BaseModel

<<<<<<< HEAD
=======
from ..config import settings_access_contro
>>>>>>> 0eb5c972 (commit)

logger = Logger(__name__)


class NodeRequest(BaseModel):
    filename: str = Field(description='The file name of smart contracts included dataset')

class Graph(BaseModel):
    nodes:Optional[Any]
    links:Optional[Any]
class NodeResponse(BaseModel):
    message: str
    results: Optional[List]
    graph: Graph
