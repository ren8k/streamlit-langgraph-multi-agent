from typing import Annotated

from langchain_core.tools import tool
from langchain_core.tools.base import InjectedToolCallId


@tool
def handoff_to_copy_generator(
    theme_copy: Annotated[
        str,
        "コピーのテーマ。どのようなコピー文を生成すべきかという内容が記載されている。",
    ],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> dict:
    """
    コピー生成を行うために、copy_generatorに引き継ぎます。
    ユーザーがコピー生成を要望している場合、このツールを呼び出します。

    copy_generatorの役割は以下の通り
    - テーマに基づいてコピー文を生成します
    """
    print("## Called Copy Generator")

    tool_msg = {
        "role": "tool",
        "content": "Successfully transferred to Copy Generator.",
        "tool_call_id": tool_call_id,
    }

    return {
        "goto": "copy_generator_subgraph",
        "update": {
            "messages": [tool_msg],
            "theme_copy": theme_copy,
        },
    }


@tool
def handoff_to_image_generator(
    visual_concept: Annotated[
        str,
        "画像の主題（ビジュアルコンセプト）。どのような画像を生成すべきかという内容が記載されている。",
    ],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> dict:
    """
    画像生成を行うために、image_generatorに引き継ぎます。
    ユーザーが画像生成を要望している場合、このツールを呼び出します。

    image_generatorの役割は以下の通り
    - 画像の主題（ビジュアルコンセプト）に基づいて画像を生成します
    """
    print("## Called Image Generator")

    tool_msg = {
        "role": "tool",
        "content": "Successfully transferred to Image Generator.",
        "tool_call_id": tool_call_id,
    }

    return {
        "goto": "image_generator_subgraph",
        "update": {
            "messages": [tool_msg],
            "visual_concept": visual_concept,
        },
    }
