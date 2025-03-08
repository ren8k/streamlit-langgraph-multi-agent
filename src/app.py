import streamlit as st
from langchain_core.messages import HumanMessage

from agent.copy_generator import CopyGenerator
from agent.image_generator import ImageGenerator
from agent.supervisor import Supervisor
from models.bedrock_img_gen_model import BedrockImageModel
from models.llm import LLM
from utils.app_util import display_message, display_messages

MODEL = "claude-3-7-sonnet"  # you can use "claude-3-5-haiku"
IMG_GEN_MODEL = "nova-canvas"
THREAD_ID = "1"
TEMPERATURE = 0.2


def main() -> None:
    # Page Config
    st.set_page_config(
        page_title="Streamlit×LangGraph MultiAgent | 広告素材生成アプリケーション",
        page_icon="🤖",
    )
    st.title("Streamlit×LangGraph MultiAgent | 広告素材生成アプリケーション")

    # Init Actors
    llm = LLM(MODEL, TEMPERATURE)
    bedrock_image_model = BedrockImageModel(IMG_GEN_MODEL)
    copy_generator = CopyGenerator(llm)
    image_generator = ImageGenerator(llm, bedrock_image_model)

    # Set session state
    if "display_messages" not in st.session_state:
        init_display_message_dict = {
            "role": "assistant",
            "title": "Supervisorの回答",
            "icon": "👨‍🏫",
            "content": """
            こんにちは！何かお手伝いできることはありますか？\u0020\u0020
            以下の機能を利用することができます。

            - コピー生成
            - 画像生成
            """,
        }
        st.session_state.display_messages = [init_display_message_dict]
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "supervisor" not in st.session_state:
        st.session_state.supervisor = Supervisor(llm, copy_generator, image_generator)

    # Display All Messages
    display_messages(st.session_state.display_messages)

    # User Input
    user_input = st.chat_input("メッセージを入力してください:")
    if user_input:
        display_message_dict = {
            "role": "user",
            "title": "ユーザーの入力",
            "icon": "👤",
            "content": user_input,
        }
        display_message(display_message_dict)
        st.session_state.display_messages.append(display_message_dict)
    else:
        st.stop()

    # Core Algorithm
    inputs = {"messages": [HumanMessage(user_input)]}
    config = {"configurable": {"thread_id": THREAD_ID}}
    st.session_state.supervisor.write_mermaid_graph()

    event_prev = {}
    for event in st.session_state.supervisor.graph.stream(
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

        # Get the latest message list (cumulative list that updates with each loop)
        messages = event[1].get("messages")
    # After the loop, add the final message list to the session
    st.session_state.messages.extend(messages)


if __name__ == "__main__":
    main()
