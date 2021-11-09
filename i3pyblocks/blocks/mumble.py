from struct import pack, unpack
import socket
import datetime
from typing import Optional, Dict, Any

from i3pyblocks import types
from i3pyblocks.blocks import base
from i3pyblocks._internal import misc, models


class MumbleBlock(base.PollingBlock):
    r"""Block that shows ping information for a mumble server.

    :param host: Host of the mumble server.

    :param port: Port of the mumble server.

    :param format_success: Format string to show on sucess.
        Supports the following placehorders:

            - ``{ping}``: Ping to the server in milliseconds
            - ``{users}``: Number of currently connected users
            - ``{max_users}``: Number of total slots on the server
            - ``{version}``: Version of the mumble server
            - ``{bandwidth}``: Maximum allowed bandwidth

    :param format_timeout: Format string to show on timeout.
        Does not support any placehorders.

    :param backgrounds_users: A maping that represents the background that will
        be used based on the number of users. It has the lowest precedence.
        For example::

            {
                1: "#00FF00,
                10: "#0000FF,
            }

    :param backgrounds_ping: Similar to ``user_background``, but uses the
        ping value instead. Has higher precendence than ``user_background``

    :param background_timeout: Background to use when a timeout occurs.
        Has the highest precendence.

    :param sleep: Sleep in seconds between each call to
        :meth:`~i3pyblocks.blocks.base.PollingBlock.run()`.

    :param \*\*kwargs: Extra arguments to be passed to
        :class:`~i3pyblocks.blocks.base.PollingBlock` class.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 64738,
        format_success: str = "M {users} {ping:.0f}ms",
        format_timeout: str = "timeout",
        backgrounds_users: models.Threshold = {},
        backgrounds_ping: models.Threshold = {
            100: types.Color.WARN,
        },
        background_timeout: Optional[str] = types.Color.URGENT,
        sleep: int = 60,
        **kwargs
    ) -> None:
        super().__init__(sleep=sleep, **kwargs)
        self.host = host
        self.port = port
        self.format_success = format_success
        self.format_timeout = format_timeout
        self.backgrounds_users = backgrounds_users
        self.backgrounds_ping = backgrounds_ping
        self.background_timeout = background_timeout

    def ping(self) -> Optional[Dict[str, Any]]:
        """Based on
        https://raw.githubusercontent.com/mumble-voip/mumble-scripts/master/Non-RPC/mumble-ping.py"""
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(1)

        buf = pack(">iQ", 0, datetime.datetime.now().microsecond)
        s.sendto(buf, (self.host, self.port))

        try:
            data, _ = s.recvfrom(1024)
        except socket.timeout:
            return None

        recv_time = datetime.datetime.now().microsecond

        r = unpack(">bbbbQiii", data)

        values = dict()
        values["version"] = ".".join([str(v) for v in r[1:4]])
        timestamp = r[4]
        values["users"] = r[5]
        values["max_users"] = r[6]
        values["bandwidth"] = r[7] / 1000

        ping = (recv_time - timestamp) / 1000.0

        values["ping"] = ping if ping > 0 else ping + 1000

        return values

    async def run(self) -> None:
        self.format = self.format_success
        background = None

        values = self.ping()
        if values == None:
            self.update(self.format_timeout, background=self.background_timeout)
            return

        if background is None:
            background = misc.calculate_threshold(self.backgrounds_ping, values["ping"])
        if background is None:
            background = misc.calculate_threshold(
                self.backgrounds_users, values["users"]
            )

        self.update(
            self.ex_format(
                self.format,
                **values,
            ),
            background=background,
        )
