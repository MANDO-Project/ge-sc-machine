import base64
import binascii
from typing import Optional, List

from logbook import Logger
from pydantic import Field, validator, BaseModel

from ..config import settings

logger = Logger(__name__)


class NodeRequest(BaseModel):
    filename: str = Field(description='The file name of smart contracts included dataset')


class NodeResponse(BaseModel):
    message: str
    results: Optional[List]
