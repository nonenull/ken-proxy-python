import asyncio
import logging.config

from remote import config
from remote.handle import handleLocalRequest

logging.config.dictConfig(config.LogConf)
logger = logging.getLogger()


async def main():
    server = await asyncio.start_server(
        handleLocalRequest, config.Host, config.Port
    )

    addr = server.sockets[0].getsockname()
    logger.info(f'Serving on {addr}')

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
