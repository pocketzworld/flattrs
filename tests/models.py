from enum import IntEnum
from typing import List, Optional, Union

import attr

from flattr import UNION_CL, Flatbuffer, FlatbufferEnum

from tests.fbs.clothing.ClothingEntity import ClothingEntity
from tests.fbs.clothing.ClothingEntityList import ClothingEntityList
from tests.fbs.user.Privilege import Privilege
from tests.fbs.user.User import User
from tests.fbs.inbox.Conversation import Conversation
from tests.fbs.inbox.ConversationType import ConversationType
from tests.fbs.inbox.Message import Message
from tests.fbs.inbox.MessageType import MessageType
from tests.fbs.networking.socket.inbox.GetConversationsResponse import (
    GetConversationsResponse
)
from tests.fbs.networking.socket.inbox.GetMessagesResponse import (
    GetMessagesResponse
)
from tests.fbs.networking.socket.inbox.SendMessageRequest import (
    SendMessageRequest
)
from tests.fbs.networking.socket.inbox.SendMessageResponse import (
    SendMessageResponse
)
from tests.fbs.networking.socket.inbox.ConversationUpdateResponse import (
    ConversationUpdateResponse
)
from tests.fbs.networking.socket.inbox.ServerContent import ServerContent
from tests.fbs.networking.socket.inbox.AnyServerContent import AnyServerContent
from tests.fbs.networking.socket.inbox.ClientContent import ClientContent
from tests.fbs.networking.socket.inbox.AnyClientContent import AnyClientContent
from tests.fbs.networking.socket.inbox.ConversationUpdateRequest import (
    ConversationUpdateRequest
)
from tests.fbs.networking.socket.inbox.GetConversationsRequest import (
    GetConversationsRequest
)
from tests.fbs.networking.socket.inbox.GetMessagesRequest import (
    GetMessagesRequest
)
from tests.flattrs_test.JustAFloat import JustAFloat
from tests.flattrs_test.JustADouble import JustADouble
from tests.flattrs_test.JustAString import JustAString
from tests.flattrs_test.JustAnOptionalString import JustAnOptionalString
from tests.flattrs_test.ListOfStrings import ListOfStrings


@Flatbuffer(JustAString)
class JustAString:
    id: str = attr.ib()


@Flatbuffer(JustAnOptionalString)
class JustAnOptionalString:
    id: Optional[str] = attr.ib()


@Flatbuffer(JustAFloat)
class JustAFloat:
    value: float = attr.ib()


@Flatbuffer(JustADouble)
class JustADouble:
    value: float = attr.ib()


@Flatbuffer(ListOfStrings)
class ListOfStrings:
    content: List[str] = attr.ib()


@Flatbuffer(ClothingEntity)
class ClothingEntity:
    descriptorId: str = attr.ib()
    descriptorVersion: int = attr.ib()
    activePalette: int = attr.ib()

    @classmethod
    def from_mongo(cls, val):
        return cls(
            descriptHallstattorId=val["item_id"],
            descriptorVersion=0,
            activePalette=val["active_palette"],
        )


@Flatbuffer(ClothingEntityList)
class ClothingEntityList:
    entities: List[ClothingEntity] = attr.ib()

    @classmethod
    def from_mongo(cls, val):
        return cls([ClothingEntity.from_mongo(i) for i in val])


@FlatbufferEnum(Privilege)
class Privilege(IntEnum):
    NotRegistered = 0
    Normal = 1
    Normal2 = 2
    Admin = 3
    Moderator = 4
    Moderator2 = 5
    Moderator3 = 6
    Verified = 7
    Banned = 8

    @classmethod
    def from_string(cls, val):
        m = {"not_registered": cls.NotRegistered, "normal": cls.Normal}
        return m[val]


