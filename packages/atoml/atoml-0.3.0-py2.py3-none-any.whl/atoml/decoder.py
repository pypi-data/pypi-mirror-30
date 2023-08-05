"""
    toml.decoder
    ~~~~~~~~~~~~
    TOML decoder

    :author: Frost Ming
    :email: mianghong@gmail.com
    :license: BSD-2
"""
__all__ = ('Converter', 'Decoder', 'loads', 'load')

import datetime
import re

from atoml.errors import TomlDecodeError
from atoml.tz import TomlTZ
from atoml.compat import basestring, unichr, long, StringIO

_DIGITS_WITH_LINE = r'(?:\d|(?<=\d)_(?=\d))+'
_KEY_NAME = (r'\s*((\'|"|\'{3}|"{3})?(?(2).*?(?<!\\)\2|[a-zA-Z0-9_\-]+))\s*')
KEY_RE = re.compile(r'%s= *' % _KEY_NAME)
BLANK_RE = re.compile(r'^\s*(#.*)?$')
TABLE_RE = re.compile(r'^\s*\[([^\[\]]+)\]\s*(#.*)?$')
TABLE_ARRAY_RE = re.compile(r'^\s*\[{2}([^\[\]]+)\]{2}\s*(#.*)?$')
MULTISTRING_RE = re.compile(r'^["]{3}(.*?)((?<!\\)["]{3})?')


def contains_list(longer, shorter):
    """Check if longer list starts with shorter list"""
    if len(longer) <= len(shorter):
        return False
    for a, b in zip(shorter, longer):
        if a != b:
            return False
    return True


def cut_list(longer, shorter):
    """Cut the longer list with the shorter one"""
    shorter = shorter or []
    return longer[len(shorter):]


class TomlInlineTable(object):
    """Sentinel class for inline table"""
    pass


def empty_inline_table(base=dict):
    """Create an empty inline table with given base class"""
    class TemporaryInlineTable(base, TomlInlineTable):
        pass
    return TemporaryInlineTable()


