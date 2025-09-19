from __future__ import annotations

import logging

import voluptuous as vol
from homeassistant import config_entries, core
from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
    RepeatMode,
)
from homeassistant.const import CONF_NAME
from homeassistant.helpers import (
    config_validation as cv,
    entity_platform,
)
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN, SERVICE_SEND_COMMAND, CONF_BROADLINK

_LOGGER = logging.getLogger(__name__)

COMMANDS = {
    "disp": "JgAsADkgGj04Pjc+OB8cIBo8GiAcIBsAC2U3IBs+Nz06OzkgGiAbPRsfGyAbAA0FAAAAAAAAAAAAAAAA",
    "one": "JgAwABofGyAcHzg8OD05IBogGiAbIBo9GQALaBoeHh4cHzo7Nz45HxogGyAaHxs/GgANBQAAAAAAAAAA",
    "two": "JgAsABshOTs4PTo7OR4cIRgiGj04AAZ4CgAFARsgNzo8PTc9OSEZIBsgGj04AA0FAAAAAAAAAAAAAAAA",
    "three": "JgAwAB0fGSIZHzo8OT04HxsgGh8aPxwgGgALZBwfGiAcHzg9OD03IRsfGyAaPRkiGgANBQAAAAAAAAAA",
    "four": "JgAoABsgOTw5PDg+OB8cIBo9NyAbAAuDGyA3Pjg+Nj05IBogGj83IBoADQU=",
    "five": "JgAsABsgHB4bIDc9OT43IBogGz43PhwAC2McHxsfGyA4PDk+NyAbIBo9OD0bAA0FAAAAAAAAAAAAAAAA",
    "six": "JgAsABwfHCAaHzk8OT05HxsfGzwcIDcAC4MbHxohHB83PTg+OB8bIBs+Gh84AA0FAAAAAAAAAAAAAAAA",
    "seven": "JgAsABogNz83Pjc9OSAdHhs7GyAbIBsAC2UbHzg+Nz45OzkfGyAZPhshGiAaAA0FAAAAAAAAAAAAAAAA",
    "eight": "JgAwABsfGyAcHjg+Nz44Hxs9NyEbIBoAC4IcIBohGSA4PTg+NyAbPjkdHB8bAAc3BwANBQAAAAAAAAAA",
    "nine": "JgAoABogODw6Ozs7OCAaPTofGj0cAAtlGyA3Pjg9Nz42Iho+NyAaPR0ADQU=",
    "zero": "JgAwABwhGh8cHjw6Nz44IBogGx8bHxsgGwALgxofGyEbHjg9OD05IhkjFyAbIBkgGwANBQAAAAAAAAAA",
    "preset": "JgAoABohNzw6PDk8OR8aPRsgGx84AAuEGiA5PDg9OD44IBk+GyAaIDUADQU=",
    "store": "JgAWABwgGx4bITU+OD8ZIjc8OCEbPRsADQUAAA==",
    "vol+": "JgA0AAkACCgdHzg9NyAbIRkgHB8ZPjkfGiAbIBoAC4QdHTk9Nx8bIBohGx8bPzQjGR0eHxsADQUAAAAA",
    "vol-": "JgA4ABshGx8aITkeGh8cIBkjGD44HxsfGz4aAAtnGh8bIRkhNiEaIBwgFyMaPjcgGiEZPRwAAvoKAA0F",
    "mute": "JgAwABsgODw6HxogGx8bHxohGzwcIDY/GgALZhsgOTs4IRogGiAbIBofHDwcHzg+GgANBQAAAAAAAAAA",
    "ok": "JgAUADk8HCA4PTc+Nz45PBsgGx8bAA0FAAAAAA==",
    "up": "JgAoADchGz44PTc9OTw6HhsgGx8bAAuEOB8bPDg+OT04PDsdGyAaIBoADQU=",
    "down": "JgAoADc9HB84PTg9OD04IRsfGT4bAAtlOT0bITY+ODw5PTodGyAcPBwADQU=",
    "left": "JgAkADggHDs5PTg+OD04PDk9GwALZjcgGzw6PDg9OD43PTk9GwANBQAAAAA=",
    "right": "JgASADc/Gx83Pjg8OT05PBsfOQANBQAAAAAAAA==",
    "exit": "JgAoADofGT44Pjc7Ozw5IBo+GiEZAAtmOCAbPDo8OD43PjcgGzwgHB0ADQU=",
    "repeat": "JgAsABsgGiEaIDg9ODw5PBwgGiA4PRwAC2QbHxsgHB83PTk9Nj8bIRkgNz4cAA0FAAAAAAAAAAAAAAAA",
    "shuffle": "JgAsABsgNz05PDk8HCAbHxogOB8bIBsAC4MbIDc+Nz05PRshGh8bHzghGSAbAA0FAAAAAAAAAAAAAAAA",
    "setup": "JgAkADo7HCA3PTk8Ojs6OzofGgALgzk8HB84Pjc9Ojs5PDkfGwANBQAAAAA=",
    "info": "JgAsABoiODs5PTg9OR8bPRshGSAbHxwAC2QbHzk9Ojs4PTkfHDwcHxsfGx8cAA0FAAAAAAAAAAAAAAAA",
    "play": "JgAsABsgGyAaHzg9OT0aIBwhNj05OxwAC2UcHhweHR82Pjk8GyAbIDc+OD0bAA0FAAAAAAAAAAAAAAAA",
    "previous": "JgAwABogGx8cHzg8NzohHzgfHB8aIBw7HAALZhogGh8cIDc+OTwaITcgGh8cIBw8GQANBQAAAAAAAAAA",
    "next": "JgAsABweOT03Pjc+GyA3IBsgGx8aHx0AC4IbIDg9OD05PBsgOR8aIBogGiAbAA0FAAAAAAAAAAAAAAAA",
    "stop": "JgAsABogGx8bHzs4Oj0cIBogNz4bHzkAC4MbHxsfGyA3Pjk7HCAaIDc9Gx85AA0FAAAAAAAAAAAAAAAA",
    "rewind": "JgAoABogODw5PDo9GSEaHzkgGT84AAuCGyA4Pjg9OD0bHxsfOSAZPTkADQU=",
    "fastforward": "JgAsABwgGh8bIDg9ODwcHxwfOD05HhwAC4IdHxogGx84PTg+Gx8bHzg9OR8cAA0FAAAAAAAAAAAAAAAA",
    "cd": "JgAkABwgNUA3PTk8Nz84Pjg9GwALZRsgNjw6Pjk7OT04Pjg9HAANBQAAAAA=",
    "radio": "JgAoAB0eGh8cHzk8OD04PTg9OSEZAAuDGx8cHx0eODw6PDg8OT04IBoADQU=",
    "pc": "JgAsABwgOD04PTg9GiEbHhwfGyE2PRoAC2YcIDg+OTs4PB0eGx8bIRogOTwZAA0FAAAAAAAAAAAAAAAA",
    "ipod": "JgAsADg9HR45PDg9OR4bIRsfGzwbHxsAC2Y4PhogOD04PTggGiAbIRo8GyEbAA0FAAAAAAAAAAAAAAAA",
    "tv": "JgAoADggGj05PDk9OSAZIBs9OCAbAAuAOiAcPDg+Nz82IRweGT83IBwADQU=",
    "av": "JgAoADk9HB84PTg8OSAaIBw7OD4ZAAtoNz0bIDg9OD02JBkgGz04OR4ADQU=",
    "hdd": "JgAoADggGz04PTc+OCAdHho+Gx44AAuEOR8aPTg+Nz42IhsgGT4aIDkADQU=",
    "aux": "JgAsABsfGSEcIDY+OD4aHzggGyAaPTkAC4IcHhwgGiA2QDVAGiA4HxshGT45AA0FAAAAAAAAAAAAAAAA",
}

