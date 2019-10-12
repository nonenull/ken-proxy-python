# coding=utf-8
import base64
import logging
import time
import json

CRLF = b'\r\n'
COLON = b':'
BUFFER_SIZE = 1024

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Protocol(object):
    def __init__(self, message: bytes):
        self.message = message
        self.header = {}
        self._parse()

    def encode(self):
        encryptionPack = base64.b64encode(self.message)
        resultDict = json.dumps({
            'time': time.time()
        })
        pack = 'HTTP/1.1 200 OK\r\nServer: nginx\r\nContent-Length: {resultLength}\r\nAuthorization: {encryptionPack}\r\n\r\n{resultDict}'.format(
            encryptionPack=encryptionPack.decode(),
            resultLength=len(resultDict),
            resultDict=resultDict,
        )
        return bytes(pack, 'utf-8')

    def decode(self) -> bytes:
        b64Response = self.header.get('Authorization')
        logger.debug(f'b64Response: {b64Response!r}')
        response = base64.b64decode(b64Response)
        return response

    def getContentLength(self) -> int:
        return int(
            self.header.get('Content-Length', 0)
        )

    def getHost(self) -> (str, str):
        logger.debug("host ==== %s", self.header)
        hostStr = self.header['Host']
        if ':' in hostStr:
            host, port = hostStr.split(COLON.decode('utf-8'))
        else:
            host = hostStr
            port = '80'
        return host, port

    def _parse(self):
        if CRLF * 2 in self.message:
            headerStr = self.message.split(CRLF * 2)[0]
        else:
            headerStr = self.message

        for n, itemStr in enumerate(headerStr.split(b'\r\n')):
            if n == 0:
                continue
            key, value = itemStr.split(COLON, maxsplit=1)
            key = key.strip()
            value = value.strip()
            self.header[key.decode('utf-8')] = value.decode('utf-8')
