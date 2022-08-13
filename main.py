import asyncio
import random
from datetime import datetime
import logger

def get_time():
    s = datetime.now().isoformat(" ", timespec='milliseconds')
    return f"{s[:10]};{s[10:]}"

def counter_client(): # Замыкания для того, чтобы избежать использования глобальных переменных.
    count = 0
    def counter_requset():
        curr_request = 0
        async def handle_echo(reader, writer):
            nonlocal count
            count += 1
            read_write_task = asyncio.create_task(handle_read_write(reader, writer))
            keep_alive_task = asyncio.create_task(keep_alive(writer))
            await keep_alive_task
            await read_write_task

        async def handle_read_write(reader, writer):
            current_client = count
            while True:
                data = await reader.read(100)
                message = data.decode(encoding='ascii')
                time = get_time()
                if random.random() < 0.1:
                    logger.log_server(time, message, "проигнорировано", True)
                    continue
                interval = random.randint(100, 1000)
                await asyncio.sleep(float(interval) / 1000)
                nonlocal curr_request
                message_send = "[{curr_request}/{count_request}] PONG ({current_client})".format(curr_request=curr_request, count_request = message[message.find("[")+1:message.find("]")], current_client = current_client)
                s = bytearray(message_send.encode(encoding='ascii'))
                s.append(0x0A)
                writer.write(s)
                logger.log_server(time, message, message_send)
                curr_request+=1
                await writer.drain()
        async def keep_alive(writer):
            while True:
                await asyncio.sleep(5)
                nonlocal curr_request
                message = "[{curr_request}] KEEPALIVE".format(curr_request=curr_request)
                s = bytearray(message.encode(encoding='ascii'))
                s.append(0x0A)
                writer.write(s)
                curr_request+=1
                await writer.drain()
        return handle_echo
    return counter_requset


async def main():
    counter_request = counter_client()
    handle_echo = counter_request()

    server = await asyncio.start_server(
        handle_echo, '127.0.0.1', 8888)

    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')

    async with server:
        await server.serve_forever()

asyncio.run(main())