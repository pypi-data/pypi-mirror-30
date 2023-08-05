import io
from xml.etree import ElementTree

from aiohttp import ClientSession

async def request(method, *args, **kargs):
    async with ClientSession() as session:
        async with session.request(method, *args, **kargs) as response:
            mimetype = response.content_type
            if mimetype.endswith('json'):
                return response.status, response.headers, await response.json()
            elif mimetype.endswith('xml'):
                with io.StringIO(await response.text()) as stream:
                    return response.status, response.headers, ElementTree.parse(stream)
            elif mimetype.startswith('text') or mimetype.endswith('javascript') or mimetype.endswith('svg'):
                return response.status, response.headers, await response.text()
            else:
                return response.status, response.headers, await response.read()

async def options(*args, **kargs):
    return await request('OPTIONS', *args, **kargs)

async def head(*args, **kargs):
    return await request('HEAD', *args, **kargs)

async def get(*args, **kargs):
    return await request('GET', *args, **kargs)

async def post(*args, **kargs):
    return await request('POST', *args, **kargs)

async def put(*args, **kargs):
    return await request('PUT', *args, **kargs)

async def patch(*args, **kargs):
    return await request('PATCH', *args, **kargs)

async def delete(*args, **kargs):
    return await request('DELETE', *args, **kargs)
