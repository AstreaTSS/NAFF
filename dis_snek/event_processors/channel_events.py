import logging

from dis_snek.const import logger_name
from dis_snek.event_processors._template import EventMixinTemplate
from dis_snek.models import listen, events, Invite
from dis_snek.models.events import RawGatewayEvent
from dis_snek.utils.converters import timestamp_converter

log = logging.getLogger(logger_name)


class ChannelEvents(EventMixinTemplate):
    @listen()
    async def _on_raw_channel_create(self, event: RawGatewayEvent) -> None:

        channel = self.cache.place_channel_data(event.data)
        self.dispatch(events.ChannelCreate(channel))

    @listen()
    async def _on_raw_channel_delete(self, event: RawGatewayEvent) -> None:
        # for some reason this event returns the deleted object?
        # so we cache it regardless
        channel = self.cache.place_channel_data(event.data)
        self.dispatch(events.ChannelDelete(channel))

    @listen()
    async def _on_raw_channel_update(self, event: RawGatewayEvent) -> None:
        channel = self.cache.place_channel_data(event.data)
        self.dispatch(events.ChannelUpdate(channel))

    @listen()
    async def _on_raw_channel_pins_update(self, event: RawGatewayEvent) -> None:
        channel = await self.cache.get_channel(event.data.get("channel_id"))
        channel.last_pin_timestamp = timestamp_converter(event.data.get("last_pin_timestamp"))
        self.cache.channel_cache[channel.id] = channel
        self.dispatch(events.ChannelPinsUpdate(channel, channel.last_pin_timestamp))

    @listen()
    async def _on_raw_invite_create(self, event: RawGatewayEvent) -> None:
        self.dispatch(events.InviteCreate(Invite.from_dict(event.data, self)))  # type: ignore

    @listen()
    async def _on_raw_invite_delete(self, event: RawGatewayEvent) -> None:
        self.dispatch(events.InviteDelete(Invite.from_dict(event.data, self)))  # type: ignore