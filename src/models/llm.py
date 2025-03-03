from typing import Literal, TypeAlias

from langchain_aws import ChatBedrockConverse
from langchain_core.language_models import BaseChatModel
from langchain_core.language_models.base import LanguageModelInput
from langchain_core.messages import BaseMessage

MODEL_NAME_TYPE: TypeAlias = Literal["claude-3-7-sonnet", "claude-3-5-haiku"]


class LLM:
    def __init__(
        self,
        model_name: MODEL_NAME_TYPE,
        temperature: float,
    ):
        self.model = self._initialize_llm(model_name, temperature)

    def _initialize_llm(
        self,
        model_name: MODEL_NAME_TYPE,
        temperature: float,
    ) -> BaseChatModel:
        if model_name == "claude-3-7-sonnet":
            model_id = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"
        elif model_name == "claude-3-5-haiku":
            model_id = "us.anthropic.claude-3-5-haiku-20241022-v1:0"
        else:
            raise ValueError(f"Model name {model_name} not supported.")
        return ChatBedrockConverse(
            model=model_id,
            region_name="us-west-2",
            temperature=temperature,
        )

    def __call__(self, input: LanguageModelInput) -> BaseMessage:
        """LLMの呼び出し"""
        try:
            return self.model.invoke(input)
        except Exception as e:
            raise e
