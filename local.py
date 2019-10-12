# coding=utf-8
import asyncio
import logging.config
from local import config, handle

logging.config.dictConfig(config.LogConf)
logger = logging.getLogger()


async def main():
    server = await asyncio.start_server(
        handle.handleOriginalRequest, config.Host, config.Port
    )

    addr = server.sockets[0].getsockname()
    logger.info(f'本地代理启动: {addr}')

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
