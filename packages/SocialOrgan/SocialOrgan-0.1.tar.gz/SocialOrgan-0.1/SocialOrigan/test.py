import asyncio
import socket
import time
import traceback


async def tcp_echo_client(num, host, loop):
    h, p = host.split(":")
    try:
        st = time.time()
        reader, writer = await asyncio.open_connection(h, int(p), loop=loop)
        et = time.time() -st
        # print('Close the socket')
        writer.close()
        return host,et

    except socket.error as e:
        # traceback.print_stack()
        return host,9999
    # print('Send: %r' % message)
    # writer.write(message.encode())

    # data = yield from reader.read(100)
    # print('Received: %r' % data.decode())


async def _Tests(hosts, loop):
    
    task = [tcp_echo_client(i, host, loop) for i, host in enumerate(hosts)]
    return await asyncio.gather(*task)



def Tests(hosts):
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(_Tests(hosts, loop))
    sorted(res, key=lambda x:x[1])
    loop.close()
    return res


async def handle_echo(reader, writer):
    data = await reader.read(100)
    message = data.decode()
    addr = writer.get_extra_info('peername')
    print("Received %r from %r" % (message, addr))

    print("Send: %r" % message)
    writer.write(data)
    await writer.drain()

    print("Close the client socket")
    writer.close()


def main():
    loop = asyncio.get_event_loop()
    coro = asyncio.start_server(handle_echo, '127.0.0.1', 18888, loop=loop)
    server = loop.run_until_complete(coro)

    # Serve requests until Ctrl+C is pressed
    print('Serving on {}'.format(server.sockets[0].getsockname()))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    # Close the server
    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()