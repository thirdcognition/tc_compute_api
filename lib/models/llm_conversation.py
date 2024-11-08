from lib.models.data.conversation import LlmConversationData
from lib.models.supabase.llm_conversation import (
    LlmConversationModel,
    LlmConversationMessageModel,
    LlmConversationMessageHistoryModel,
)
from uuid import UUID
from datetime import datetime, timezone
from typing import List, Optional, Tuple
from supabase.client import AsyncClient


class LlmConversation:
    def __init__(self, supabase: AsyncClient, auth_id: UUID, organization_id: UUID):
        self.supabase = supabase
        self.conversation_data: LlmConversationData = LlmConversationData(
            supabase, auth_id, organization_id
        )

    async def new_message(
        self,
        model,  # : LanguageModel,
        initial_message: Optional[str] = None,
        initial_response: Optional[str] = None,
    ):
        """
        Create a new conversation with the initial message and response from the LLM.

        :param model: The language model used for generating responses.
        :param initial_message: The initial message content, defaults to None.
        :type initial_message: Optional[str], optional
        :param initial_response: The initial response content, defaults to None.
        :type initial_response: Optional[str], optional
        """
        conversation = LlmConversationModel(start_time=datetime.now(timezone.utc))
        await conversation.save_to_supabase(self.supabase)

        if initial_message is not None:
            message = LlmConversationMessageModel(
                content=initial_message,
                model=model,
                type="human",
                conversation_id=conversation.id,
            )
            await message.save_to_supabase(self.supabase)

        if initial_response is not None:
            response = LlmConversationMessageModel(
                content=initial_response,
                model=model,
                type="ai",
                conversation_id=conversation.id,
            )
            await response.save_to_supabase(self.supabase)

    async def get_conversation_history(
        self, conversation_id: UUID
    ) -> List[LlmConversationMessageHistoryModel]:
        """
        Get the conversation history for a specific conversation.

        :param conversation_id: The ID of the conversation.
        :type conversation_id: UUID
        :return: The conversation history.
        :rtype: List[LlmConversationMessageHistoryModel]
        """
        response = (
            await self.supabase.table("llm_conversation_message_history")
            .select("*")
            .eq("conversation_id", str(conversation_id))
            .execute()
        )
        return [LlmConversationMessageHistoryModel(**data) for data in response.data]

    async def get_messages_with_history(
        self, conversation_id: UUID
    ) -> List[
        Tuple[
            LlmConversationMessageModel,
            Optional[LlmConversationMessageModel],
            Optional[LlmConversationMessageModel],
        ]
    ]:
        """
        Get messages with their history for a specific conversation.

        :param conversation_id: The ID of the conversation.
        :type conversation_id: UUID
        :return: The messages with their history.
        :rtype: List[Tuple[LlmConversationMessageModel, Optional[LlmConversationMessageModel], Optional[LlmConversationMessageModel]]]
        """
        history = await self.get_conversation_history(conversation_id)

        message_mapping = {
            history_item.message_id: {
                "previous_message_id": history_item.previous_message_id,
                "next_message_id": history_item.next_message_id,
                "query": history_item.query_id,
                "response": history_item.response_id,
            }
            for history_item in history
            if history_item.message_id is not None
        }

        response = (
            await self.supabase.table("llm_conversation_message")
            .select("*")
            .eq("conversation_id", str(conversation_id))
            .execute()
        )
        messages = [LlmConversationMessageModel(**data) for data in response.data]

        messages_with_history = []
        for message in messages:
            if message.id in message_mapping:
                previous_message_id = message_mapping[message.id].get(
                    "previous_message_id"
                )
                next_message_id = message_mapping[message.id].get("next_message_id")

                previous_message = (
                    next(
                        (msg for msg in messages if msg.id == previous_message_id), None
                    )
                    if previous_message_id is not None
                    else None
                )
                next_message = (
                    next((msg for msg in messages if msg.id == next_message_id), None)
                    if next_message_id is not None
                    else None
                )

                messages_with_history.append((message, next_message, previous_message))

        return messages_with_history
