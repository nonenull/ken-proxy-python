# coding=utf-8
import asyncio
import logging
import base64
import os
from local import config
from public.protocol import Protocol

logger = logging.getLogger(__name__)

loop = asyncio.new_event_loop()


async def handleOriginalRequest(reader, writer):
    p = Pipe(reader, writer)
    await p.link()
    # await p.close()


class Pipe(object):
    def __init__(self, reader, writer):
        self.srcReader = reader
        self.srcWriter = writer

        self.dstReader = None
        self.dstWriter = None

    async def link(self):
        srcRequest = await self.read(self.srcReader)
        logger.debug(f"get src request : {srcRequest!r}")
        srcReqProto = LocalProtocol(srcRequest)

        if b'GET /pac' in srcRequest:
            with open('local/pac.txt', 'r') as f:
                pacTemplate = f.read()
                pac = pacTemplate.replace(
                    '__PROXY__',
                    f'PROXY {config.Host}:{config.Port};'
                )
                pack = 'HTTP/1.1 200 OK\r\nContent-Type: application/x-ns-proxy-autoconfig\r\nContent-Length: {resultLength}\r\n\r\n{pac}'.format(
                    resultLength=len(pac),
                    pac=pac,
                )
                logger.debug(f"response pac file : {pack!r}")
                self.srcWriter.write(
                    pack.encode('utf-8')
                )
                await self.srcWriter.drain()
                self.srcWriter.close()
            return

        self.dstReader, self.dstWriter = await asyncio.open_connection(
            config.ServerHost, config.ServerPort
        )
        self.dstWriter.write(
            srcReqProto.encode()
        )
        await self.dstWriter.drain()

        await self.getDstResponsetoSrc()
        if srcRequest.startswith(b"CONNECT"):
            task1 = asyncio.create_task(self.srcToDst())
            task2 = asyncio.create_task(self.dstToSrc())

            res = asyncio.gather(task1, task2, return_exceptions=True)
            logger.debug("res ===== %s ...", res)
        else:
            await self.close()

    async def getSrcRequestToDst(self):
        srcRequest = await self.read(self.srcReader)
        srcReqProto = LocalProtocol(srcRequest)
        logger.debug(f"get src request : {srcRequest!r}")
        self.dstReader, self.dstWriter = await asyncio.open_connection(
            config.ServerHost, config.ServerPort
        )
        self.dstWriter.write(
            srcReqProto.encode()
        )
        await self.dstWriter.drain()

    async def getDstResponsetoSrc(self):
        encryptResponse = await self.read(self.dstReader)
        rp = Protocol(encryptResponse)
        response = rp.decode()
        self.srcWriter.write(
            response
        )
        await self.dstWriter.drain()

    async def read(self, reader) -> bytes:
        header = await reader.readuntil(b"\r\n\r\n")
        hp = Protocol(header)
        contentLength = hp.getContentLength()
        if contentLength > 0:
            body = await self.dstReader.read(contentLength)
            return header + body
        return header

    async def close(self):
        self.dstWriter.close()
        self.srcWriter.close()

    async def srcToDst(self):
        while 1:
            try:
                if self.dstWriter.is_closing():
                    break
                logger.debug("srcToDst.....")
                request = await self.srcReader.read(1024)
                if not request:
                    break
                logger.debug(f"srcToDst request: {request!r}")
                self.dstWriter.write(
                    request
                )
                await self.dstWriter.drain()
            except Exception as e:
                logger.debug("dstToSrc error: %s", e)
                break

    async def dstToSrc(self):
        while 1:
            try:
                if self.srcWriter.is_closing():
                    break
                logger.debug("dstToSrc.....")

                response = await self.dstReader.read(1024)
                if not response:
                    break
                logger.debug(f"dstToSrc response:{response!r}")
                self.srcWriter.write(
                    response
                )
                await self.srcWriter.drain()
            except Exception as e:
                logger.debug("dstToSrc error: %s", e)
                break


class LocalProtocol(Protocol):
    def __init__(self, message):
        super().__init__(message)

    def encode(self) -> bytes:
        pack = "GET http://{host}:{port}/ HTTP/1.1\r\nHost: {host}:{port}\r\nAuther: {user}\r\nAuthorization: {oPack}\r\n\r\n".format(
            host=config.ServerHost,
            port=config.ServerPort,
            user=config.ServerUser,
            oPack=base64.b64encode(self.message).decode("utf-8"),
        )
        return bytes(pack, 'utf-8')