SUPPORT_NDX = (
    MediaPlayerEntityFeature.PAUSE
    | MediaPlayerEntityFeature.PREVIOUS_TRACK
    | MediaPlayerEntityFeature.NEXT_TRACK
    | MediaPlayerEntityFeature.PLAY_MEDIA
    | MediaPlayerEntityFeature.PLAY
    | MediaPlayerEntityFeature.STOP
    | MediaPlayerEntityFeature.REPEAT_SET
    | MediaPlayerEntityFeature.SELECT_SOURCE
    | MediaPlayerEntityFeature.SHUFFLE_SET
)

SOURCES = ("CD", "Radio", "PC", "iPod", "TV", "AV", "HDD", "Aux")


async def async_setup_entry(
    hass: core.HomeAssistant,
    config_entry: config_entries.ConfigEntry,
    async_add_entities,
) -> None:
    async_add_entities(
        [
            NDXDevice(
                hass, config_entry.data[CONF_NAME], config_entry.data[CONF_BROADLINK]
            )
        ]
    )

    # Register entity services
    platform = entity_platform.async_get_current_platform()
    platform.async_register_entity_service(
        SERVICE_SEND_COMMAND,
        {
            vol.Required("command"): cv.string,
        },
        NDXDevice.send_command.__name__,
    )


