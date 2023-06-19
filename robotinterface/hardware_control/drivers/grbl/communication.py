import asyncio
import logging
import serial_asyncio
from robotinterface.hardware_control.drivers.grbl.constants import TIMEOUT

log = logging.getLogger(__name__)


class SerialConnection:
    """
    Represents a serial connection with read and write capabilities for a GRBL controller

    Attributes:
        reader (asyncio.StreamReader): The asyncio reader.
        writer (asyncio.StreamReader): The asyncio writer.
    """

    @classmethod
    async def create(cls, port: str, baudrate: int):
        """
        Creates a SerialConnection instance.

        Args:
            port: The port to connect to.
            baudrate: The baud rate of the connection.

        Returns:
            SerialConnection: The created SerialConnection instance.
        """
        reader, writer = await serial_asyncio.open_serial_connection(url=port, baudrate=baudrate)
        return cls(reader, writer)

    def __init__(self, reader: asyncio.StreamReader, writer: asyncio.StreamReader):
        """
        Initializes a new instance of the SerialConnection class.

        Args:
            reader: The asyncio reader.
            writer: The asyncio writer.
        """
        self.reader, self.writer = reader, writer

    async def send(self, msg: str, leading_LF: bool = False) -> str:
        """
        Sends a message and retrieves the answer.

        Args:
            msg: The message to send.
            leading_LF: Whether to expect a leading line feed (default: False).

        Returns:
            str: The received answer.

        """
        prepared_msg = self.prepare_msg(msg)
        self.writer.write(prepared_msg)
        logging.debug(f"Communication sent: {msg}")

        answer = await self.get_answer(leading_LF)
        return answer

    async def send_bytes(self, msg: bytes, leading_LF: bool = False) -> str:
        """
        Sends bytes and retrieves the answer.

        Args:
            msg: The bytes to send.
            leading_LF: Whether to expect a leading line feed (default: False).

        Returns:
            str: The received answer.
        """
        self.writer.write(msg)
        answer = await self.get_answer(leading_LF)
        return answer

    async def get_answer(self, leading_LF: bool = False):
        """
        Retrieves the answer from the reader.

        Args:
            leading_LF: Whether to expect a leading line feed (default: False).

        Returns:
            str: The received answer.
        """
        if leading_LF:
            await asyncio.wait_for(self.reader.readuntil(b'\n'), timeout=TIMEOUT)
        raw_answer = await self.reader.readuntil(b'\n')
        answer = self.process_raw_answer(raw_answer)
        logging.debug(f'Communication received: "{answer}"')
        return answer

    @staticmethod
    def prepare_msg(msg: str) -> bytes:
        """
        Prepares the message to be sent. Only the "?" command doesn't need a new line character to be 
        read by the grbl controller.

        Args:
            msg: The message to prepare.

        Returns:
            bytes: The prepared message.
        """
        msg = msg.strip()
        if msg != "?":
            msg += "\n"
        msg_encoded = msg.encode("utf-8")
        return msg_encoded

    @staticmethod
    def process_raw_answer(raw_answer: bytes) -> str:
        """
        Processes the raw answer received from the reader.

        Args:
            raw_answer: The raw answer to process.

        Returns:
            str: The processed answer.
        """
        return raw_answer.rstrip().decode()
