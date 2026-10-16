"""Check docs snippets and execute SDK/HTTP examples against mock transports.

Run with Python 3.10+ and libraos-sdk, httpx, PyYAML and jsonschema installed.
This does not contact an inference server or modify agent definitions.
"""

import ast
import asyncio
import contextlib
import io
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
from types import SimpleNamespace

from jsonschema import ValidationError

import httpx
import yaml

from libraos import Client

ROOT = Path(__file__).resolve().parents[1]
FENCES = re.compile(r'^```(\w+)\n(.*?)^```', re.M | re.S)
counts = {'python': 0, 'yaml': 0, 'bash': 0, 'json': 0}
for page in sorted(ROOT.glob('docs/**/*.md')):
    for language, code in FENCES.findall(page.read_text()):
        if language == 'python':
            ast.parse(code, filename=str(page))
        elif language == 'yaml':
            # Full agent Markdown examples contain a YAML frontmatter block.
            text = code.split('---', 2)[1] if code.startswith('---\n') else code
            list(yaml.safe_load_all(text))
        elif language == 'bash':
            subprocess.run(['bash', '-n'], input=code, text=True, check=True)
            if '/v1/messages' in code and 'curl ' in code:
                args = shlex.split(code)
                payload = json.loads(args[args.index('-d') + 1])
                assert payload['metadata']['agent_id'], f'{page}: missing agent selector'
        elif language == 'json':
            json.loads(code)
        else:
            continue
        counts[language] += 1
print('Syntax checks:', counts)

def blocks(path):
    return [code for lang, code in FENCES.findall((ROOT / path).read_text())
            if lang == 'python']

requests = []
classification = {'intent': 'billing', 'priority': 'medium', 'confidence': 0.9,
                  'reasoning': 'Invoice question', 'language': 'en'}

routing_status = 200

def handle(request):
    body = json.loads(request.content)
    requests.append((request.url.path, body, request.headers))
    if request.url.path == '/v1/agents':
        assert request.headers['anthropic-beta'] == 'managed-agents-2026-04-01'
        assert body['system'] == first['SYSTEM']
        assert body['tool_scope'] == 'none'
        assert body['agent_type'] == 'persona'
        assert 'instructions' not in body
        return httpx.Response(200, json={'id': body['name']})
    if request.url.path == '/agents/v1/email-classifier/chat':
        assert request.method == 'POST'
        assert set(body) == {'message'}
        assert request.headers['authorization'] == 'Bearer test-token'
        return httpx.Response(routing_status, json={'output': classification})
    assert request.url.path == '/v1/messages'
    assert 'agent_id' in body['metadata']
    text = 'Hello from the agent.'
    return httpx.Response(200, json={'id': 'msg-test', 'type': 'message',
        'role': 'assistant', 'content': [{'type': 'text', 'text': text}],
        'model': body['model'], 'stop_reason': 'end_turn',
        'usage': {'input_tokens': 1, 'output_tokens': 1}})

class ExampleClient(Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, transport=httpx.MockTransport(handle))

os.environ['LIBRA_OS_URL'] = 'https://test.invalid'
os.environ['LIBRA_OS_API_KEY'] = 'test-token'

# Execute the exact tutorial, swapping only its network transport.
code = blocks('docs/agents/creating-an-agent.md')[0]
code = code.replace('from libraos import Client', '')
first = {'Client': ExampleClient}
output = io.StringIO()
with contextlib.redirect_stdout(output):
    exec(compile(code, 'first_agent.py', 'exec'), first)
assert output.getvalue().strip() == 'Hello from the agent.'
assert requests[-1][1]['metadata']['agent_id'] == requests[0][1]['name']
print('SDK quickstart: prompt, beta header, routing, and text extraction passed')

support = {'Client': ExampleClient}
exec(blocks('docs/guides/customer-support.md')[0].replace('from libraos import Client', ''), support)
result = asyncio.run(support['answer']('user-token', [{'role': 'user', 'content': 'Help'}]))
assert result == 'Hello from the agent.'
assert requests[-1][2]['authorization'] == 'Bearer user-token'
print('Support example: supported SDK arguments and user credential passed')

actions = []
class RoutingClient(httpx.AsyncClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, transport=httpx.MockTransport(handle))

routing = {'httpx': SimpleNamespace(AsyncClient=RoutingClient),
           'assign_queue': lambda *args: actions.append('assign'),
           'add_internal_note': lambda *args: actions.append('note'),
           'escalate_to_human': lambda *args: actions.append('escalate')}
exec(blocks('docs/guides/ticket-routing.md')[0].replace('import httpx', ''), routing)
# The inline client contract must match the agent's YAML contract.
routing_page = (ROOT / 'docs/guides/ticket-routing.md').read_text()
agent_schema = next(yaml.safe_load(code)['output_type']['schema_inline']
                    for lang, code in FENCES.findall(routing_page)
                    if lang == 'yaml' and code.startswith('output_type:'))
assert routing['ROUTING_SCHEMA'] == agent_schema
asyncio.run(routing['route']({'id': 't-1', 'text': 'Where is my invoice?'}))
assert actions == ['note', 'assign'], actions
actions.clear()
classification['confidence'] = 0.2
asyncio.run(routing['route']({'id': 't-2', 'text': 'An ambiguous request'}))
assert actions == ['note', 'escalate'], actions
print('Routing example: native chat output, schema and review-before-assignment passed')

for invalid in ({'intent': 'billing'}, {**classification, 'intent': 'invented'},
                {**classification, 'confidence': 2}, 'prose instead of an object'):
    actions.clear()
    valid = classification
    classification = invalid
    try:
        asyncio.run(routing['route']({'id': 't-invalid', 'text': 'Question'}))
    except ValidationError:
        pass
    else:
        raise AssertionError('Invalid classification was accepted')
    finally:
        classification = valid
    assert actions == [], actions

for routing_status in (403, 422, 503):
    actions.clear()
    try:
        asyncio.run(routing['route']({'id': 't-error', 'text': 'Question'}))
    except httpx.HTTPStatusError as exc:
        assert exc.response.status_code == routing_status
    else:
        raise AssertionError('HTTP failure was accepted')
    assert actions == [], actions
print('Routing boundaries: schema and HTTP failures cause no ticket-system actions')
