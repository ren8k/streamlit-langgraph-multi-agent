import streamlit as st
from PIL import Image

from utils.img_util import convert_base64_2_img


def display_message(message: dict) -> None:
    """
    messageをstreamlit上に表示する関数
    """
    with st.chat_message(message["role"]):
        with st.expander(
            message["title"],
            expanded=True,
            icon=message["icon"],
        ):
            if "images" in message:
                st.write(message["content"])
                # images is saved as List[Image.Image]
                images = [convert_base64_2_img(img) for img in message["images"]]
                _show_images(images)
            else:
                st.write(message["content"], unsafe_allow_html=True)


def display_messages(messages: list[dict]) -> None:
    """
    streamlit上で過去のメッセージをすべて表示する関数
    """
    for message in messages:
        display_message(message)


def _show_images(images: list[Image.Image]) -> None:
    """
    画像をstreamlit上に表示する関数
    """
    cols = st.columns(len(images))
    for idx, col in enumerate(cols):
        with col:
            st.image(
                images[idx],
                caption=f"画像 {idx+1}",
            )
