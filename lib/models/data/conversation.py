import asyncio
from typing import List, Optional
from datetime import datetime, timezone

from lib.models.supabase.llm_conversation import (
    LlmConversationModel,
    LlmConversationMessageModel,
    LlmConversationMessageHistoryModel,
    LlmConversationThreadModel,
)
from lib.models.user import User


class LlmConversationData:
    def __init__(
        self,
        user: User,
        conversations: Optional[List[LlmConversationModel]] = None,
        messages: Optional[List[LlmConversationMessageModel]] = None,
        message_history: Optional[List[LlmConversationMessageHistoryModel]] = None,
        threads: Optional[List[LlmConversationThreadModel]] = None,
    ):
        """
        Initialize a LlmConversationData object.

        :param user: The user associated with the conversation data.
        :type user: User
        :param conversations: The list of conversations, defaults to None. If provided, it is used to initialize the conversations attribute.
        :type conversations: Optional[List[LlmConversationModel]], optional
        :param messages: The list of messages, defaults to None. If provided, it is used to initialize the messages attribute.
        :type messages: Optional[List[LlmConversationMessageModel]], optional
        :param message_history: The list of message history, defaults to None. If provided, it is used to initialize the message_history attribute.
        :type message_history: Optional[List[LlmConversationMessageHistoryModel]], optional
        :param threads: The list of threads, defaults to None. If provided, it is used to initialize the threads attribute.
        :type threads: Optional[List[LlmConversationThreadModel]], optional
        """
        self.user: User = user
        self.conversations: Optional[List[LlmConversationModel]] = conversations
        self.messages: Optional[List[LlmConversationMessageModel]] = messages
        self.message_history: Optional[
            List[LlmConversationMessageHistoryModel]
        ] = message_history
        self.threads: Optional[List[LlmConversationThreadModel]] = threads

    async def save_all_to_supabase(self):
        """
        Save all data to Supabase.
        """
        # Separate lists for different model types
        conversations_to_upsert: List[LlmConversationModel] = []
        messages_to_upsert: List[LlmConversationMessageModel] = []
        histories_to_upsert: List[LlmConversationMessageHistoryModel] = []
        threads_to_upsert: List[LlmConversationThreadModel] = []

        # Collect instances
        if self.conversations:
            conversations_to_upsert.extend(self.conversations)
        if self.messages:
            messages_to_upsert.extend(self.messages)
        if self.message_history:
            histories_to_upsert.extend(self.message_history)
        if self.threads:
            threads_to_upsert.extend(self.threads)

        # Prepare upsert tasks
        upsert_tasks = []

        if conversations_to_upsert:
            upsert_tasks.append(
                conversations_to_upsert[0].upsert_to_supabase(
                    self.user.supabase, conversations_to_upsert
                )
            )

        if messages_to_upsert:
            upsert_tasks.append(
                messages_to_upsert[0].upsert_to_supabase(
                    self.user.supabase, messages_to_upsert
                )
            )

        if histories_to_upsert:
            upsert_tasks.append(
                histories_to_upsert[0].upsert_to_supabase(
                    self.user.supabase, histories_to_upsert
                )
            )

        if threads_to_upsert:
            upsert_tasks.append(
                threads_to_upsert[0].upsert_to_supabase(
                    self.user.supabase, threads_to_upsert
                )
            )

        # Run all upsert operations concurrently
        await asyncio.gather(*upsert_tasks)

    async def fetch_conversations(self, refresh: bool = False) -> None:
        """
        Fetch the conversations from Supabase.

        :param refresh: Whether to refresh the data from Supabase, defaults to False
        :type refresh: bool, optional
        """
        if not self.conversations or refresh:
            self.conversations = (
                await LlmConversationModel.fetch_existing_from_supabase(
                    self.user.supabase,
                    filter={
                        "owner_id": str(self.user.auth_id),
                        "organization_id": str(self.user.active_organization_id),
                    },
                )
            )

    async def fetch_messages(self, refresh: bool = False) -> None:
        """
        Fetch the messages from Supabase.

        :param refresh: Whether to refresh the data from Supabase, defaults to False
        :type refresh: bool, optional
        """
        if not self.messages or refresh:
            self.messages = (
                await LlmConversationMessageModel.fetch_existing_from_supabase(
                    self.user.supabase,
                    filter={
                        "owner_id": str(self.user.auth_id),
                        "organization_id": str(self.user.active_organization_id),
                    },
                )
            )

    async def fetch_message_history(self, refresh: bool = False) -> None:
        """
        Fetch the message history from Supabase.

        :param refresh: Whether to refresh the data from Supabase, defaults to False
        :type refresh: bool, optional
        """
        if not self.message_history or refresh:
            self.message_history = (
                await LlmConversationMessageHistoryModel.fetch_existing_from_supabase(
                    self.user.supabase,
                    filter={
                        "owner_id": str(self.user.auth_id),
                        "organization_id": str(self.user.active_organization_id),
                    },
                )
            )

    async def fetch_threads(self, refresh: bool = False) -> None:
        """
        Fetch the threads from Supabase.

        :param refresh: Whether to refresh the data from Supabase, defaults to False
        :type refresh: bool, optional
        """
        if not self.threads or refresh:
            self.threads = (
                await LlmConversationThreadModel.fetch_existing_from_supabase(
                    self.user.supabase,
                    filter={
                        "owner_id": str(self.user.auth_id),
                        "organization_id": str(self.user.active_organization_id),
                    },
                )
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
        await conversation.create(self.user.supabase)

        if initial_message is not None:
            message = LlmConversationMessageModel(
                content=initial_message,
                model=model,
                type="human",
                conversation_id=conversation.id,
                owner_id=self.user.auth_id,
                organization_id=self.user.active_organization_id,
            )
            await message.create(self.user.supabase)

        if initial_response is not None:
            response = LlmConversationMessageModel(
                content=initial_response,
                model=model,
                type="ai",
                conversation_id=conversation.id,
                owner_id=self.user.auth_id,
                organization_id=self.user.active_organization_id,
            )
            await response.create(self.user.supabase)
