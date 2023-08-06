import json

from pygments import highlight
from pygments.lexers.data import JsonLexer
from pygments.formatters.terminal import TerminalFormatter


def var_2_cool_json(data):
    """

    :param data:
    :return:
    """

    output = json.dumps(
        data, indent=2
    )

    return highlight(output, JsonLexer(), TerminalFormatter())