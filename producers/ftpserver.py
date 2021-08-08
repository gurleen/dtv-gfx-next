import asyncio
import aioftp
import socket


USERS = (
    aioftp.User(
        "gurleen",
        "password",
        home_path="/",
        permissions=(
            aioftp.Permission("/", readable=True, writable=True),
        )
    ),
)


async def run_ftp_server(q: asyncio.Queue):
    server = aioftp.Server(users=USERS, path_io_factory=aioftp.AsyncPathIO)
    await server.start(port=39735, family=socket.AF_INET)