from Cipher.core.event import Event, ChannelEvent, UserChannelEvent, ConnectingEvent, ConnectedEvent,\
    DisconnectingEvent, DisconnectedEvent, MessageChannelEvent, ChannelSendMessageEvent, MessageUserEvent, UserEvent,\
    SendMessageEvent


class DiscordEvent(Event):
    event_type = "discord"


class DiscordConnectingEvent(DiscordEvent, ConnectingEvent):
    pass


class DiscordConnectedEvent(DiscordEvent, ConnectedEvent):
    pass


class DiscordDisconnectingEvent(DiscordEvent, DisconnectingEvent):
    pass


class DiscordDisconnectedEvent(DiscordEvent, DisconnectedEvent):
    pass


class DiscordChannelEvent(DiscordEvent, ChannelEvent):
    pass


class DiscordUserChannelEvent(DiscordChannelEvent, UserChannelEvent):
    pass


class DiscordMessageChannelEvent(DiscordUserChannelEvent, MessageChannelEvent):
    pass


class DiscordUserEvent(DiscordEvent, UserEvent):
    pass


class DiscordMessageUserEvent(DiscordUserEvent, MessageUserEvent):
    pass


class DiscordSendMessageEvent(DiscordEvent, SendMessageEvent):
    pass


class DiscordChannelSendMessageEvent(DiscordSendMessageEvent, ChannelSendMessageEvent):
    pass