class Converter:

    patterns = [
        ('blank', BLANK_RE),
        ('boolean', re.compile(r'(true|false)')),
        ('datetime', re.compile(r'(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2})'
                                r'(\.\d{6})?(Z|[+-]\d{2}:\d{2})?')),
        ('date', re.compile(r'(\d{4}-\d{2}-\d{2})')),
        ('time', re.compile(r'(\d{2}:\d{2}:\d{2})(\.\d{6})?')),
        ('integer', re.compile(r'([+-]?%s(?=[^eE\.])'
                               r'|0x[a-fA-F0-9]+'
                               r'|0o[0-7]+'
                               r'|0b[01]+)' % (_DIGITS_WITH_LINE,))),
        ('float', re.compile(r'([+-]?%s(?:\.%s)?'
                             r'(?:[+-]?[eE]\d+)?'
                             r'|[+-]?(?:inf|nan))'
                             % (_DIGITS_WITH_LINE, _DIGITS_WITH_LINE),
                             flags=re.I)),
        ('multi_string', re.compile(r'["]{3}')),
        ('multi_lit_string', re.compile(r"[']{3}")),
        ('string', re.compile(r'(?!"{3})"(.*?)(?<!\\)"')),
        ('lit_string', re.compile(r"(?!'{3})'(.*?)(?<!\\)'")),
        ('list_begin', re.compile(r'\[ *')),
        ('table_begin', re.compile(r'\{ *'))
    ]

    string_end_re = re.compile(r'(.*?)(?<!\\)"{3}')
    lit_string_end_re = re.compile(r"(.*?)(?<!\\)'{3}")

    escapes = {
        'b': '\b',
        't': '\t',
        'n': '\n',
        'f': '\f',
        'r': '\r',
        '\\': '\\',
        '"': '"',
        '/': '/',
        "'": "'"
    }

    list_end_re = re.compile(r' *\]')
    table_end_re = re.compile(r' *\}')
    sep_re = re.compile(r' *, *')
    basicstr_re = re.compile(r'[^"\\\000-\037]*')
    unicode_re = re.compile(r'[uU]((?<=u)[a-fA-F0-9]{4}|(?<=U)[a-fA-F0-9]{8})')

    def __init__(self, parser):
        self.parser = parser
        self.line = None

    def unescape(self, string):
        tokens = []
        i = 0
        while True:
            m = Converter.basicstr_re.match(string, i)
            i = m.end()
            tokens.append(m.group())
            if i == len(string) or string[i] != '\\':
                break
            else:
                i += 1
            if Converter.unicode_re.match(string, i):
                m = Converter.unicode_re.match(string, i)
                i = m.end()
                tokens.append(unichr(int(m.group(1), 16)))
            else:
                if string[i] not in Converter.escapes:
                    raise TomlDecodeError(self.parser.lineno,
                                          'Bad escape: \\%s' % string[i])
                tokens.append(Converter.escapes[string[i]])
                i += 1
        return ''.join(tokens)

    def convert(self, line=None, is_end=True):
        """Read the line content and return the converted value

        :param line: the line to feed to converter
        :param is_end: if set to True, will raise an error if
        the line has something remaining.
        """
        if line is not None:
            self.line = line
        if not self.line:
            raise TomlDecodeError(self.parser.lineno,
                                  'EOF is hit!')
        token = None
        self.line = self.line.lstrip()
        for key, pattern in self.patterns:
            m = pattern.match(self.line)
            if m:
                self.line = self.line[m.end():]
                handler = getattr(self, 'convert_%s' % key)
                token = handler(m)
                break
        else:
            raise TomlDecodeError(self.parser.lineno,
                                  'Parsing error: %r' % self.line)
        if is_end and not BLANK_RE.match(self.line):
            raise TomlDecodeError(self.parser.lineno,
                                  'Something is remained: %r' % self.line)
        return token

    def convert_blank(self, match):
        return None

    def convert_boolean(self, match):
        return match.group(1) == 'true'

    def convert_string(self, match):
        return self.unescape(match.group(1))

    def convert_lit_string(self, match):
        return match.group(1)

    def convert_integer(self, match):
        number = match.group(1)
        base = 10
        if number.startswith('0x'):
            base = 16
        elif number.startswith('0o'):
            base = 8
        elif number.startswith('0b'):
            base = 2
        return long(number.replace('_', ''), base)

    def convert_float(self, match):
        return float(match.group(1).replace('_', ''))

    def convert_datetime(self, match):
        date_string = match.group(1).replace('T', ' ')
        dt = datetime.datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
        if match.group(2):
            dt = dt.replace(microsecond=int(match.group(2)[1:]))
        if match.group(3):
            dt = dt.replace(tzinfo=TomlTZ(match.group(3)))
        return dt

    def convert_date(self, match):
        dt = datetime.datetime.strptime(match.group(1), '%Y-%m-%d')
        return dt.date()

    def convert_time(self, match):
        dt = datetime.datetime.strptime(match.group(1), '%H:%M:%S')
        if match.group(2):
            dt = dt.replace(microsecond=int(match.group(2)[1:]))
        return dt.time()

    def convert_multi_string(self, match):
        parts = []
        if not self.line.rstrip():
            parts.append('')
            self.line = self.parser._readline()
        skip_whitespace = False
        while True:
            if not self.line:
                raise TomlDecodeError(self.parser.lineno,
                                      'Missing closing quotes')
            m = self.string_end_re.match(self.line)
            if m:
                content = m.group(1)
                self.line = self.line[m.end():]
            else:
                content = self.line
                self.line = self.parser._readline()
            if skip_whitespace:
                content = content.lstrip()
            if content.rstrip() and content.rstrip()[-1] == '\\':
                content = content.rstrip()[:-1]
                skip_whitespace = True
            elif content.strip():
                skip_whitespace = False
            parts.append(content)
            if m:
                break

        return self.unescape(''.join(parts))

    def convert_multi_lit_string(self, match):
        parts = []
        if not self.line.rstrip():
            parts.append('')
            self.line = self.parser._readline()
        while True:
            if not self.line:
                raise TomlDecodeError(self.parser.lineno,
                                      'Missing closing quotes')
            m = self.lit_string_end_re.match(self.line)
            if m:
                content = m.group(1)
                self.line = self.line[m.end():]
            else:
                content = self.line
                self.line = self.parser._readline()
            parts.append(content)
            if m:
                break
        return ''.join(parts)

    def convert_list_begin(self, match):
        temp = []
        ele_type = None
        while True:
            if self.list_end_re.match(self.line):
                self.line = self.line[self.list_end_re.match(self.line).end():]
                break
            if self.sep_re.match(self.line):
                self.line = self.line[self.sep_re.match(self.line).end():]
                continue
            token = self.convert(is_end=False)
            if token is None:
                self.line = self.parser._readline().lstrip()
            else:
                if ele_type is None:
                    ele_type = type(token)
                else:
                    if ele_type != type(token):
                        raise TomlDecodeError(
                            self.parser.lineno,
                            'Element type %r is different from others(%r)'
                            % (type(token), ele_type))
                temp.append(token)
        return temp

    def convert_table_begin(self, match):
        temp = empty_inline_table(self.parser.dict_)
        while True:
            if self.table_end_re.match(self.line):
                self.line = self.line[
                    self.table_end_re.match(self.line).end():]
                break
            if self.sep_re.match(self.line):
                self.line = self.line[self.sep_re.match(self.line).end():]
                continue
            m = KEY_RE.match(self.line)
            if not m:
                raise TomlDecodeError(self.parser.lineno,
                                      'Key pair missing')
            self.line = self.line[m.end():]
            keys = self.parser.split_string(m.group(1), '.')
            value = self.convert(is_end=False)
            if value is None:
                raise TomlDecodeError(self.parser.lineno,
                                      'Value is missing: %r' % self.line)
            self.parser._store_table(keys[:-1], {keys[-1]: value}, data=temp)
        return temp


