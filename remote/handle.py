import asyncio
import logging

from local.handle import Pipe as LocalPipe
from public.protocol import Protocol

logger = logging.getLogger(__name__)

loop = asyncio.new_event_loop()


async def handleLocalRequest(reader, writer):
    p = Pipe(reader, writer)
    await p.link()
    # await p.close()


class Pipe(LocalPipe):
    def __init__(self, reader, writer):
        super().__init__(reader, writer)

    async def link(self):
        await self.getSrcRequestToDst()

    async def getSrcRequestToDst(self):
        srcRequest = await self.read(self.srcReader)
        srcReqProto = Protocol(srcRequest)
        try:
            decodeSrcRequest = srcReqProto.decode()
        except:
            p = Protocol(b"")
            self.srcWriter.write(
                p.encode()
            )
            await self.srcWriter.drain()
            return
        else:
            dsrp = Protocol(decodeSrcRequest)
            host, port = dsrp.getHost()
            self.dstReader, self.dstWriter = await asyncio.open_connection(
                host, port
            )
            if decodeSrcRequest.startswith(b"CONNECT"):
                logger.debug("connect mode ...")
                response = b'HTTP/1.0 200 Connection Established\r\n\r\n'
                rp = Protocol(response)
                self.srcWriter.write(
                    rp.encode()
                )
                await self.srcWriter.drain()
                task1 = asyncio.create_task(self.srcToDst())
                task2 = asyncio.create_task(self.dstToSrc())
                res = asyncio.gather(task1, task2, return_exceptions=True)
                logger.debug("res ===== %s ...", res)
                return

            self.dstWriter.write(
                decodeSrcRequest
            )
            await self.dstWriter.drain()
            await self.getDstResponsetoSrc()
            await self.close()

    async def getDstResponsetoSrc(self):
        response = await self.read(self.dstReader)
        rp = Protocol(response)
        self.srcWriter.write(
            rp.encode()
        )
        await self.dstWriter.drain()
