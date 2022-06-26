from typing import List, Optional

from pydantic import BaseModel

from ..consts import BugType, Message


class Node(BaseModel):
    id: int
    name: Optional[str]
    vulnerability: bool
    code_lines: List[int] 


class Edge(BaseModel):
    source: int
    target: int


class GraphStructure(BaseModel):
    nodes: List[Node]
    edges: List[Edge]


class CoarseGrainedReport(BaseModel):
    bug_type: Optional[BugType]
    message: Message
    runtime: int
    vulnerability: bool
    

class FineGrainedReport(BaseModel):
    bug_type: Optional[BugType]
    message: Message
    runtime: int
    number_of_bug_node: int
    number_of_normal_node: int
    vulnerability: bool
    graph: Optional[GraphStructure]
    results: List[Node]
    

class Summarize(BaseModel):
    bug_type: BugType
    coarse_grained_report: CoarseGrainedReport
    fine_grained_report: FineGrainedReport
