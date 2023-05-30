import asyncio
import logging
import serial_asyncio
import time

log = logging.getLogger(__name__)

TIMEOUT = 1
class SerialConnection:


    @classmethod
    async def create(cls, port: str, bauderate: int):
        reader, writer = await serial_asyncio.open_serial_connection(url=port, baudrate=bauderate)
        return cls(reader, writer)

    def __init__(self, reader: asyncio.StreamReader, writer: asyncio.StreamReader):
        self.reader, self.writer = reader, writer

    async def send(self, msg: str, leading_LF: bool = False) -> str:
        prepared_msg = self.prepare_msg(msg)
        self.writer.write(prepared_msg)
        logging.debug(f"communication sent: {msg}")

        answer = await self.get_answer(leading_LF)
        return answer

    async def send_bytes(self, msg: bytes, leading_LF: bool = False) -> str:
        self.writer.write(msg)
        answer = await self.get_answer(leading_LF)
        return answer

    async def get_answer(self, leading_LF: bool = False):
        if leading_LF:
            await asyncio.wait_for(self.reader.readuntil(b'\n'), timeout=TIMEOUT)
        raw_answer = await self.reader.readuntil(b'\n')
        answer = self.process_raw_answer(raw_answer)
        logging.debug(f'communication received: "{answer}"')
        return answer


    @staticmethod
    def prepare_msg(msg: str) -> bytes:
        msg = msg.strip()
        if msg != "?":
            msg += "\n"
        msg_encoded = msg.encode("utf-8")
        return msg_encoded


    @staticmethod
    def process_raw_answer(raw_answer: bytes) -> str:
        return raw_answer.rstrip().decode()
