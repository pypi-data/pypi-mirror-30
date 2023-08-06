#!/usr/bin/env python3

import logging
import errno
from time import time, sleep
from typing import Union, Optional

import serial
from serial import SerialException

from delumowave.config.delumo import (DEVICE, COMMAND, EEPROM_SIZE)

_LOGGER = logging.getLogger(__name__)


class NodeAddrError(ValueError):
    def __init__(self, node_addr, msg=None):
        if msg is None:
            msg = f'Node address: {node_addr} -  must be {bytes}, {list} or ' \
                  f'{tuple}, must have size 3, and each item must be {int} ' \
                  f'in range [0x00, 0xFF]'
        super().__init__(msg)


class NodeVersionError(ValueError):
    def __init__(self, node_version, msg=None):
        if msg is None:
            msg = f'Node version: {node_version} - must be {int} in range ' \
                  f'[0x00, 0xFF]'
        super().__init__(msg)


class ProcedureError(ValueError):
    def __init__(self, procedure, msg=None):
        if msg is None:
            msg = f'Procedure: {procedure} - must be {int} in range [0x00, 0xFF]'
        super().__init__(msg)


class DataLengthError(ValueError):
    def __init__(self, data_length, msg=None):
        if msg is None:
            msg = f'Data length: {data_length} -  must be {int} in range ' \
                  f'[0x00, 0xFF]'
        super().__init__(msg)


class EEPROMAddrError(ValueError):
    def __init__(self, eeprom_addr, msg=None):
        if msg is None:
            msg = f'EEPROM address: {eeprom_addr} - must be {int} in range ' \
                  f'[0x00, 0xFF]'
        super().__init__(msg)


class EEPROMDataError(ValueError):
    def __init__(self, eeprom_data, msg=None):
        if msg is None:
            msg = f'EEPROM data: {eeprom_data} - must be {bytes}, {list}, ' \
                  f'{tuple} and each item must be {int} in range [0x00, 0xFF]' \
                  f' or single {int} in range [0x00, 0xFF]. And EEPROM data ' \
                  f'must not be out of EEPROM.'
        super().__init__(msg)


class RequestError(ValueError):
    def __init__(self, request, msg=None):
        if msg is None:
            msg = f'Request: {request} - must be {bytes}, {list} or {tuple} ' \
                  f'and each item must be {int} in range [0x00, 0xFF]'
        super().__init__(msg)


class RequestLengthError(ValueError):
    def __init__(self, request_length, expected_request_length, msg=None):
        if msg is None:
            msg = f'Request length {request_length} is not equal expected ' \
                  f'request length {expected_request_length}'
        super().__init__(msg)


class ResponseError(ValueError):
    def __init__(self, response, msg=None):
        if msg is None:
            msg = f'Response: {response} - must be {bytes}, {list} or {tuple}' \
                  f' and each item must be {int} in range [0x00, 0xFF]'
        super().__init__(f'Response: {response} - ' + msg)


class RadioControllerBlocked(SerialException):
    def __init__(self, msg=None):
        if msg is None:
            msg = 'Radio controller is blocked by other process.'
        super().__init__(errno.EAGAIN, msg)


class NotSupportedError(KeyError):
    def __init__(self, msg=None):
        if msg is None:
            msg = 'Operation is not supported for this node firmware version.'
        super().__init__(msg)


def hex_repr(data: Union[int, bytes, list, tuple, set]) -> Optional[str]:
    """
    Get hexadecimal representation of data (single int digit or
    bytes, list of int, tuple of int, set of int). This function is used for
    pretty logging.

    Parameters
    ----------
    data : Union[int, bytes, list, tuple, set]
        Data that should be represented in hex.

    Returns
    -------
    str
        Depending on the input data type function returns value could be
        represented in string of single hex int or string of list of int.

    Examples
    --------
    If input data has ``int`` type

    >>> hex_repr(18)
    '0x12'

    If input data has ``bytes`` type

    >>> hex_repr(b'\\x12\\x23\\x34')
    '[0x12, 0x23, 0x34]'

    If input data has ``list`` type

    >>> hex_repr([18, 35, 52])
    '[0x12, 0x23, 0x34]'

    """

    if isinstance(data, (bytes, list, tuple, set)) and \
            all(isinstance(x, int) for x in data):
        return f'[{", ".join([f"{b:#04x}" for b in data])}]'
    elif isinstance(data, int):
        return f'{data:#04x}'
    else:
        return None


