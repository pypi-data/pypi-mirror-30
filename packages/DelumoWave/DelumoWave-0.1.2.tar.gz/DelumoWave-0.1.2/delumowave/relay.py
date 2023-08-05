#!/usr/bin/env python3

import logging
from typing import Union

from delumowave.controller import DelumoWaveController, hex_repr
from delumowave.config.relay import (RELAY, BRIGHTNESS, STATE, DIMMING_STEP)

_LOGGER = logging.getLogger(__name__)


class DelumoWaveRelay(DelumoWaveController):
    def __init__(self,
                 node_addr: Union[bytes, list, tuple],
                 node_version: int = max(RELAY, key=int),
                 port_path: str = '/dev/ttyUSB0',
                 unlock_timeout: float = 5.0,
                 sleep_time: float = 0.1,
                 block: bool = False,
                 logging_level: Union[str, int, None] = None):
        """
        This class provide methods to manage relay/dimmer.

        Parameters
        ----------
        node_addr : Union[bytes, list, tuple]
            Node address. Three latest meaningful bytes. For example:
            ``b'\\x12\\xA7\\xE4'``, ``[173, 34, 211]``, ``[0x7A, 0x19, 0xF0]``.
        node_version : int
            Node firmware version. One byte from 0x00 to 0xFF.
            By default, latest available firmware version.
        port_path : str, optional
            Device name: depending on operating system. e.g. ``/dev/ttyUSB0``,
            ``/dev/ttyAMA0`` on GNU/Linux or ``COM3`` on Windows.
            By default, ``/dev/ttyAMA0`` is used.
        unlock_timeout : float
        sleep_time : float
        block : float
        logging_level : Union[str, int, None], optional
            Available logging levels: ``DEBUG``, ``INFO``, ``WARNING``,
            ``ERROR``, ``CRITICAL``, ``NOTSET``. Also it could be written by
            numeric values.
            By default, logging is disabled.
        """

        if logging_level is None:
            _LOGGER.disabled = True
        elif isinstance(logging_level, str):
            if logging_level.upper() in ('DEBUG', 'INFO', 'WARNING', 'ERROR',
                                         'CRITICAL', 'NOTSET'):
                _LOGGER.setLevel(logging_level.upper())
        elif isinstance(logging_level, int):
            _LOGGER.setLevel(logging_level)
        else:
            _LOGGER.setLevel('ERROR')

        _LOGGER.debug(f'DelumoWaveRelay __init__() with Args: {{'
                      f'\'node_addr\': {hex_repr(node_addr)}, '
                      f'\'port_path\': {port_path}}}')

        super().__init__(port_path=port_path,
                         unlock_timeout=unlock_timeout,
                         sleep_time=sleep_time,
                         block=block,
                         logging_level=logging_level)

        self._node_version = node_version
        self._node_addr = node_addr

        #: Relay/dimmer constants for appropriate firmware version
        self.RELAY = RELAY[self._node_version]

    def invert(self) -> bool:
        """
        Invert state (``ON`` - 0x55 or ``OFF`` - 0xFF) of relay/dimmer

        Returns
        -------
        bool
            True if the command to invert state of relay/dimmer was
            successfully sent, False otherwise.
        """

        _LOGGER.debug('Calling invert()')

        try:
            return self.send_cmd(node_addr=self._node_addr,
                                 procedure=self.RELAY['PROCEDURE']['SWITCH_INVERSION'])
        except KeyError as ex:
            _LOGGER.error(f'{ex} is not supported for '
                          f'{hex_repr(self._node_version)} relay/dimmer '
                          f'firmware version. ', exc_info=True)
            return False
        # except Exception as ex:
        #     _LOGGER.exception(ex, exc_info=True)

    def relay_on(self) -> bool:
        """
        Switch on relay/dimmer by executing command with procedure ``SWITCH_ON``

        Returns
        -------
        bool
            True if the command to switch on relay/dimmer was successfully sent,
            False otherwise.
        """

        _LOGGER.debug('Calling relay_on()')

        try:
            return self.send_cmd(node_addr=self._node_addr,
                                 procedure=self.RELAY['PROCEDURE']['SWITCH_ON'])
        except KeyError as ex:
            _LOGGER.error(f'{ex} is not supported for '
                          f'{hex_repr(self._node_version)} relay/dimmer '
                          f'firmware version. ', exc_info=True)
            return False

    def relay_off(self) -> bool:
        """
        Switch off relay/dimmer by executing command with procedure
        ``SWITCH_OFF``

        Returns
        -------
        bool
            True if the command to switch off relay/dimmer was successfully
            sent, False otherwise.
        """

        _LOGGER.debug('Calling relay_off()')

        try:
            return self.send_cmd(node_addr=self._node_addr,
                                 procedure=self.RELAY['PROCEDURE']['SWITCH_OFF'])
        except KeyError as ex:
            _LOGGER.error(f'{ex} is not supported for '
                          f'{hex_repr(self._node_version)} relay/dimmer '
                          f'firmware version. ', exc_info=True)
            return False

    def dimmer_on(self) -> bool:
        """
        Switch on dimmer by writing state to EEPROM
        """

        _LOGGER.debug('Dimmer on')

        return self.send_cmd(node_addr=self._node_addr,
                             procedure=self.RELAY['PROCEDURE']['GLOBAL_ON'])

    def dimmer_off(self) -> bool:
        """
        Switch off dimmer by writing state to EEPROM
        """

        _LOGGER.debug('Dimmer off')

        return self.send_cmd(node_addr=self._node_addr,
                             procedure=self.RELAY['PROCEDURE']['GLOBAL_OFF'])

    @property
    def time_to_relay_off(self) -> int:
        """
        Get time to relay/dimmer off in hours
        """

        _LOGGER.debug('Get time to relay off')
        time_to_relay_off = self.read(node_addr=self._node_addr,
                                      eeprom_addr=self.RELAY['EEPROM']['TIME_RELAY_OFF'],
                                      data_size=0x01)[0]
        _LOGGER.debug(f'Time to relay off -> {hex_repr(time_to_relay_off)}')

        return time_to_relay_off

    @time_to_relay_off.setter
    def time_to_relay_off(self, time_in_hours: int):
        """
        Set time to relay/dimmer off in hours
        """

        _LOGGER.debug(f'Set time to relay off {time_in_hours}')
        status = self.write(node_addr=self._node_addr,
                            eeprom_addr=self.RELAY['EEPROM']['TIME_RELAY_OFF'],
                            data=time_in_hours)
        _LOGGER.debug(f'Time to relay off -> {hex_repr(time_in_hours)}. '
                      f'{"OK!" if status else "Failed!"}')

    @property
    def hardware_type(self) -> int:
        """
        Get hardware type of node (relay or dimmer)
        """

        _LOGGER.debug('Get hardware type')
        hardware_type = self.read(node_addr=self._node_addr,
                                  eeprom_addr=self.RELAY['EEPROM']['HARDWARE_TYPE'],
                                  data_size=0x01)[0]
        _LOGGER.debug(f'Relay hardware type -> {hex_repr(hardware_type)}')

        return hardware_type

    @hardware_type.setter
    def hardware_type(self, hardware_type):
        """
        Set hardware type of node (relay or dimmer)
        """

        _LOGGER.debug(f'Set hardware type {hardware_type}')
        self.write(node_addr=self._node_addr,
                   eeprom_addr=self.RELAY['EEPROM']['HARDWARE_TYPE'],
                   data=hardware_type)
        _LOGGER.debug(f'Relay hardware type -> {hex_repr(hardware_type)}')

    @property
    def firmware_version(self) -> int:
        """
        Get firmware version of node
        """

        _LOGGER.debug('Get firmware version')
        firmware_version = self.read(node_addr=self._node_addr,
                                     eeprom_addr=self.RELAY['EEPROM']['FIRMWARE_VERSION'],
                                     data_size=0x01)[0]
        _LOGGER.debug(f'Relay firmware version -> {hex_repr(firmware_version)}')

        return firmware_version

    @firmware_version.setter
    def firmware_version(self, firmware_version):
        """
        Set firmware version of node
        """

        _LOGGER.debug('Get firmware version')
        self.write(
            node_addr=self._node_addr,
            eeprom_addr=self.RELAY['EEPROM']['FIRMWARE_VERSION'],
            data=firmware_version)
        _LOGGER.debug(f'Relay firmware version -> {hex_repr(firmware_version)}')

    @property
    def state(self) -> bool:
        """
        Get state of node - on (0x55) or off (0xFF)
        """

        _LOGGER.debug('Get state')
        state_byte = self.read(node_addr=self._node_addr,
                               eeprom_addr=self.RELAY['EEPROM']['STATE'],
                               data_size=0x01)[0]
        _LOGGER.debug(f'Relay state -> {hex_repr(state_byte)}')
        state = next((x for x, y in STATE.items() if y == state_byte), None)
        _LOGGER.debug(f'Relay state -> {state}')

        return state

    @state.setter
    def state(self, state: bool):
        """
        Set state of node - ON (0x55) or OFF (0xFF)
        """

        _LOGGER.debug(f'Set state {state}')
        state_byte = STATE[state]
        self.write(node_addr=self._node_addr,
                   eeprom_addr=self.RELAY['EEPROM']['STATE'],
                   data=state_byte)
        _LOGGER.debug(f'Relay state -> {state} ({state_byte})')

    @property
    def brightness_level(self) -> int:
        """
        Get brightness level of dimmer
        """

        _LOGGER.debug('Get brightness_level')
        brightness_level = self.read(node_addr=self._node_addr,
                                     eeprom_addr=self.RELAY['EEPROM']['BRIGHTNESS_LEVEL'],
                                     data_size=0x01)[0]
        _LOGGER.debug(f'Relay brightness level -> {hex_repr(brightness_level)}')

        return brightness_level

    @brightness_level.setter
    def brightness_level(self, brightness_level: int):
        """
        Set brightness level of dimmer
        """

        _LOGGER.debug(f'Set brightness_level {brightness_level}')
        if brightness_level > BRIGHTNESS['MAX']:
            brightness_level = BRIGHTNESS['MAX']
        if brightness_level < BRIGHTNESS['MIN']:
            brightness_level = BRIGHTNESS['MIN']

        self.write(node_addr=self._node_addr,
                   eeprom_addr=self.RELAY['EEPROM']['BRIGHTNESS_LEVEL'],
                   data=brightness_level)
        _LOGGER.debug(f'Relay brightness level -> {hex_repr(brightness_level)}')

    @property
    def brightness_level_comfort(self) -> int:
        """
        Get brightness level comfort of dimmer
        """

        _LOGGER.debug('Get brightness level comfort')
        brightness_level_comfort = self.read(node_addr=self._node_addr,
                                             eeprom_addr=self.RELAY['EEPROM']['BRIGHTNESS_LEVEL_COMFORT'],
                                             data_size=0x01)[0]
        _LOGGER.debug(f'Relay brightness level comfort -> {hex_repr(brightness_level_comfort)}')

        return brightness_level_comfort

    @brightness_level_comfort.setter
    def brightness_level_comfort(self, brightness_level_comfort: int):
        """
        Set brightness level comfort of dimmer
        """

        _LOGGER.debug(f'Set brightness level comfort {brightness_level_comfort}')
        if brightness_level_comfort > BRIGHTNESS['MAX']:
            brightness_level_comfort = BRIGHTNESS['MAX']
        if brightness_level_comfort < BRIGHTNESS['MIN']:
            brightness_level_comfort = BRIGHTNESS['MIN']

        self.write(node_addr=self._node_addr,
                   eeprom_addr=self.RELAY['EEPROM']['BRIGHTNESS_LEVEL_COMFORT'],
                   data=brightness_level_comfort)
        _LOGGER.debug(f'Relay brightness level comfort -> {hex_repr(brightness_level_comfort)}')

    @property
    def dimming_speed(self) -> int:
        """
        Get dimming speed
        """

        _LOGGER.debug('Get dimming speed')
        dimming_speed = self.read(node_addr=self._node_addr,
                                  eeprom_addr=self.RELAY['EEPROM']['DIMMING_SPEED'],
                                  data_size=0x01)[0]
        _LOGGER.debug(f'Relay dimming speed -> {hex_repr(dimming_speed)}')

        return dimming_speed

    @dimming_speed.setter
    def dimming_speed(self, dimming_speed: int):
        """
        Set dimming speed
        """

        _LOGGER.debug(f'Set dimming speed {dimming_speed}')
        self.write(node_addr=self._node_addr,
                   eeprom_addr=self.RELAY['EEPROM']['DIMMING_SPEED'],
                   data=dimming_speed)
        _LOGGER.debug(f'Relay dimming speed -> {hex_repr(dimming_speed)}')

    @property
    def dimming_step(self) -> int:
        """
        Get dimming step
        """

        _LOGGER.debug('Get dimming step')
        dimming_step = self.read(node_addr=self._node_addr,
                                 eeprom_addr=self.RELAY['EEPROM']['DIMMING_STEP'],
                                 data_size=0x01)[0]
        _LOGGER.debug(f'Relay dimming step -> {hex_repr(dimming_step)}')

        return dimming_step

    @dimming_step.setter
    def dimming_step(self, dimming_step: int):
        """
        Set dimming step
        """

        _LOGGER.debug(f'Set dimming step {dimming_step}')
        if dimming_step > DIMMING_STEP['MAX']:
            dimming_step = DIMMING_STEP['MAX']
        if dimming_step < DIMMING_STEP['MIN']:
            dimming_step = DIMMING_STEP['MIN']

        self.write(node_addr=self._node_addr,
                   eeprom_addr=self.RELAY['EEPROM']['DIMMING_STEP'],
                   data=dimming_step)
        _LOGGER.debug(f'Relay dimming step -> {hex_repr(dimming_step)}')
