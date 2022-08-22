import base64
import binascii
from typing import List, Optional

from uuid import UUID, uuid4
from pydantic import Field
from logbook import Logger
from pydantic import Field, validator, BaseModel

from ..schemas.fields import BugType, GraphStructure, Message, Node


logger = Logger(__name__)


class ContractRequest(BaseModel):
    smart_contract: str = Field(description='The file content in base64 encoded format.')
    contract_name: str = 'contract_0.sol'

    class Config:
        schema_extra = {
            'smart_contract': 'LyoKICogQHNvdXJjZTogaHR0cHM6Ly9zbWFydGNvbnRyYWN0c2VjdXJpdHkuZ2l0aHViLmlvL1NXQy1yZWdpc3RyeS9kb2NzL1NXQy0xMjQjYXJiaXRyYXJ5LWxvY2F0aW9uLXdyaXRlLXNpbXBsZXNvbAogKiBAYXV0aG9yOiBTdWhhYmUgQnVncmFyYQogKiBAdnVsbmVyYWJsZV9hdF9saW5lczogMjcKICovCgogcHJhZ21hIHNvbGlkaXR5IF4wLjQuMjU7CgogY29udHJhY3QgV2FsbGV0IHsKICAgICB1aW50W10gcHJpdmF0ZSBib251c0NvZGVzOwogICAgIGFkZHJlc3MgcHJpdmF0ZSBvd25lcjsKCiAgICAgY29uc3RydWN0b3IoKSBwdWJsaWMgewogICAgICAgICBib251c0NvZGVzID0gbmV3IHVpbnRbXSgwKTsKICAgICAgICAgb3duZXIgPSBtc2cuc2VuZGVyOwogICAgIH0KCiAgICAgZnVuY3Rpb24gKCkgcHVibGljIHBheWFibGUgewogICAgIH0KCiAgICAgZnVuY3Rpb24gUHVzaEJvbnVzQ29kZSh1aW50IGMpIHB1YmxpYyB7CiAgICAgICAgIGJvbnVzQ29kZXMucHVzaChjKTsKICAgICB9CgogICAgIGZ1bmN0aW9uIFBvcEJvbnVzQ29kZSgpIHB1YmxpYyB7CiAgICAgICAgIC8vIDx5ZXM+IDxyZXBvcnQ+IEFDQ0VTU19DT05UUk9MCiAgICAgICAgIHJlcXVpcmUoMCA8PSBib251c0NvZGVzLmxlbmd0aCk7IC8vIHRoaXMgY29uZGl0aW9uIGlzIGFsd2F5cyB0cnVlIHNpbmNlIGFycmF5IGxlbmd0aHMgYXJlIHVuc2lnbmVkCiAgICAgICAgIGJvbnVzQ29kZXMubGVuZ3RoLS07IC8vIGFuIHVuZGVyZmxvdyBjYW4gYmUgY2F1c2VkIGhlcmUKICAgICB9CgogICAgIGZ1bmN0aW9uIFVwZGF0ZUJvbnVzQ29kZUF0KHVpbnQgaWR4LCB1aW50IGMpIHB1YmxpYyB7CiAgICAgICAgIHJlcXVpcmUoaWR4IDwgYm9udXNDb2Rlcy5sZW5ndGgpOwogICAgICAgICBib251c0NvZGVzW2lkeF0gPSBjOyAvLyB3cml0ZSB0byBhbnkgaW5kZXggbGVzcyB0aGFuIGJvbnVzQ29kZXMubGVuZ3RoCiAgICAgfQoKICAgICBmdW5jdGlvbiBEZXN0cm95KCkgcHVibGljIHsKICAgICAgICAgcmVxdWlyZShtc2cuc2VuZGVyID09IG93bmVyKTsKICAgICAgICAgc2VsZmRlc3RydWN0KG1zZy5zZW5kZXIpOwogICAgIH0KIH0K',
            'contract_name': 'smart_contract_0.sol'
        }

    @validator('smart_contract')
    def decode_b64_content(cls, v):
        try:
            return base64.b64decode(v)
        except binascii.Error as e:
            logger.debug('Received content: {}', v[:5])
            raise ValueError(str(e))


class FailedCase(BaseModel):
    message: Message


class FineGrainedDetectReponse(BaseModel):
    id: UUID = uuid4()
    smart_contract_length: int = None
    message: Message = None
    bug_type: BugType = None
    runtime: int = None
    number_of_bug_node: int = None
    number_of_normal_node: int = None
    vulnerability: bool = None
    graph: Optional[GraphStructure] = None
    results: List[Node] = None

class CoarseGrainedDetectReponse(BaseModel):
    id: UUID = uuid4()
    smart_contract_length: int
    message: Message = None
    bug_type: BugType = None
    runtime: int = None
    vulnerability: bool = None


class MultiBuggyNodeDetectReponse(BaseModel):
    id: UUID = uuid4()
    messages: Optional[str]
    summaries: Optional[List]
    # summaries: Optional[Dict]
    smart_contract_length: Optional[int]
    heatmap_categories: Optional[int]


class MultiBuggyGraphDetectReponse(BaseModel):
    id: UUID = uuid4()
    summaries: List
    smart_contract_length: int
