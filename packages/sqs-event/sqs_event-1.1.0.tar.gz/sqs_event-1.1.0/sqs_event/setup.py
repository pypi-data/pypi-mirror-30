from ergaleia.config import Config
from ergaleia.load_from_path import load_lines_from_path
from ergaleia.to_args import to_args
from ergaleia.un_comment import un_comment

from sqs_event.dispatcher import add_event_handler
from sqs_event.user import add_user_setup, add_user_normalize


CONFIG = Config([
    'queue.name env=SQS_EVENT_QUEUE_NAME',
    'queue.wait_time value=20 validator=int env=SQS_EVENT_QUEUE_WAIT_TIME',
    (
        'queue.visibility_timeout validator=int'
        ' env=SQS_EVENT_QUEUE_VISIBILITY_TIMEOUT'
    )
])


def _handle(command, line):
    args, kwargs = to_args(line)
    try:
        dict(
            event=_handle_event,
            config=_handle_config,
            normalize=_handle_normalize,
            setup=_handle_setup,
        )[command.lower()](line, *args, **kwargs)
    except KeyError as e:
        raise Exception('invalid record type {}'.format(e))


def _handle_event(line, name, handler):
    add_event_handler(name, handler)


def _handle_config(line, *args, **kwargs):
    CONFIG._define_from_path([line])


def _handle_setup(line, path):
    add_user_setup(path)


def _handle_normalize(line, path):
    add_user_normalize(path)


def load(defn='event'):
    for num, line in enumerate(
                un_comment(load_lines_from_path(defn)),
                start=1
            ):
        if line:
            try:
                tokens = line.split(' ', 1)
                if len(tokens) == 1:
                    raise Exception('missing tokens')
                _handle(*tokens)
            except Exception as e:
                raise Exception(
                    '{} on line {} of {}'.format(e, num, defn)
                )
