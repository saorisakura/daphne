from urllib.parse import parse_qs

from twisted.internet import reactor, protocol
from twisted.web import server, resource
import asyncio


class Echo(protocol.Protocol):
    def dataReceived(self, data):
        self.transport.write(data)

    def connectionLost(self, reason):
        self.transport.loseConnection()


class EchoFactory(protocol.Factory):
    def buildProtocol(self, addr):
        return Echo()


class Root(resource.Resource):
    def getChild(self, name, request):
        return self

    def render_GET(self, request):
        return b"Hello, world!"

    def render_POST(self, request):
        return b"Hello, world!"

    def render(self, request):
        return b"Hello, world!"


def main():
    # http
    # site = server.Site(Root())
    # reactor.listenTCP(8080, site)
    # reactor.run()

    # tcp
    reactor.listenTCP(8000, EchoFactory())
    reactor.run()


async def app(scope, receive, send):
    assert scope['type'] == 'http'

    # 解析请求
    body = b''
    more_body = True
    while more_body:
        message = await receive()
        body += message.get('body', b'')
        more_body = message.get('more_body', False)

    # 解析查询参数
    query_string = scope['query_string'].decode()
    query_params = parse_qs(query_string)

    # 构造响应
    response_body = b'Hello, ASGI!'
    response = {
        'status': 200,
        'headers': [
            (b'Content-Type', b'text/plain'),
            (b'Content-Length', str(len(response_body)).encode())
        ],
        'body': response_body
    }

    # 发送响应
    await send(response)


# 创建服务器
async def serve(host, port):
    server = await asyncio.start_server(app, host, port)
    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')

    async with server:
        await server.serve_forever()


def main_async():
    asyncio.run(serve('localhost', 8000))


if __name__ == '__main__':
    # main()
    main_async()

