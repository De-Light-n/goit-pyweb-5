import asyncio
import logging

import websockets
import names
from websockets import WebSocketServerProtocol
from websockets.exceptions import ConnectionClosedOK
from aiofile import AIOFile
from aiopath import AsyncPath

from exchange import exchange

logger = logging.getLogger("async_logger")
formatter = logging.Formatter('%(asctime)s - %(message)s')
log_file = AsyncPath("server.log")
fh = logging.FileHandler(log_file)
fh.setFormatter(formatter)
fh.setLevel(logging.INFO)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
)
logger.addHandler(fh)


class Server:
    clients = set()

    async def register(self, ws: WebSocketServerProtocol):
        ws.name = names.get_full_name()
        self.clients.add(ws)
        logging.info(f'{ws.remote_address} connects')

    async def unregister(self, ws: WebSocketServerProtocol):
        self.clients.remove(ws)
        logging.info(f'{ws.remote_address} disconnects')

    async def send_to_clients(self, message: str):
        if self.clients:
            [await client.send(message) for client in self.clients]

    async def ws_handler(self, ws: WebSocketServerProtocol):
        await self.register(ws)
        try:
            await self.distrubute(ws)
        except ConnectionClosedOK:
            pass
        finally:
            await self.unregister(ws)

    async def distrubute(self, ws: WebSocketServerProtocol):
        async for message in ws:
            if message.startswith("exchange"):
                params = message.split(" ")
                result = await exchange(params)
                await self.send_to_clients(f"{ws.name}: {str(result)}")
                logger.info(f"Exchange was done with arguments:{params[1:]}")
            else:
                await self.send_to_clients(f"{ws.name}: {message}")


async def main():
    server = Server()
    async with websockets.serve(server.ws_handler, 'localhost', 8080):
        await asyncio.Future()  # run forever

if __name__ == '__main__':
    asyncio.run(main())
