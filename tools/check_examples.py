"""Check docs snippets and execute SDK examples against a mock HTTP transport.

Run with Python 3.10+ and libraos-sdk + PyYAML installed. This does not contact
an inference server or modify agent definitions.
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
            yaml.safe_load(text)
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

def handle(request):
    body = json.loads(request.content)
    requests.append((request.url.path, body, request.headers))
    if request.url.path == '/v1/agents':
        assert request.headers['anthropic-beta'] == 'managed-agents-2026-04-01'
        assert body['system'] == 'You are a helpful assistant. Answer concisely.'
        assert body['agent_type'] == 'persona'
        assert 'instructions' not in body
        return httpx.Response(200, json={'id': 'my-first-agent'})
    assert request.url.path == '/v1/messages'
    assert 'agent_id' in body['metadata']
    text = json.dumps(classification) if body['metadata']['agent_id'] == 'email-classifier' else 'Hello from the agent.'
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
output = io.StringIO()
with contextlib.redirect_stdout(output):
    exec(compile(code, 'first_agent.py', 'exec'), {'Client': ExampleClient})
assert output.getvalue().strip() == 'Hello from the agent.'
assert requests[-1][1]['metadata']['agent_id'] == 'my-first-agent'
print('SDK quickstart: prompt, beta header, routing, and text extraction passed')

support = {'Client': ExampleClient}
exec(blocks('docs/guides/customer-support.md')[0].replace('from libraos import Client', ''), support)
result = asyncio.run(support['answer']('user-token', [{'role': 'user', 'content': 'Help'}]))
assert result == 'Hello from the agent.'
assert requests[-1][2]['authorization'] == 'Bearer user-token'
print('Support example: supported SDK arguments and user credential passed')

actions = []
routing = {'Client': ExampleClient,
           'assign_queue': lambda *args: actions.append('assign'),
           'add_internal_note': lambda *args: actions.append('note'),
           'escalate_to_human': lambda *args: actions.append('escalate')}
exec(blocks('docs/guides/ticket-routing.md')[0].replace('from libraos import Client', ''), routing)
asyncio.run(routing['route']({'id': 't-1', 'text': 'Where is my invoice?'}))
assert actions == ['note', 'assign'], actions
actions.clear()
classification['confidence'] = 0.2
asyncio.run(routing['route']({'id': 't-2', 'text': 'An ambiguous request'}))
assert actions == ['note', 'escalate'], actions
print('Routing example: content-block JSON extraction and review-before-assignment passed')
