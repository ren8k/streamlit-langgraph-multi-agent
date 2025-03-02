from langgraph.graph.message import add_messages
from typing_extensions import Annotated, Literal, NotRequired, TypedDict


class DisplayMessageDict(TypedDict):
    role: Literal["user", "assistant"]
    title: str
    icon: str
    content: str
    images: NotRequired[list[str]]


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]

    # Copy Generator
    theme_copy: str
    draft_copy: str

    # Image Generator
    visual_concept: str
    img_prompt: str

    is_finished: bool
    display_message_dict: DisplayMessageDict