class NDXDevice(MediaPlayerEntity):
    # Representation of a Emotiva Processor

    def __init__(self, hass, name, broadlink_entity):
        self._hass = hass
        self._state = MediaPlayerState.IDLE
        self._entity_id = "media_player.naim_ndx"
        self._unique_id = "naim_ndx_" + name.replace(" ", "_").replace(
            "-", "_"
        ).replace(":", "_")
        self._device_class = "receiver"
        self._name = name
        self._broadlink_entity = broadlink_entity
        self._source = ""
        self._sources = SOURCES
        self._shuffle = False

    @property
    def should_poll(self):
        return False

    @property
    def icon(self):
        return "mdi:disc"

    @property
    def state(self) -> MediaPlayerState:
        return self._state

    @property
    def name(self):
        # return self._device.name
        return None

    @property
    def has_entity_name(self):
        return True

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return DeviceInfo(
            identifiers={
                # Serial numbers are unique identifiers within a specific domain
                (DOMAIN, self._unique_id)
            },
            name=self._name,
            manufacturer="Naim",
            model="NDX",
        )

    @property
    def source_list(self):
        return self._sources

    @property
    def source(self):
        return self._source

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def entity_id(self):
        return self._entity_id

    @property
    def device_class(self):
        return self._device_class

    @entity_id.setter
    def entity_id(self, entity_id):
        self._entity_id = entity_id

    @property
    def supported_features(self) -> MediaPlayerEntityFeature:
        return SUPPORT_NDX

    @property
    def repeat(self):
        return RepeatMode.ONE

    @property
    def shuffle(self) -> bool:
        """Boolean if shuffle is enabled."""
        return self._shuffle

    async def send_command(self, command):
        await self._send_broadlink_command(command)

    async def _send_broadlink_command(self, command):
        await self._hass.services.async_call(
            "remote",
            "send_command",
            {
                "entity_id": self._broadlink_entity,
                "num_repeats": "1",
                "delay_secs": "0.4",
                "command": f"b64:{COMMANDS[command]}",
            },
        )

    async def async_set_repeat(self, repeat: RepeatMode) -> None:
        """Set the repeat mode."""
        if repeat == RepeatMode.ONE:
            await self._send_broadlink_command("repeat")
            self.async_schedule_update_ha_state()

    async def async_media_stop(self) -> None:
        """Send stop command to media player."""
        await self._send_broadlink_command("stop")
        self._state = MediaPlayerState.IDLE
        self.async_schedule_update_ha_state()

    async def async_media_play(self) -> None:
        """Send play command to media player."""
        await self._send_broadlink_command("play")
        self._state = MediaPlayerState.PLAYING
        self.async_schedule_update_ha_state()

    async def async_media_pause(self) -> None:
        """Send pause command to media player."""
        await self._send_broadlink_command("pause")
        self._state = MediaPlayerState.PAUSED
        self.async_schedule_update_ha_state()

    async def async_media_next_track(self) -> None:
        """Send next track command."""
        await self._send_broadlink_command("next")

    async def async_media_previous_track(self) -> None:
        """Send next track command."""
        await self._send_broadlink_command("previous")

    async def async_select_source(self, source: str) -> None:
        await self._send_broadlink_command(source.lower())

    async def async_set_shuffle(self, shuffle: bool) -> None:
        """Enable/disable shuffle mode."""
        self._shuffle = not self._shuffle
        await self._send_broadlink_command("shuffle")
        await self.coordinator.async_refresh()