class Decoder(object):
    """The toml decoder class

    :param instream: a file object or string stream to be parsed
    :param dict_: (optional)the output type, defaults to native dict
    :param converter: (opitonal)the value converter, contains
        all data types specified in toml v0.4.0
    """
    def __init__(self, instream, dict_=dict, converter=None):
        self.dict_ = dict_
        self.data = self.dict_()
        if isinstance(instream, bytes):
            instream = instream.decode('utf-8')
        self.instream = StringIO(instream)
        if converter is None:
            converter = Converter(self)
        self.converter = converter
        self.lineno = 0

    def parse(self, data=None, table_name=None):
        """Parse the lines from index i

        :param data: optional, store the parsed result to it when specified
        :param table_name: when inside a table array, it is the table name
        """
        temp = self.dict_()
        sub_table = None
        is_array = False
        line = ''
        while True:
            line = self._readline()
            if not line:
                self._store_table(sub_table, temp, is_array, data=data)
                break       # EOF
            if BLANK_RE.match(line):
                continue
            if TABLE_RE.match(line):
                next_table = self.split_string(
                    TABLE_RE.match(line).group(1), '.', False)
                if table_name and not contains_list(next_table, table_name):
                    self._store_table(sub_table, temp, is_array, data=data)
                    break
                table = cut_list(next_table, table_name)
                if sub_table == table:
                    raise TomlDecodeError(self.lineno, 'Duplicate table name'
                                          'in origin: %r' % sub_table)
                else:       # different table name
                    self._store_table(sub_table, temp, is_array, data=data)
                    sub_table = table
                    is_array = False
            elif TABLE_ARRAY_RE.match(line):
                next_table = self.split_string(
                    TABLE_ARRAY_RE.match(line).group(1), '.', False)
                if table_name and not contains_list(next_table, table_name):
                    # Out of current loop
                    # write current data dict to table dict
                    self._store_table(sub_table, temp, is_array, data=data)
                    break
                table = cut_list(next_table, table_name)
                if sub_table == table and not is_array:
                    raise TomlDecodeError(self.lineno, 'Duplicate name of '
                                          'table and array of table: %r'
                                          % sub_table)
                else:   # Begin a nested loop
                    # Write any temp data to table dict
                    self._store_table(sub_table, temp, is_array, data=data)
                    sub_table = table
                    is_array = True
                    self.parse(temp, next_table)
            elif KEY_RE.match(line):
                m = KEY_RE.match(line)
                keys = self.split_string(m.group(1), '.')
                value = self.converter.convert(line[m.end():])
                if value is None:
                    raise TomlDecodeError(self.lineno, 'Value is missing')
                self._store_table(keys[:-1], {keys[-1]: value}, data=temp)
            else:
                raise TomlDecodeError(self.lineno,
                                      'Pattern is not recognized: %r' % line)
        # Rollback to the last line for next parse
        # This will do nothing if EOF is hit
        self.instream.seek(self.instream.tell() - len(line))
        self.lineno -= 1

    def _store_table(self, table_name, table, is_array=False, data=None):
        if not table and not table_name:
            return
        if data is None:
            data = self.data
        if table_name:
            for name in table_name[:-1]:
                data = data.setdefault(name, self.dict_())
                if not isinstance(data, self.dict_):
                    raise TomlDecodeError(self.lineno,
                                          'Not a dict: %r' % name)
            name = table_name[-1]
            if is_array:
                data = data.setdefault(name, [])
                if not isinstance(data, list):
                    raise TomlDecodeError(self.lineno,
                                          'Not a list: %r' % name)
                data.append(table.copy())
                table.clear()
                return
            else:
                data = data.setdefault(name, self.dict_())
                if not isinstance(data, self.dict_):
                    raise TomlDecodeError(self.lineno,
                                          'Not a dict: %r' % name)
        for k, v in table.items():
            if k in data:
                raise TomlDecodeError(self.lineno,
                                      'Duplicate key %r' % k)
            else:
                data[k] = v
        table.clear()

    def _readline(self):
        line = self.instream.readline()
        self.lineno += 1
        if isinstance(line, bytes):
            line = line.decode('utf-8')
        return line

    def split_string(self, string, splitter='.', allow_empty=True):
        """Split the string with respect of quotes"""
        i = 0
        rv = []
        need_split = False
        while i < len(string):
            m = re.compile(_KEY_NAME).match(string, i)
            if not need_split and m:
                i = m.end()
                body = m.group(1)
                if body[:3] == '"""':
                    body = self.converter.unescape(body[3:-3])
                elif body[:3] == "'''":
                    body = body[3:-3]
                elif body[0] == '"':
                    body = self.converter.unescape(body[1:-1])
                elif body[0] == "'":
                    body = body[1:-1]
                if not allow_empty and not body:
                    raise TomlDecodeError(
                        self.lineno,
                        'Empty section name is not allowed: %r' % string)
                rv.append(body)
                need_split = True
            elif need_split and string[i] == splitter:
                need_split = False
                i += 1
                continue
            else:
                raise TomlDecodeError(self.lineno,
                                      'Illegal section name: %r' % string)
        if not need_split:
            raise TomlDecodeError(
                self.lineno,
                'Empty section name is not allowed: %r' % string)
        return rv


def load(f, dict_=dict):
    """Load and parse toml from a file object
    An additional argument `dict_` is used to specify the output type
    """
    if not f.read:
        raise ValueError('The first parameter needs to be a file object, ',
                         '%r is passed' % type(f))
    return loads(f.read(), dict_)


def loads(content, dict_=dict):
    """Parse a toml string
    An additional argument `dict_` is used to specify the output type
    """
    if not isinstance(content, basestring):
        raise ValueError('The first parameter needs to be a string object, ',
                         '%r is passed' % type(content))
    decoder = Decoder(content, dict_)
    decoder.parse()
    return decoder.data
