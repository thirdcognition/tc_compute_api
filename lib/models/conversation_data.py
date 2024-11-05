from typing import Dict, List, Optional, Union
from lib.models.organization_user import OrganizationUser
from lib.models.supabase.llm_conversation import LlmConversationModel, LlmConversationMessageModel, LlmConversationMessageHistoryModel, LlmConversationThreadModel
from lib.models.user_data import UserData
from pydantic import UUID4
from postgrest import APIResponse
from supabase.client import AsyncClient

class LlmConversationData:
    def __init__(
        self,
        user: OrganizationUser,
        conversations: Optional[List[LlmConversationModel]] = None,
        messages: Optional[List[LlmConversationMessageModel]] = None,
        message_history: Optional[List[LlmConversationMessageHistoryModel]] = None,
        threads: Optional[List[LlmConversationThreadModel]] = None,
    ):
        """
        Initialize a LlmConversationData object.

        :param supabase: The Supabase client. Used for making API calls to Supabase.
        :type supabase: AsyncClient
        :param auth_id: The ID of the user. Used to fetch user-specific data.
        :type auth_id: UUID4
        :param organization_id: The ID of the organization. Used to fetch organization-specific data.
        :type organization_id: UUID4
        :param _active_conversation_id: The ID of the active conversation, defaults to None.
        :type _active_conversation_id: Optional[UUID4], optional
        :param conversations: The list of conversations, defaults to None. If provided, it is used to initialize the conversations attribute.
        :type conversations: Optional[List[LlmConversation]], optional
        :param messages: The list of messages, defaults to None. If provided, it is used to initialize the messages attribute.
        :type messages: Optional[List[LlmConversationMessage]], optional
        :param message_history: The list of message history, defaults to None. If provided, it is used to initialize the message_history attribute.
        :type message_history: Optional[List[LlmConversationMessageHistory]], optional
        :param threads: The list of threads, defaults to None. If provided, it is used to initialize the threads attribute.
        :type threads: Optional[List[LlmConversationThread]], optional
        """
        self.user: OrganizationUser = user
        self.conversations: Optional[List[LlmConversationModel]] = conversations
        self.messages: Optional[List[LlmConversationMessageModel]] = messages
        self.message_history: Optional[List[LlmConversationMessageHistoryModel]] = message_history
        self.threads: Optional[List[LlmConversationThreadModel]] = threads

    async def save_all_to_supabase(self):
        """
        Save all data to Supabase.

        :param supabase: The Supabase client.
        :type supabase: AsyncClient
        """
        if self.conversations:
            for conversation in self.conversations:
                await conversation.save_to_supabase(self.user.supabase)
        if self.messages:
            for message in self.messages:
                await message.save_to_supabase(self.user.supabase)
        if self.message_history:
            for history in self.message_history:
                await history.save_to_supabase(self.user.supabase)
        if self.threads:
            for thread in self.threads:
                await thread.save_to_supabase(self.user.supabase)

    async def fetch_conversations(self, refresh: bool = False) -> None:
        """
        Fetch the conversations from Supabase.

        :param refresh: Whether to refresh the data from Supabase, defaults to False
        :type refresh: bool, optional
        """
        if not self.conversations or refresh:
            response: APIResponse = (
                await self.user.supabase.table("llm_conversation")
                .select("*")
                .eq("owner_id", str(self.user.auth_id))
                .eq("organization_id", str(self.user.active_organization_id)) .execute()
            )
            self.conversations = [ LlmConversationModel(**data) for data in response.data ]

    async def fetch_messages(self, refresh: bool = False) -> None:
        """
        Fetch the messages from Supabase.

        :param refresh: Whether to refresh the data from Supabase, defaults to False
        :type refresh: bool, optional
        """
        if not self.messages or refresh:
            response: APIResponse = (
                await self.user.supabase.table("llm_conversation_message")
                .select("*")
                .eq("owner_id", str(self.user.auth_id))
                .eq("organization_id", str(self.user.active_organization_id))
                .execute()
            )
            self.messages = [
                LlmConversationMessageModel(**data) for data in response.data
            ]

    async def fetch_message_history(self, refresh: bool = False) -> None:
        """
        Fetch the message history from Supabase.

        :param refresh: Whether to refresh the data from Supabase, defaults to False
        :type refresh: bool, optional
        """
        if not self.message_history or refresh:
            response: APIResponse = (
                await self.user.supabase.table("llm_conversation_message_history")
                .select("*")
                .eq("owner_id", str(self.user.auth_id))
                .eq("organization_id", str(self.user.active_organization_id))
                .execute()
            )
            self.message_history = [
                LlmConversationMessageHistoryModel(**data) for data in response.data
            ]

    async def fetch_threads(self, refresh: bool = False) -> None:
        """
        Fetch the threads from Supabase.

        :param refresh: Whether to refresh the data from Supabase, defaults to False
        :type refresh: bool, optional
        """
        if not self.threads or refresh:
            response: APIResponse = (
                await self.user.supabase.table("llm_conversation_thread")
                .select("*")
                .eq("owner_id", str(self.user.auth_id))
                .eq("organization_id", str(self.user.active_organization_id))
                .execute()
            )
            self.threads = [
                LlmConversationThreadModel(**data) for data in response.data
            ]



