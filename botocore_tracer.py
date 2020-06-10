import atexit
import datetime
import inspect
import json
import uuid
import botocore.client
from botocore.handlers import BUILTIN_HANDLERS
from collections import defaultdict
from urllib.parse import parse_qsl

BOTOCORE_EVENT_TO_CATCH = 'before-send'

_CALLS = defaultdict(set)


class _CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        if isinstance(obj, bytes):
            return obj.decode('utf-8')
        return json.JSONEncoder.default(self, obj)


def _to_tuples(obj):
    if isinstance(obj, list):
        return tuple(_to_tuples(e) for e in obj)
    if isinstance(obj, dict):
        return tuple((_to_tuples(k), _to_tuples(v)) for k, v in sorted(obj.items()))
    return obj


def register_botocore_event(event_name, request, **kwargs):
    frame = inspect.currentframe()

    # go to botocore.client frame
    while frame.f_code.co_filename != botocore.client.__file__:
        frame = frame.f_back

    # go to the frame just before botocore.client
    while frame.f_code.co_filename == botocore.client.__file__:
        frame = frame.f_back

    # need tuples to add to the set, can't add lists because they aren't hashable
    if 'json' in str(request.headers.get('content-type', b'')):
        body = _to_tuples(json.loads(request.body))
    else:
        if hasattr(request.body, 'read'):
            body = '<content redacted>'
        else:
            body = _to_tuples(parse_qsl(request.body))
    service, api = event_name.replace(f'{BOTOCORE_EVENT_TO_CATCH}.', '').split('.', 1)
    call_info = (f'{service}:{api}', request.url, body)
    key = f'{inspect.getsourcefile(frame)}:{frame.f_lineno}'
    _CALLS[key].add(call_info)


def display(stdout):
    output = json.dumps({
        '_run_id': str(uuid.uuid4()),
        '_datetime': datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S'),
        'output': _CALLS,
    }, indent=2, cls=_CustomJSONEncoder)
    if stdout:
        print(output)
    else:
        now = datetime.datetime.utcnow().strftime("%Y_%m_%dT%H_%M_%S")
        with open(f'botocore_tracer--{now}.json', 'w') as f:
            f.write(output)


def install(display_fn=display, stdout=False):
    atexit.register(display_fn, stdout)
    BUILTIN_HANDLERS.append((BOTOCORE_EVENT_TO_CATCH, register_botocore_event))

