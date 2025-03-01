import json

from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import Command
from typing_extensions import Literal

from agent.copy_generator import CopyGenerator
from agent.image_generator import ImageGenerator
from agent.state import AgentState
from agent.tools import handoff_to_copy_generator, handoff_to_image_generator
from models.llm import LLM


class Supervisor:
    def __init__(
        self, llm: LLM, copy_generator: CopyGenerator, image_generator: ImageGenerator
    ) -> None:
        self.tools = [handoff_to_copy_generator, handoff_to_image_generator]
        self.tools_by_name = {tool.name: tool for tool in self.tools}
        self.llm_with_tools = llm.model.bind_tools(self.tools)
        self.graph = self.build_graph(copy_generator, image_generator)

    def build_graph(
        self, copy_generator: CopyGenerator, image_generator: ImageGenerator
    ) -> CompiledStateGraph:
        graph_builder = StateGraph(AgentState)
        graph_builder.add_node(self.supervisor)
        graph_builder.add_node("copy_generator_subgraph", copy_generator.graph)
        graph_builder.add_node("image_generator_subgraph", image_generator.graph)
        graph_builder.add_node(self.end_node)
        graph_builder.add_edge("copy_generator_subgraph", "supervisor")
        graph_builder.add_edge("image_generator_subgraph", "supervisor")
        graph_builder.set_entry_point("supervisor")
        return graph_builder.compile()

    def supervisor(self, state: AgentState) -> Command[
        Literal[
            "copy_generator_subgraph",
            "image_generator_subgraph",
            "end_node",
        ]
    ]:
        response = self.llm_with_tools.invoke(
            [
                (
                    "system",
                    """
                    あなたは、Sub Agentの会話を管理する役割を持つ監督者です。
                    ユーザーのリクエストに基づき、どのSub Agentを指示するか（どのツールを呼び出すか）を決定します。
                    ツール呼び出しの必要がない場合は、ユーザーのサポートを行います。

                    - Sub Agent呼び出しが必要あれば、Sub Agentを呼び出してください。その際、なぜそのSub Agentを呼び出すのかの理由も説明してください。
                    - **Sub Agent呼び出しが不要な場合は、Sub Agentを呼び出す必要はありません。** 
                    - 直前にSub Agentを呼び出した場合、Sub Agentの結果を整理して報告してください。
                    """,
                )
            ]
            + state["messages"]
            + [
                (
                    "human",
                    """
                    <instructions>
                    会話を基にSub Agentを呼び出してください。呼び出しの必要がなければ、Sub Agentの結果を整理して報告してください。
                    </instructions>
                    """,
                )
            ]
        )

        print(response)

        # tool messageをメッセージに追加
        state["messages"].append(response)

        if len(response.tool_calls) > 0:
            for tool_call in response.tool_calls:
                tool = self.tools_by_name[tool_call["name"]]
                tool_response = tool.invoke(
                    {**tool_call, "args": {**tool_call["args"], "state": state}}
                )
                invoke_result = json.loads(tool_response.content)

            display_message_dict = {
                "role": "assistant",
                "title": "Supervisorの思考が完了しました。",
                "icon": "👨‍🏫",
                "content": response.content,
            }

            return Command(
                goto=invoke_result["goto"],
                update={
                    **invoke_result["update"],
                    "display_message_dict": display_message_dict,
                },
            )

        else:
            display_message_dict = {
                "role": "assistant",
                "title": "Supervisorの回答",
                "icon": "👨‍🏫",
                "content": response.content,
            }
            return Command(
                goto="end_node",
                update={
                    "messages": response,
                    "display_message_dict": display_message_dict,
                },
            )

    def end_node(self, state: AgentState) -> Command[Literal[END]]:
        print("Node: end_node" + "\n")

        return Command(
            goto=END,
            update={"is_finished": True, "display_message_dict": None},
        )

    # ================
    # Helper
    # ================
    def write_mermaid_graph(self) -> None:
        print("Writing graph.md")
        with open("graph.md", "w") as file:
            file.write(f"```mermaid\n{self.graph.get_graph(xray=1).draw_mermaid()}```")
