
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from httpModel.httpBaseModel import Message


class ChatCompletionRequest(BaseModel):
    model: Optional[str] = "gpt-4o"
    messages: Optional[List[Message]] = []
    temperature: Optional[float] = 1.0
    top_p: Optional[float] = 1.0
    n: Optional[int] = 1
    stream: Optional[bool] = False
    stop: Optional[Union[str, List[str]]] = None
    max_tokens: Optional[int] = None
    presence_penalty: Optional[float] = 0
    frequency_penalty: Optional[float] = 0
    logit_bias: Optional[Dict[str, float]] = None
    user: Optional[str] = None


