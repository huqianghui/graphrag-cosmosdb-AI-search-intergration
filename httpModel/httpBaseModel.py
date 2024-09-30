
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


# Data models
class Message(BaseModel):
    role: str
    content: str

