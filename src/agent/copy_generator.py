from langgraph.graph import StateGraph
from langgraph.graph.state import CompiledStateGraph

from agent.state import AgentState
from models.llm import LLM


class CopyGenerator:
    def __init__(self, llm: LLM) -> None:
        self.llm = llm
        self.graph = self.build_graph()

    def build_graph(self) -> CompiledStateGraph:
        graph_builder = StateGraph(AgentState)
        graph_builder.add_node(self.generate_copy)
        graph_builder.add_node(self.refine_copy)

        graph_builder.set_entry_point("generate_copy")
        graph_builder.add_edge("generate_copy", "refine_copy")
        graph_builder.set_finish_point("refine_copy")
        return graph_builder.compile()

    def generate_copy(self, state: AgentState) -> dict:
        response = self.llm(
            [
                (
                    "system",
                    "あなたはプロのコピーライターです。",
                )
            ]
            + [
                (
                    "human",
                    f"""以下のテーマで、キャッチコピーを1つ生成してください。必ず結果のみ出力してください。
                    <theme_copy>
                    {state['theme_copy']}
                    </theme_copy>
                    """,
                )
            ]
        )

        display_message_dict = {
            "role": "assistant",
            "title": "Copy Generatorの生成結果",
            "icon": "📝",
            "content": response.content,
        }

        return {
            "messages": response,
            "draft_copy": response.content,
            "display_message_dict": display_message_dict,
        }

    def refine_copy(self, state: AgentState) -> dict:
        response = self.llm(
            [
                (
                    "system",
                    "あなたはプロのコピーライターです。",
                )
            ]
            + [
                (
                    "human",
                    f"""多角的な観点で、以下のキャッチコピーを改善してください。必ず結果のみ、改善した1つのコピーだけ出力してください。
                    <draft_copy>
                    {state['draft_copy']}
                    </draft_copy>
                    """,
                )
            ]
        )

        display_message_dict = {
            "role": "assistant",
            "title": "Copy Generatorの改善結果",
            "icon": "📝",
            "content": response.content,
        }

        return {
            "messages": response,
            "display_message_dict": display_message_dict,
        }
