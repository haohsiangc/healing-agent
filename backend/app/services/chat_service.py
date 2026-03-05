import base64
import logging
from typing import List

from anthropic import Anthropic
from app.agent.base import SkillResult
from app.agent.skills import skill_registry

logger = logging.getLogger(__name__)

COUNSELOR_SYSTEM_PROMPT = """對話請以繁體中文進行：你是一位熟悉現象學心理學取向的諮商實習生，擅長引導使用者描述他事情中的當下知覺到的事物。
回答問題的時候必須有同理心，請同理使用者說的內容，再繼續回答與討論或給予建議。回答不要超過30個字。當你收到類似介紹自己的提問時，說自己擅長陪人聊天，引導大家療癒自己。"""

IMAGE_COUNSELOR_PROMPT = """對話請以繁體中文進行：你是一位熟悉現象學心理學的諮商實習生，請根據使用者對他所選出的圖像描述進行引導，
指出這張圖像與先前對話的關聯，幫助使用者探索他們的分享與該圖像間的連結，並繼續對話。"""

TRANSLATE_PROMPT = """You are a professional text-to-image prompt generator. Using the following Chinese text, generate a creative image generation prompt in English. 
Keep it under 60 tokens. Focus on emotions, colors, and atmosphere rather than literal translation."""


class ChatService:
    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-latest"):
        self.client = Anthropic(api_key=api_key)
        self.model = model

    def chat(
        self,
        user_message: str,
        history: List[dict],  # [{"role": "user"|"assistant", "content": str}]
    ) -> SkillResult:
        """
        Generate a counseling response using Agent Skills.
        Returns a SkillResult whose .message is the reply text and whose
        .flags carries metadata (e.g. {"suggest_meditation": True/False}).
        """
        system_msg = COUNSELOR_SYSTEM_PROMPT
        history_msgs = history.copy()
        history_msgs.append({"role": "user", "content": user_message})

        tools = skill_registry.get_definitions()
        last_skill_result: SkillResult | None = None

        # Agent Skill Calling Loop
        while True:
            response = self.client.messages.create(
                model=self.model,
                system=system_msg,
                messages=history_msgs,
                max_tokens=1000,
                temperature=0.8,
                tools=tools,
            )

            if response.stop_reason == "tool_use":
                history_msgs.append({"role": "assistant", "content": response.content})

                tool_results = []
                for content_block in response.content:
                    if content_block.type == "tool_use":
                        skill_result = skill_registry.execute(
                            content_block.name, content_block.input
                        )
                        last_skill_result = skill_result
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": content_block.id,
                            "content": skill_result.message or "Success",
                        })

                history_msgs.append({"role": "user", "content": tool_results})

                # Short-circuit: if any executed skill set suggest_meditation,
                # return its result immediately without another LLM call.
                if last_skill_result and last_skill_result.flags.get("suggest_meditation"):
                    return last_skill_result

            else:
                # LLM provided a final text response without active tool calls
                text_response = next(
                    (block.text for block in response.content if block.type == "text"),
                    "抱歉，我目前無法回應。",
                )
                return SkillResult(message=text_response, flags={"suggest_meditation": False})

    def translate_to_image_prompt(self, chinese_text: str) -> str:
        """Translate a Chinese conversation summary into an English image generation prompt."""
        response = self.client.messages.create(
            model=self.model,
            system=TRANSLATE_PROMPT,
            messages=[{"role": "user", "content": chinese_text}],
            temperature=0.3,
            max_tokens=80,
        )
        return next((block.text for block in response.content if block.type == "text"), "abstract healing art")

    def chat_about_image(
        self,
        user_message: str,
        image_base64: str,
        conversation_history: List[dict],
    ) -> str:
        """Multimodal: discuss the selected image with conversation context."""
        # Build context summary for the system message
        history_text = "\n".join(
            f"{m['role']}: {m['content']}" for m in conversation_history[-6:]
        )
        system_content = IMAGE_COUNSELOR_PROMPT
        if history_text:
            system_content += f"\n\n先前對話摘要：\n{history_text}"

        response = self.client.messages.create(
            model=self.model,
            system=system_content,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",  # Assuming standard JPEG encoding throughout app
                                "data": image_base64
                            }
                        },
                        {
                            "type": "text",
                            "text": f"看到這張圖像，讓我想到：{user_message}"
                        }
                    ]
                }
            ],
            max_tokens=300,
        )
        return next((block.text for block in response.content if block.type == "text"), "抱歉，我無法讀取圖像。")
