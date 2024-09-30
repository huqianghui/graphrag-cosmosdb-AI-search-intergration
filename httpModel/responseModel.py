
import time
import uuid
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from httpModel.httpBaseModel import Message


class Usage(BaseModel):
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    
class ChatCompletionResponseChoice(BaseModel):
    index: Optional[int] = None
    message: Optional[Message] = None
    finish_reason: Optional[str] = None

class ChatCompletionResponse(BaseModel):
    id: str = Field(default_factory=lambda: f"chatcmpl-{uuid.uuid4().hex}")
    object: str = "chat.completion"
    created: int = Field(default_factory=lambda: int(time.time()))
    model: Optional[str]="gpt-4o"
    choices: List[ChatCompletionResponseChoice]
    usage: Optional[Usage]=None
    system_fingerprint: Optional[str] = None