class DelumoWaveController:
    def __init__(self,
                 port_path: str = '/dev/ttyUSB0',
                 baudrate: int = 115200,
                 bytesize: int = serial.EIGHTBITS,
                 parity: int = serial.PARITY_NONE,
                 stopbits: int = serial.STOPBITS_ONE,
                 timeout: float = 3.0,
                 write_timeout: float = 3.0,
                 unlock_timeout: float = 5.0,
                 sleep_time: float = 0.1,
                 block: bool = False,
                 logging_level: Union[str, int, None] = None):
        """
        Base class for low-level communication with nodes. This class provide
        base methods to send command to nodes, read nodes' EEPROM and write to
        nodes' EEPROM via radio controller, connected by UART or USB.

        Parameters
        ----------
        port_path : str, optional
            Device name via which radio controller is connected: depending on
            operating system. e.g. ``/dev/ttyUSB0``, ``/dev/ttyAMA0``
            on GNU/Linux or ``COM3`` on Windows.
            By default, ``/dev/ttyAMA0`` is used.
        baudrate : int, optional
            Baud rate such as 9600 or 115200 etc. By default, 115200 is used.
        bytesize : int, optional
            Number of data bits. Possible values: ``FIVEBITS``, ``SIXBITS``,
            ``SEVENBITS``, ``EIGHTBITS``. By default, ``EIGHTBITS`` is used.
        parity : int, optional
            Enable parity checking. Possible values: ``PARITY_NONE``,
            ``PARITY_EVEN``, ``PARITY_ODD``, ``PARITY_MARK``, ``PARITY_SPACE``.
            By default, ``PARITY_NONE`` is used.
        stopbits : int, optional
            Number of stop bits. Possible values: ``STOPBITS_ONE``,
            ``STOPBITS_ONE_POINT_FIVE``, ``STOPBITS_TWO``.
            By default, ``STOPBITS_ONE`` is used.
        timeout : float, optional
            Set a read timeout value. By default, ``3.0`` is used.
        write_timeout : float, optional
            Set a write timeout value. By default, ``3.0`` is used.
        unlock_timeout : float, optional
            How long (in seconds) try to to open radio controller in case if it
            is blocked by other process. By default, 5 seconds.
        sleep_time : float, optional
            How often (in seconds) try to open radio controller in case if it is
            blocked by other process. By default, each 0.1 second.
        block : bool, optional
            Block radio controller and wait until a radio transmission and node
            processing are complete. By default, block is False.
        logging_level : Union[str, int, None], optional
            Available logging levels: ``DEBUG``, ``INFO``, ``WARNING``,
            ``ERROR``, ``CRITICAL``, ``NOTSET``. Also it could be written by
            numeric values.
            By default, logging is disabled.

        Raises
        ------
        ValueError
            Will be raised when parameter are out of range, e.g. baud rate,
            data bits.
        SerialException
            In case the device can not be found or can not be configured.

        See Also
        --------
        serial.serial_for_url : function to open serial port
        logging.setLevel : function to set logging level (see available
            constants).
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

        _LOGGER.debug(f'DelumoWaveController __init__() with Args: {locals()}')

        self._port_path = port_path
        self.__unlock_timeout = unlock_timeout
        self.__sleep_time = sleep_time
        self.__block = block
        self.__node_addr = None
        self.__procedure = None
        self.__node_version = None
        self.__request = None
        self.__request_length = None
        self.__expected_request_length = None
        self.__response = None
        self.__response_cmd = None
        self.__response_data = None
        self.__response_length = None
        self.__expected_response_length = None
        self.__eeprom_data_length = None
        self.__data_length = None
        self.__eeprom_addr = None
        self.__eeprom_data = None

        self._controller = serial.serial_for_url(url=port_path,
                                                 baudrate=baudrate,
                                                 bytesize=bytesize,
                                                 parity=parity,
                                                 stopbits=stopbits,
                                                 timeout=timeout,
                                                 write_timeout=write_timeout,
                                                 do_not_open=True,
                                                 exclusive=True)

        _LOGGER.info(f'Radio controller is ready: {self._controller}')

    @property
    def _node_addr(self) -> bytes:
        return self.__node_addr

    @_node_addr.setter
    def _node_addr(self, node_addr: Union[bytes, list, tuple]):
        if not isinstance(node_addr, (bytes, list, tuple)):
            raise NodeAddrError(node_addr)
        if not len(node_addr) == 3:
            raise NodeAddrError(node_addr)
        if not all((isinstance(x, int) and 0x00 <= x <= 0xFF) for x in node_addr):
            raise NodeAddrError(node_addr)

        self.__node_addr = bytes(node_addr)

    @property
    def _procedure(self) -> int:
        return self.__procedure

    @_procedure.setter
    def _procedure(self, procedure: int):
        if not isinstance(procedure, int):
            raise ProcedureError(procedure)
        elif not 0x00 <= procedure <= 0xFF:
            raise ProcedureError(procedure)

        self.__procedure = procedure

    @property
    def _node_version(self) -> int:
        return self.__node_version

    @_node_version.setter
    def _node_version(self, node_version: int):
        if not isinstance(node_version, int):
            raise NodeVersionError(node_version)
        elif not 0x00 <= node_version <= 0xFF:
            raise NodeVersionError(node_version)

        self.__node_version = node_version

    @property
    def _request(self) -> bytes:
        return self.__request

    @_request.setter
    def _request(self, request: Union[bytes, list, tuple]):
        if not isinstance(request, (bytes, list, tuple)):
            raise RequestError(request)
        if not all((isinstance(x, int) and 0x00 <= x <= 0xFF) for x in request):
            raise RequestError(request)

        self.__request = bytes(request)
        self.__expected_request_length = len(self._request)

        if request[4] == COMMAND['READ_EEPROM']:
            # If requested data length is 0x00, then it expected whole EEPROM
            # data from eeprom_addr to the end of EEPROM. Otherwise it expect
            # data_length bytes from addr_eemprom
            if self._data_length != 0x00:
                self.__eeprom_data_length = self._data_length
            else:
                self.__eeprom_data_length = EEPROM_SIZE - self._eeprom_addr

            #: Request length + requested data length + 1 byte of check sum
            self.__expected_response_length = self.__expected_request_length + self.__eeprom_data_length + 1

    @property
    def _request_length(self) -> int:
        return self.__request_length

    @_request_length.setter
    def _request_length(self, request_length: int):
        if request_length == self._expected_request_length:
            self.__request_length = request_length
        else:
            raise RequestLengthError(request_length,
                                     self._expected_request_length)

    @property
    def _response(self) -> bytes:
        return self.__response

    @_response.setter
    def _response(self, response: Union[bytes, list, tuple]):
        if not isinstance(response, (bytes, list, tuple)):
            raise ResponseError(response)
        if not all((isinstance(x, int) and 0x00 <= x <= 0xFF) for x in response):
            raise ResponseError(response)

        self.__response = bytes(response)
        self.__response_length = len(self._response)
        self.__response_cmd = self._response[:self._request_length]
        self.__response_data = self._response[self._request_length:]

        if self.__response_length != self._expected_response_length:
            # TODO: возможно ли другая причина исключения кроме времени?
            raise ResponseError(response,
                                f'Time is over! No enough data were getting! '
                                f'Response length is {self._response_length}, '
                                f'but should be '
                                f'{self._expected_response_length}.')

        # Check command part
        if self._checksum(self._response_cmd[:-1]) != self._response_cmd[-1] \
                or self._response[4] != COMMAND['RESPONSE'] \
                or self._response[:4] != self._request[:4] \
                or self._response_cmd[5:-1] != self._request[5:-1]:

            raise ResponseError(response, f'Response command part failed!')

        # Check data part
        if self._checksum(self._response_data[:-1]) != self._response_data[-1]:
            raise ResponseError(response,
                                f'Data checksum failed! Data checksum is '
                                f'{hex_repr(self._response_data[-1])}, but '
                                f'should be '
                                f'{hex_repr(self._checksum(self._response_data[:-1]))}.')

    @property
    def _response_length(self) -> int:
        return self.__response_length

    @property
    def _response_cmd(self) -> bytes:
        return self.__response_cmd

    @property
    def _response_data(self) -> bytes:
        return self.__response_data

    @property
    def _eeprom_data_length(self) -> int:
        return self.__eeprom_data_length

    @property
    def _expected_request_length(self) -> int:
        return self.__expected_request_length

    @property
    def _expected_response_length(self) -> int:
        return self.__expected_response_length

    @property
    def _data_length(self) -> int:
        return self.__data_length

    @_data_length.setter
    def _data_length(self, data_length: int):
        if isinstance(data_length, int) and 0x00 <= data_length <= 0xFF:
            self.__data_length = data_length
        elif not isinstance(data_length, int):
            raise DataLengthError(data_length)
        elif not 0x00 <= data_length <= 0xFF:
            raise DataLengthError(data_length)

    @property
    def _eeprom_addr(self) -> int:
        return self.__eeprom_addr

    @_eeprom_addr.setter
    def _eeprom_addr(self, eeprom_addr: int):
        if isinstance(eeprom_addr, int) and 0x00 <= eeprom_addr <= 0xFF:
            self.__eeprom_addr = eeprom_addr
        elif not isinstance(eeprom_addr, int):
            raise EEPROMAddrError(eeprom_addr)
        elif not 0x00 <= eeprom_addr <= 0xFF:
            raise EEPROMAddrError(eeprom_addr)
    @property
    def _eeprom_data(self) -> bytes:
        return self.__eeprom_data

    @_eeprom_data.setter
    def _eeprom_data(self, eeprom_data: Union[bytes, list, tuple, int]):
        if not isinstance(eeprom_data, (bytes, list, tuple, int)):
            raise EEPROMDataError(eeprom_data)
        if isinstance(eeprom_data, int):
            eeprom_data = [eeprom_data]
        elif len(eeprom_data) >= EEPROM_SIZE - self._eeprom_addr:    # TODO: EEPROM Addr должен быть задана до!
            raise EEPROMDataError(eeprom_data)
        if not all((isinstance(x, int) and 0x00 <= x <= 0xFF) for x in eeprom_data):
            raise EEPROMDataError(eeprom_data)

        self.__eeprom_data = bytes(eeprom_data)
        self.__eeprom_data_length = len(self.__eeprom_data)

    def _pretty_eeprom(self, eeprom: bytes) -> str:
        """
        Compose pretty string from array of hex data (EEPROM) for logging
        """

        pretty_eeprom = ''
        lines, columns = divmod(len(eeprom), 16)
        for line in range(lines):
            pretty_eeprom += '\n\t ' + \
                             ' '.join([hex_repr(b) for b in
                                       eeprom[line * 16: (line + 1) * 16]])
        if columns:
            pretty_eeprom += '\n\t ' + \
                             ' '.join([hex_repr(b) for b in
                                       eeprom[lines * 16: len(eeprom)]])

        return pretty_eeprom

    def _checksum(self, data: Union[bytes, list, tuple, set]) -> int:
        """Calculate checksum for data.

        Summarize all bytes (int) in data and return least significant byte.

        Parameters
        ----------
        data : Union[bytes, list, tuple, set]
            Data, for which checksum is calculated. It could be bytes or list,
            tuple, set of int values.

        Returns
        -------
        checksum : int
            Calculated checksum for input data.

        Examples
        --------
        >>> self._checksum(b'\x00\x12\x23\x34\x02\x80\x00')
        235
        >>> self._checksum([0x00, 0x12, 0x23, 0x34, 0x02, 0x80, 0x00])
        235
        """
        if not isinstance(data, (bytes, list, tuple, set)):
            raise TypeError(f'Data must be {bytes}, {list} or {tuple}, '
                            f'not {type(data)}')
        if not all((isinstance(x, int) and 0x00 <= x <= 0xFF) for x in data):
            raise TypeError(f'{type(data)} items\' data must be {int} and be '
                            f'in range [0x00, 0xFF]')

        return sum(data) & 0xFF

    def send_cmd(self,
                 node_addr: Union[bytes, list, tuple],
                 procedure: int) -> bool:
        """Send command to node.

        Parameters
        ----------
        node_addr : Union[bytes, list, tuple]
            Target node address to which send command. It should be 3 bytes or
            3 int (list or tuple).
        procedure : int
            It should be one of the PROCEDURE constant: ``SWITCH_ON``,
            ``STEP_UP``, ``SWITCH_INVERSION``, ``SWITCH_OFF``, ``STEP_DOWN``,
            ``GLOBAL_ON``, ``GLOBAL_OFF``, ``SET_MODE``, ``RESET_MODE`` and etc.

        Returns
        -------
        bool
            True if command was successfully sent, False otherwise.

        Examples
        --------
        >>> self.send_cmd(node_addr=b'\x12\x23\x34', procedure=0x02)
        True
        """

        _LOGGER.debug(f'Calling send_cmd() with Args: {{'
                      f'\'node_addr\': {hex_repr(node_addr)}, '
                      f'\'procedure\': {hex_repr(procedure)}}}')

        try:
            self._node_addr = node_addr
            self._procedure = procedure
        except (NodeAddrError, ProcedureError) as ex:
            _LOGGER.exception(f'Invalid input parameters: {ex}')
            raise

        request = [DEVICE['COMPUTER'],  # Device ID
                   self._node_addr[0],  # Address
                   self._node_addr[1],  # Address
                   self._node_addr[2],  # Address
                   COMMAND['EXECUTE_PROCEDURE'],  # Command
                   self._procedure,  # Procedure number
                   0x00]  # Reserve
        request.append(self._checksum(request[1:]))  # Checksum

        try:
            self._request = serial.to_bytes(request)
        except RequestError as ex:
            _LOGGER.exception(f'Incorrect request format: {ex}')
            raise

        _LOGGER.debug(f'Request: {hex_repr(request)}')

        controller_is_blocked = True
        time_to_wait = self.__unlock_timeout
        # ==================== RADIO CONTROLLER START ====================
        while time_to_wait > 0.0:
            if self._controller.is_open:
                # _LOGGER.debug(f'Radio controller {self._port_path} is already '
                #               f'opened')
                sleep(self.__sleep_time)
                time_to_wait -= self.__sleep_time
                continue

            try:
                self._controller.open()
            except SerialException as ex:
                if ex.errno == errno.ENOENT:
                    _LOGGER.exception(f'Radio controller {self._port_path} is '
                                      f'not available!')
                    raise
                elif ex.errno == errno.EAGAIN:
                    # _LOGGER.debug(f'Radio controller is busy by other process')
                    sleep(self.__sleep_time)
                    time_to_wait -= self.__sleep_time
                else:
                    _LOGGER.exception(f'SerialException: {ex}')
                    raise
            else:
                _LOGGER.debug(f'Radio controller is available: {self._controller}')
                controller_is_blocked = False

                # ----- COMMUNICATION START -----
                # Send request
                self._controller.reset_output_buffer()
                try:
                    self._request_length = self._controller.write(request)
                except RequestLengthError as ex:
                    _LOGGER.exception(f'Error while sending request: {ex}')
                    raise
                # ----- COMMUNICATION END -----

                if self.__block:
                    sleep(0.3)

                break
            finally:
                self._controller.close()
        # ==================== RADIO CONTROLLER END ======================

        if controller_is_blocked:
            error_msg = f'Radio controller {self._controller} is blocked by ' \
                        f'other process for {self.__unlock_timeout} seconds'
            _LOGGER.debug(error_msg)
            raise RadioControllerBlocked(error_msg)

        return True

    def read(self,
             node_addr: Union[bytes, list, tuple],
             eeprom_addr: int,
             data_size: int) -> bytes:
        """
        Read data from Node EEPROM
        Node's examples: relay, dimmer, motor, thermoregulator

        Parameters
        ----------
        node_addr
        eeprom_addr
        data_size

        Returns
        -------

        """

        _LOGGER.debug(f'Calling read() with Args:'
                      f'\'node_addr\': {hex_repr(node_addr)}, '
                      f'\'eeprom_addr\': {hex_repr(eeprom_addr)}, '
                      f'\'data_size\': {hex_repr(data_size)}')

        try:
            self._node_addr = node_addr
            self._data_length = data_size
            self._eeprom_addr = eeprom_addr
        except (NodeAddrError, DataLengthError, EEPROMAddrError) as ex:
            _LOGGER.exception(f'Invalid input parameters: {ex}')
            raise ex

        request = [DEVICE['COMPUTER'],  # Device ID
                   self._node_addr[0],  # Address
                   self._node_addr[1],  # Address
                   self._node_addr[2],  # Address
                   COMMAND['READ_EEPROM'],  # Command
                   self._data_length,  # Size of data to read
                   self._eeprom_addr]  # Start address EEPROM, where read
        request.append(self._checksum(request[1:]))  # Checksum

        try:
            self._request = serial.to_bytes(request)
        except RequestError as ex:
            _LOGGER.exception(f'Incorrect request format: {ex}')
            raise

        _LOGGER.debug(f'Request: {hex_repr(request)}')

        controller_is_blocked = True
        time_to_wait = self.__unlock_timeout
        # ==================== RADIO CONTROLLER START ====================
        while time_to_wait > 0.0:
            if self._controller.is_open:
                # _LOGGER.debug(f'Radio controller {self._port_path} is already '
                #               f'opened')
                sleep(self.__sleep_time)
                time_to_wait -= self.__sleep_time
                continue

            try:
                self._controller.open()
            except SerialException as ex:
                if ex.errno == errno.ENOENT:
                    _LOGGER.exception(f'Radio controller {self._port_path} is '
                                      f'not available!')
                    raise
                elif ex.errno == errno.EAGAIN:
                    # _LOGGER.debug(f'Radio controller is busy by other process')
                    sleep(self.__sleep_time)
                    time_to_wait -= self.__sleep_time
                else:
                    _LOGGER.exception(f'SerialException: {ex}')
                    raise
            else:
                _LOGGER.debug(f'Radio controller is available: {self._controller}')
                controller_is_blocked = False

                # ----- COMMUNICATION START -----
                # Send request
                self._controller.reset_output_buffer()
                try:
                    self._request_length = self._controller.write(request)
                except RequestLengthError as ex:
                    _LOGGER.exception(f'Error while sending request: {ex}')
                    raise

                # Receive response
                time1 = time()
                self._controller.reset_input_buffer()
                try:
                    self._response = self._controller.read(self._expected_response_length)
                except ResponseError as ex:
                    _LOGGER.exception(f'Error while receiving response: {ex}')
                    raise
                except SerialException as ex:
                    _LOGGER.exception(f'Unknown error in serial port while '
                                      f'receiving response: {ex}')
                    raise
                time2 = time()
                # ----- COMMUNICATION END -----

                if self.__block:
                    sleep(0.1)

                break
            finally:
                self._controller.close()
        # ==================== RADIO CONTROLLER END ======================

        if controller_is_blocked:
            error_msg = f'Radio controller {self._controller} is blocked by ' \
                        f'other process for {self.__unlock_timeout} seconds.'
            _LOGGER.debug(error_msg)
            raise RadioControllerBlocked(error_msg)

        _LOGGER.debug(f'Response transfer time: {time2 - time1} sec')
        _LOGGER.debug(f'Request length -> {self._request_length}. '
                      f'Response length -> {self._response_length}.')
        _LOGGER.debug(f'EEPROM data: {hex_repr(self._response_data[:-1])}')
        # _LOGGER.debug(f'EEPROM data: {self._pretty_eeprom(self._response_data[:-1])}')

        return self._response_data[:-1]     # Last byte is check sum

    def write(self,
              node_addr: Union[bytes, list, tuple],
              eeprom_addr: int,
              data: Union[int, bytes, list, tuple]) -> bool:
        """
        Write data to Node EEPROM.
        Node's examples: relay, dimmer, motor, thermoregulator

        Parameters
        ----------
        node_addr
        eeprom_addr
        data

        Returns
        -------

        """

        _LOGGER.debug(f'Calling write() with Args:'
                      f'\'node_addr\': {hex_repr(node_addr)}, '
                      f'\'eeprom_addr\': {hex_repr(eeprom_addr)}, '
                      f'\'data\': {hex_repr(data)}')

        try:
            self._node_addr = node_addr
            self._eeprom_addr = eeprom_addr
            self._eeprom_data = data
        except (NodeAddrError, EEPROMAddrError, EEPROMDataError) as ex:
            _LOGGER.exception(f'Invalid input parameters: {ex}')
            raise ex

        request = [DEVICE['COMPUTER'],  # Device ID
                   node_addr[0],  # Address
                   node_addr[1],  # Address
                   node_addr[2],  # Address
                   COMMAND['WRITE_EEPROM'],  # Command
                   self._eeprom_data_length,  # Size of data to write
                   eeprom_addr]  # Start EEPROM address, where write
        request.append(self._checksum(request[1:]))  # Checksum of command
        request += self._eeprom_data
        request.append(self._checksum(self._eeprom_data))  # Checksum of data

        try:
            self._request = serial.to_bytes(request)
        except RequestError as ex:
            _LOGGER.exception(f'Incorrect request format: {ex}')
            raise

        _LOGGER.debug(f'Request: {hex_repr(request)}')

        controller_is_blocked = True
        time_to_wait = self.__unlock_timeout
        # ==================== RADIO CONTROLLER START ====================
        while time_to_wait > 0.0:
            if self._controller.is_open:
                # _LOGGER.debug(f'Radio controller {self._port_path} is already '
                #               f'opened')
                sleep(self.__sleep_time)
                time_to_wait -= self.__sleep_time
                continue

            try:
                self._controller.open()
            except SerialException as ex:
                if ex.errno == errno.ENOENT:
                    _LOGGER.exception(f'Radio controller {self._port_path} is '
                                      f'not available!')
                    raise
                elif ex.errno == errno.EAGAIN:
                    # _LOGGER.debug(f'Radio controller is busy by other process')
                    sleep(self.__sleep_time)
                    time_to_wait -= self.__sleep_time
                else:
                    _LOGGER.exception(f'SerialException: {ex}')
                    raise
            else:
                _LOGGER.debug(f'Radio controller is available: {self._controller}')
                controller_is_blocked = False

                # ----- COMMUNICATION START -----
                # Send request
                self._controller.reset_output_buffer()
                try:
                    self._request_length = self._controller.write(request)
                except RequestLengthError as ex:
                    _LOGGER.exception(f'Error while sending request: {ex}')
                    raise
                # ----- COMMUNICATION END -----

                if self.__block:
                    expected_block_time = 0.3 + self._request_length / 280
                    sleep(expected_block_time)

                break
            finally:
                self._controller.close()
        # ==================== RADIO CONTROLLER END ======================

        if controller_is_blocked:
            error_msg = f'Radio controller {self._controller} is blocked by ' \
                        f'other process for {self.__unlock_timeout} seconds'
            _LOGGER.debug(error_msg)
            raise RadioControllerBlocked(error_msg)

        return True
