from pygments.lexer import RegexLexer, words
from pygments.token import Keyword, Text, String

KEYWORDS = [
    'create',
    'delete',
    'edit',
    'get',
    'help',
    'ls',
    'quit',
    'raw',
    'rmr',
    'set',
    'stat',
    'toggle_write'
]

# A zookeeper CLI command
COMMAND = r'(%s)' % ('|'.join(KEYWORDS))

# A znode path
PATH = r'/[^\s]*'

# A string-value
QUOTED_STR = r"('[^']*'|\"[^\"]*\")"

# A single 4 letter word
FOUR_LETTER_WORD = r'\w{4}'


class ZkCliLexer(RegexLexer):

    tokens = {
        'root': [
            (PATH, Text),
            (FOUR_LETTER_WORD, Text),
            (QUOTED_STR, String),
            (words(KEYWORDS, suffix=r'\b'), Keyword),
        ],
    }
