from langchain_aws import ChatBedrockConverse
from langchain_core.language_models import BaseChatModel
from langchain_core.language_models.base import LanguageModelInput
from langchain_core.messages import BaseMessage


class LLM:
    def __init__(self, model_name: str, temperature: float):
        self.model = self._initialize_llm(model_name, temperature)

    def _initialize_llm(self, model_name: str, temperature: float) -> BaseChatModel:
        if model_name == "claude-3-5":
            return ChatBedrockConverse(
                model="anthropic.claude-3-5-sonnet-20241022-v2:0",
                region_name="us-west-2",
                temperature=temperature,
            )
        else:
            raise ValueError(f"Model name {model_name} not supported.")

    def __call__(self, input: LanguageModelInput) -> BaseMessage:
        """LLMの呼び出し"""
        try:
            return self.model.invoke(input)
        except Exception as e:
            raise e
