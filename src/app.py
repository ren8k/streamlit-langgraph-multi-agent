import streamlit as st
from langchain_core.messages import HumanMessage

from agent.copy_generator import CopyGenerator
from agent.image_generator import ImageGenerator
from agent.supervisor import Supervisor
from models.bedrock_img_gen_model import BedrockImageModel
from models.llm import LLM
from utils.app_util import display_message, display_messages

MODEL = "claude-3-5"
IMG_GEN_MODEL = "nova-canvas"
THREAD_ID = "1"
TEMPERATURE = 0.2


def main() -> None:
    # Page Config
    st.set_page_config(
        page_title="Streamlit×LangGraph MultiAgent | コピー生成アプリケーション",
        page_icon="🤖",
    )
    st.title("Streamlit×LangGraph MultiAgent | コピー生成アプリケーション")

    # Init Actors
    llm = LLM(MODEL, TEMPERATURE)
    bedrock_image_model = BedrockImageModel(IMG_GEN_MODEL)

    copy_generator = CopyGenerator(llm)
    image_generator = ImageGenerator(llm, bedrock_image_model)

    supervisor = Supervisor(llm, copy_generator, image_generator)

    # Session State
    if "is_start_chat" not in st.session_state:
        st.session_state.is_start_chat = False
    if "display_messages" not in st.session_state:
        init_display_message_dict = {
            "role": "assistant",
            "title": "Supervisorの回答",
            "icon": "👨‍🏫",
            "content": """
            こんにちは！何かお手伝いできることはありますか？
            以下の機能を利用することができます。

            - コピー生成
            - 画像生成
            """,
        }
        st.session_state.display_messages = [init_display_message_dict]
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # User Input
    user_input = st.chat_input("メッセージを入力してください:")
    if user_input:
        display_message_dict = {
            "role": "user",
            "title": "ユーザーの入力",
            "icon": "👤",
            "content": user_input,
        }
        st.session_state.display_messages.append(display_message_dict)
        st.session_state.is_start_chat = True

    # Display Messages
    display_messages(st.session_state.display_messages)

    if not st.session_state.is_start_chat:
        st.stop()

    # Core Algorithm
    inputs = {"messages": st.session_state.messages + [HumanMessage(user_input)]}
    config = {"configurable": {"thread_id": THREAD_ID}}

    supervisor.write_mermaid_graph()

    event_prev = {}
    for event in supervisor.graph.stream(
        inputs, config, stream_mode="values", subgraphs=True
    ):
        # Skip when transition between parent and child
        if event_prev == event[1]:
            continue
        event_prev = event[1]
        # Display Message
        if display_message_dict := event[1].get("display_message_dict"):
            display_message(display_message_dict)
            st.session_state.display_messages.append(display_message_dict)

        # Update Message History
        messages = event[1].get("messages")
    st.session_state.messages.extend(messages)


if __name__ == "__main__":
    main()
