#!/usr/bin/env python3

import asyncio
import logging
import math

import psutil

from i3pyblocks import core, modules

logging.basicConfig(filename=f".i3pyblocks.log", level=logging.INFO)


def partitions(excludes=["/boot", "/nix/store"]):
    partitions = psutil.disk_partitions()
    return [p for p in partitions if p.mountpoint not in excludes]


async def main(loop):
    runner = core.Runner(loop=loop)

    runner.register_module(
        modules.psutil.NetworkSpeedModule(
            format=" {upload}  {download}", separator=False
        )
    )
    runner.register_module(
        modules.psutil.SensorsTemperaturesModule(
            format="{icon} {temperature:.0f}°C",
            icons={25: "", 50: "", 75: "", math.inf: ""},
            separator=False,
        )
    )
    for partition in partitions():
        runner.register_module(
            modules.psutil.DiskUsageModule(
                format=" {label}: {free:.1f}GiB",
                path=partition.mountpoint,
                short_label=True,
                separator=False,
            )
        )
    runner.register_module(
        modules.psutil.VirtualMemoryModule(
            format=" {available:.1f}GiB", separator=False
        )
    )
    runner.register_module(
        modules.psutil.CpuPercentModule(format=" {percent}%", separator=False)
    )
    runner.register_module(
        modules.psutil.LoadAvgModule(format=" {load1}", separator=False)
    )
    runner.register_module(
        modules.psutil.SensorsBatteryModule(
            format_plugged=" {percent:.0f}%",
            format_unplugged={10: "", 25: "", 50: "", 75: "", math.inf: ""},
            separator=False,
        )
    )
    runner.register_module(
        modules.LocalTimeModule(
            format_time=" %T", format_date=" %a, %d/%m", separator=False
        )
    )
    await runner.start()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
    loop.close()
