
import sys  # noqa: F401
import asyncio

from wdom.tag import H1
from wdom.document import get_document
from wdom import server

loop = asyncio.get_event_loop()
doc = get_document()
doc.body.appendChild(H1('FIRST', id='h1'))
doc.add_cssfile('testdir/test.css')
server.add_static_path('testdir', '/home/takagi/Projects/wdom/tests/test_selenium/testdir')  # noqa: E501
server.start_server(loop=loop, check_time=10)
loop.run_forever()
