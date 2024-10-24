from dataclasses import asdict, dataclass
from typing import List, Optional


@dataclass
class Entity:
    id: str
    name: str
    description: str
    type: str
    human_readable_id: str
    description_embedding: Optional[List[float]]
    