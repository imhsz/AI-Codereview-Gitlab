import os
from typing import Dict, List, Optional

from openai import OpenAI

from biz.llm.client.base import BaseClient
from biz.llm.types import NotGiven, NOT_GIVEN
from biz.utils.log import logger


class CustomClient(BaseClient):
    """
    自定义供应商客户端类，支持OpenAI兼容接口的模型服务。
    """
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("CUSTOM_API_KEY")
        self.base_url = os.getenv("CUSTOM_API_BASE_URL")
        
        if not self.api_key:
            raise ValueError("API key is required. Please provide it or set it in the environment variables.")
        
        if not self.base_url:
            raise ValueError("Base URL is required. Please set it in the environment variables.")
        
        try:
            self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
            self.default_model = os.getenv("CUSTOM_API_MODEL", "gpt-3.5-turbo")
            logger.info(f"自定义供应商客户端初始化成功，使用模型: {self.default_model}")
        except Exception as e:
            logger.error(f"自定义供应商客户端初始化失败: {e}")
            raise

    def completions(self,
                    messages: List[Dict[str, str]],
                    model: Optional[str] | NotGiven = NOT_GIVEN,
                    ) -> str:
        """
        调用自定义供应商的API进行对话。
        """
        try:
            model = model or self.default_model
            completion = self.client.chat.completions.create(
                model=model,
                messages=messages,
            )
            return completion.choices[0].message.content
        except Exception as e:
            logger.error(f"自定义供应商API调用失败: {e}")
            raise 