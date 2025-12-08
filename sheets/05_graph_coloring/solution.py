from pydantic import BaseModel
from status import Status


class Solution(BaseModel):
    coloring: dict
    num_colors: int
    lower_bound: float | None
    status: Status
