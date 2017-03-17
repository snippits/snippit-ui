#!/usr/bin/python3
from __future__ import unicode_literals, print_function
from aiohttp import web
import os
import sys
import json
import collections

base_path = os.path.join(os.path.dirname(__file__), '..', 'public')

async def handle(request):
    name = request.match_info.get('name', "index.html")
    rel_path = os.path.join(base_path, name)

    if (name == "index.html"):
        headers = {"content-type": "text/html"}
        with open(rel_path, 'r') as content_file:
            text = content_file.read()
    else:
        headers = {"content-type": "text/html"}
        with open(rel_path, 'r') as content_file:
            text = content_file.read()

    return web.Response(text=text, headers=headers)

async def output_handle(request):
    name = request.match_info.get('name', "")
    rel_path = os.path.join(base_path, "output", name)

    with open(rel_path, 'r') as content_file:
        text = json.loads(content_file.read())

    return web.json_response(text)

app = web.Application()
app.router.add_static('/lib', os.path.join(base_path, 'lib'))
app.router.add_static('/stylesheets', os.path.join(base_path, 'stylesheets'))

app.router.add_get('/output/{name}', output_handle)
app.router.add_get('/{name}', handle)

web.run_app(app)

