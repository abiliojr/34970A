import aioserial
import asyncio
from scpi.interface import Interface


class Serial(Interface):
    def __init__(self, port: str, baudrate, rtscts: bool = True, timeout: float = 5) -> None:
        self._s = aioserial.AioSerial(port, baudrate, rtscts=rtscts)
        self._s.reset_input_buffer()
        self._s.reset_output_buffer()
        self._timeout = timeout

    async def send_data(self, command: str) -> None:
        await self._s.write_async(command.encode("ascii"))
        await self._s.write_async(b"\n")

    async def recv_data(self) -> str:
        async with asyncio.timeout(self._timeout):
            return (await self._s.readline_async()).decode("ascii").strip("\r\n")

    async def _read_until_any(self, separators: bytes) -> bytes:
        data = bytearray()
        while True:
            c = await self._s.read_async(1)
            data += c
            if c in separators:
                return bytes(data)

    async def recv_data_field(self, separators: str) -> tuple[str, str]:
        async with asyncio.timeout(self._timeout):
            data = (await self._read_until_any(separators.encode("ascii"))).decode()
            return data[:-1], data[-1]
