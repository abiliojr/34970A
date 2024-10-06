from scpi import Device, Serial, Datetime


class Alarm:
    def __init__(self, value):
        readable_states = ("no", "low", "high")
        self._v = int(value)
        self._s = readable_states[self._v]

    def __str__(self):
        return self._s

    def __repr__(self) -> str:
        return str(self)

    def __int__(self):
        return self._v


class Quantity:
    def __init__(self, qty: str):
        self._value, self._unit = qty.split()
        self._value = float(self._value)

    def __repr__(self) -> str:
        return f"{self.value} {self.unit}"

    def __float__(self) -> float:
        return self.value

    @property
    def value(self) -> float:
        return self._value

    @property
    def unit(self) -> str:
        return self._unit


class HP3970A(Device):
    _brand = "HEWLETT-PACKARD"
    _model = "34970A"
    _has_clock = True

    def __init__(self, port: str, baudrate, rtscts: bool = True) -> None:
        super().__init__(Serial(port, baudrate, rtscts))

    async def display_text(self, text: str) -> None:
        await self.cmd("DISPLAY:TEXT").set(f'"{text}"')

    async def clear_display(self) -> None:
        await self.cmd("DISPLAY:TEXT:CLEAR").send()

    async def read(self, absolute_time: bool = True):
        await self.cmd("FORMAT:READING:ALARM").set("on")
        await self.cmd("FORMAT:READING:CHANNEL").set("on")
        await self.cmd("FORMAT:READING:UNIT").set("on")

        await self.cmd("FORMAT:READING:TIME").set("on")
        await self.cmd("FORMAT:READING:TIME:TYPE").set("absolute" if absolute_time else "relative")

        # number of fields = 3 (alarm, channel, measure) + time fields
        # yyyy,MM,dd,hh,mm,ss.ss (6) when relative or 1 when relative

        num_fields = 3 + (6 if absolute_time else 1)

        async for fields in self.cmd("READ?").query_fields(num_fields):
            yield {
                "quantity": Quantity(fields[0]),
                "time": Datetime(",".join(fields[1:7])) if absolute_time else float(fields[1]),
                "channel": int(fields[-2]),
                "alarms": Alarm(fields[-1]),
            }