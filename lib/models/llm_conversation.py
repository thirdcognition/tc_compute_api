from app.core.enums import LanguageModel, ollama_models_chat
from lib.models.conversation_data import LlmConversationData
from lib.models.supabase.llm_conversation import LlmConversationModel, LlmConversationMessageModel, LlmConversationMessageHistoryModel
from pydantic import BaseModel, UUID4, Field
from cachetools import TTLCache
from datetime import datetime, timezone
from typing import List, Optional, Annotated, Tuple, Union
from supabase.client import AsyncClient
from app.core.config import settings


# The rest of the code remains the same...

class LlmConversation:
    def __init__(self, supabase: AsyncClient, auth_id: UUID4, organization_id: UUID4):
        self.supabase: supabase
        self.conversation_data: LlmConversationData = LlmConversationData(supabase, auth_id, organization_id)

    # Function which creates new conversation with the initial message and response from the LLM
    async def new_message(
        self,
        model: LanguageModel,
        initial_message: Optional[str] = None,
        initial_response: Optional[str] = None,
    ):
        # Create the conversation
        conversation = LlmConversationModel(
            started_at=datetime.now(timezone.utc)
        )
        await conversation.save_to_supabase()

        if initial_message is not None:
            # Add the conversation to the cache
            # Insert the conversation into the database
            # Create the initial message and response
            message = LlmConversationMessageModel(
                content=initial_message,
                model=model,
                type="human"
            )
            await message.save_to_supabase(self.supabase)

        if initial_response is not None:
            response = LlmConversationMessageModel(
                content=initial_response,
                model=model,
                type="ai"
            )
            await response.save_to_supabase(self.supabase)


    # async def get_conversation_history(
    #     self, conversation: Union[UUID4, LlmConversation]
    # ) -> List[LlmConversationMessageHistory]:
    #     if isinstance(conversation, LlmConversation):
    #         conversation_id = conversation.id
    #     else:
    #         conversation_id = conversation

    #     # Check if the conversation history is already in the cache
    #     if conversation_id in self.history_cache:
    #         return self.history_cache[conversation_id]

    #     # If not, fetch from the database
    #     response = (
    #         await self.supabase.table("conversation_message_history")
    #         .select("*")
    #         .eq("conversation_id", str(conversation_id))
    #         .execute()
    #     )
    #     history = [LlmConversationMessageHistory(**data) for data in response.data]

    #     # Update the cache with the new conversation history
    #     self.history_cache[conversation_id] = history

    #     return history

    # async def get_messages_with_history(
    #     self, conversation: Union[UUID4, LlmConversation]
    # ) -> List[Tuple[LlmConversationMessage, Optional[LlmConversationMessage], Optional[LlmConversationMessage]]]:
    #     if isinstance(conversation, LlmConversation):
    #         conversation_id = conversation.id
    #     else:
    #         conversation_id = conversation

    #     # Check if the conversation_id is already in the cache
    #     if conversation_id in self.messages_with_history_cache:
    #         return self.messages_with_history_cache[conversation_id]

    #     # Fetch the conversation history
    #     history = await self.get_conversation_history(conversation_id)

    #     # Extract the message IDs, previous message IDs, and next message IDs from the conversation history
    #     message_mapping = {
    #         history_item.message_id: {
    #             "previous_message_id": history_item.previous_message_id,
    #             "next_message_id": history_item.next_message_id,
    #             "query": history_item.query_id,
    #             "response": history_item.response_id,
    #         }
    #         for history_item in history
    #         if history_item.message_id is not None
    #     }

    #     # Fetch the messages from the database
    #     # Fetch the messages from the database using conversation_id
    #     response = (
    #         await self.supabase.table("conversation_messages")
    #         .select("*")
    #         .eq("conversation_id", str(conversation_id))
    #         .execute()
    #     )
    #     messages = [LlmConversationMessage(**data) for data in response.data]

    #     # Map the messages using the message_mapping list
    #     messages_with_history_cache = []
    #     for message in messages:
    #         if message.id in message_mapping:
    #             previous_message_id = message_mapping[message.id].get("previous_message_id")
    #             next_message_id = message_mapping[message.id].get("next_message_id")

    #             previous_message = next((msg for msg in messages if msg.id == previous_message_id), None) if previous_message_id is not None else None
    #             next_message = next((msg for msg in messages if msg.id == next_message_id), None) if next_message_id is not None else None

    #             messages_with_history_cache.append((message, next_message, previous_message))

    #     # Update the cache with the new messages
    #     self.messages_with_history_cache[conversation_id] = messages_with_history_cache

    #     return messages_with_history_cache

# The rest of the code remains