@Flatbuffer(User)
class User:
    id: str = attr.ib()
    username: str = attr.ib()
    equipped: ClothingEntityList = attr.ib()
    emailAddress: Optional[str] = attr.ib()
    phoneNumber: Optional[str] = attr.ib()
    privilege: Privilege = attr.ib()
    isNewsfeedPrivate: bool = attr.ib()
    lastActiveIn: int = attr.ib()
    vipSecondsLeft: int = attr.ib()

    @classmethod
    def from_mongo(cls, val):
        return cls(
            str(val["_id"]),
            val["username"],
            ClothingEntityList.from_mongo(
                val["equipped_avatar_items_hash"]["items"]
            ),
            None,
            None,
            Privilege.from_string(val["privilege_level"]),
            val["settings"].get("ios_newsfeed_private", False),
            int(val["last_activity_at"].timestamp()),
            vipSecondsLeft=0,
        )


@FlatbufferEnum(MessageType)
class MessageType(IntEnum):
    Text = 0
    Trade = 1
    Image = 2
    UserModified = 3


@Flatbuffer(Message)
class Message:
    id: str = attr.ib()
    content: str = attr.ib()
    senderId: str = attr.ib()
    type: MessageType = attr.ib()

    @classmethod
    def from_mongo(cls, val):
        return cls(
            id=str(val["_id"]),
            content=val["content"],
            senderId=str(val["sender_id"]),
            type=MessageType.Text,
        )


@FlatbufferEnum(ConversationType)
class ConversationType(IntEnum):
    Normal = 0
    Support = 1
    Crew = 2
    CrewInvite = 3


@Flatbuffer(Conversation)
class Conversation:
    id: str = attr.ib()
    type: ConversationType = attr.ib()
    didJoin: bool = attr.ib()
    hasActiveTrade: bool = attr.ib()
    unreadCount: int = attr.ib()
    recentMembers: List[User] = attr.ib()
    memberCount: int = attr.ib()
    lastMessage: Message = attr.ib()

    @classmethod
    def from_mongo(cls, val, didJoin=False, num_unread=0, recentMembers=None):
        return cls(
            str(val["_id"]),
            ConversationType.Normal,
            didJoin,
            False,
            num_unread,
            [] if recentMembers is None else recentMembers,
            len(val["user_info"]),
            Message.from_mongo(val["last_message"]),
        )


@Flatbuffer(ConversationUpdateResponse)
class ConversationUpdateResponse:
    conversation: Conversation = attr.ib()


@Flatbuffer(GetConversationsResponse)
class GetConversationsResponse:
    conversations: List[Conversation] = attr.ib()


@Flatbuffer(GetMessagesResponse)
class GetMessagesResponse:
    messages: List[Message] = attr.ib()
    members: List[User] = attr.ib()


@Flatbuffer(SendMessageResponse)
class SendMessageResponse:
    message: Message = attr.ib()


@Flatbuffer(ServerContent)
class ServerContent:
    content: Union[
        ConversationUpdateResponse,
        GetConversationsResponse,
        GetMessagesResponse,
        SendMessageResponse,
    ] = attr.ib(metadata={UNION_CL: AnyServerContent})


@Flatbuffer(ConversationUpdateRequest)
class ConversationUpdateRequest:
    conversationId: str = attr.ib()


@Flatbuffer(GetConversationsRequest)
class GetConversationsRequest:
    lastConversationId: Optional[str] = attr.ib()


@Flatbuffer(GetMessagesRequest)
class GetMessagesRequest:
    conversationId: str = attr.ib()
    lastMessageId: Optional[str] = attr.ib()


@Flatbuffer(SendMessageRequest)
class SendMessageRequest:
    conversationId: str = attr.ib()
    message: Message = attr.ib()


@Flatbuffer(ClientContent)
class ClientContent:
    content: Union[
        ConversationUpdateRequest,
        GetConversationsRequest,
        GetMessagesRequest,
        SendMessageRequest,
    ] = attr.ib(metadata={UNION_CL: AnyClientContent})
