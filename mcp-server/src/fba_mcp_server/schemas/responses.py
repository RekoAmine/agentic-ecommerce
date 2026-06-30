"""Response envelopes for MCP tools."""

from pydantic import BaseModel, ConfigDict, Field


class ToolResponse[DataT](BaseModel):
    """Common successful response envelope returned by tools."""

    model_config = ConfigDict(frozen=True)

    data: DataT
    simulated: bool = True
    message: str = Field(default="Simulated response generated successfully.")
