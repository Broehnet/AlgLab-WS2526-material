from pydantic import BaseModel, Field
from status import Status
from typing import Optional

class Solution(BaseModel):
    coloring: dict
    num_colors: Optional[float] = Field(None)
    lower_bound: Optional[float] = Field(None)
    status: Status
