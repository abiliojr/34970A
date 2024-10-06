#!/usr/bin/env python3

import asyncio
from datetime import datetime
from hp3970a import HP3970A


async def main() -> None:
    device = HP3970A("/dev/ttyUSB0", 115200)

    await device.reset()
    await device.assert_identification()

    await device.clear_status()
    await device.set_clock(datetime.now())
    print(f"Experiment started at: {await device.get_clock()}")

    for slot in (100, 200, 300):
        model = await device.identify_card(slot)
        print(f"{model} in slot {slot}")

    print()

    await device.display_text("configuring!")

    await device.cmd("CONFIGURE:VOLTAGE:DC").set("auto,(@101,104)")
    await device.cmd("CONFIGURE:TEMPERATURE").set("TCouple,K,(@301)")
    await device.cmd("UNIT:TEMPERATURE").set("C,(@301)")
    await device.cmd("CALCULATE:LIMIT:LOWER").set("9,(@101)")

    await device.cmd("CALCULATE:LIMIT:LOWER:STATE").set("on")
    await device.cmd("OUTPUT:ALARM1:SOURCE").set("(@101)")

    await device.cmd("CALCULATE:LIMIT:UPPER").set("-14, (@104)")
    await device.cmd("CALCULATE:LIMIT:UPPER:STATE").set("on")
    await device.cmd("OUTPUT:ALARM4:SOURCE").set("(@104)")

    await device.cmd("ROUTE:MONITOR:CHANNEL").set("(@301)")
    await device.cmd("ROUTE:MONITOR:STATE").set("on")

    await device.cmd("ROUTE:SCAN").set("(@301)")
    # await device.cmd("ROUTE:SCAN").set("(@101,104,301)")

    await device.cmd("TRIGGER:SOURCE").set("timer")
    await device.cmd("TRIGGER:TIMER").set("1")
    await device.cmd("TRIGGER:COUNT").set("100")

    await device.clear_display()
    # await device.display_text("measuring...")

    async for read in device.read():
        print(read)

    await device.display_text("Done!")
    await asyncio.sleep(1)
    await device.clear_display()

try:
    asyncio.run(main())
except TimeoutError:
    print("Command timed out...")
