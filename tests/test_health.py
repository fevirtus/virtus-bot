import asyncio
import json
import unittest
from types import SimpleNamespace
from web.server import app


class HealthRoutes(unittest.IsolatedAsyncioTestCase):
    async def get(self, path):
        messages = []
        async def receive():
            return {'type':'http.request', 'body':b'', 'more_body':False}
        async def send(message):
            messages.append(message)
        scope = {'type':'http', 'asgi':{'version':'3.0'}, 'http_version':'1.1', 'method':'GET',
                 'scheme':'http', 'path':path, 'raw_path':path.encode(), 'query_string':b'',
                 'root_path':'', 'headers':[], 'server':('test',80), 'client':('test',123)}
        await asyncio.wait_for(app(scope, receive, send), 2)
        status = next(m['status'] for m in messages if m['type']=='http.response.start')
        body = b''.join(m.get('body', b'') for m in messages)
        return status, body

    async def test_liveness_not_shadowed_by_static_mount(self):
        status, body = await self.get('/health/live')
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body), {'status':'alive'})

    async def test_readiness_waits_for_discord(self):
        previous = getattr(app.state, 'bot', None)
        app.state.bot = SimpleNamespace(is_ready=lambda:False)
        try:
            status, body = await self.get('/health/ready')
            self.assertEqual(status, 503)
            self.assertIn(b'Discord not ready', body)
        finally:
            app.state.bot = previous
