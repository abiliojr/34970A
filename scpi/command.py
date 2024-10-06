from scpi.interface import Interface


class Command:
    def __init__(self, scpi: Interface, cmd: str) -> None:
        self._scpi = scpi
        self._cmd = cmd

    async def send(self):
        await self._scpi.send_data(self._cmd)

    async def set(self, value: str):
        await self._scpi.send_data(f"{self._cmd} {value}")

    async def query(self, args: str = None) -> str:
        await self._scpi.send_data(self._cmd if not args else f"{self._cmd} {args}")
        return await self._scpi.recv_data()

    async def query_fields(self, n_fields: int, separator: str = ",", args: str = None) -> tuple:
        separators = separator + "\n"
        await self._scpi.send_data(self._cmd if not args else f"{self._cmd} {args}")

        while True:
            fields = []
            for _ in range(n_fields):
                field, sep = await self._scpi.recv_data_field(separators)
                fields.append(field)
            yield fields

            if sep == "\n":
                break
