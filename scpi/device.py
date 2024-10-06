from datetime import datetime
from scpi.command import Command
from scpi.interface import Interface
from scpi.utils import Datetime


class Device:
    def __init__(self, scpi: Interface) -> None:
        self._scpi = scpi

    def cmd(self, command: str) -> Command:
        return Command(self._scpi, command)

    async def identify(self) -> tuple:
        res = await self.cmd("*IDN?").query()
        return tuple(res.split(","))

    async def reset(self) -> None:
        await self.cmd("*RST").send()

    async def clear_status(self) -> None:
        await self.cmd("*CLS").send()

    async def abort(self) -> None:
        await self.cmd("ABORT").send()

    async def set_clock(self, now: datetime) -> None:
        if not self._has_clock:
            raise NotImplementedError("this device doesn't have a clock")

        await self.cmd("SYSTEM:TIME").set(now.strftime("%H,%M,%S.%f")[:-3])
        await self.cmd("SYSTEM:DATE").set(now.strftime("%Y,%m,%d"))

    async def get_clock(self) -> Datetime:
        if not self._has_clock:
            raise NotImplementedError("this device doesn't have a clock")

        now_date = await self.cmd("SYSTEM:DATE?").query()
        now_time = await self.cmd("SYSTEM:TIME?").query()

        return Datetime(f"{now_date},{now_time}")

    async def assert_identification(self) -> None:
        brand, model, _, _ = await self.identify()
        assert brand == self._brand, "Invalid brand"
        assert model == self._model, "Invalid model"

    async def identify_card(self, slot: int):
        brand, model, serialno, firmware = (await self.cmd("SYSTEM:CTYPE?").query(str(slot))).split(",")
        assert brand == self._brand, "Invalid brand"
        return model
