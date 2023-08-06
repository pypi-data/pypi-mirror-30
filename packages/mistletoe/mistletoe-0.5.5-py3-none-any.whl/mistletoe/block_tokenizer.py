"""
Block-level tokenizer for mistletoe.
"""


class MismatchException(Exception):
    def __init__(self, lines=None):
        super().__init__()
        self.lines = lines


class FileWrapper:
    def __init__(self, lines):
        self.lines = self.normalize(lines)
        self._index = -1
        self._anchor = 0

    def __next__(self):
        self._index += 1
        if self._index < len(self.lines):
            return self.lines[self._index]
        raise StopIteration

    def __iter__(self):
        return self

    def __repr__(self):
        return repr(self.lines[self._index:])

    def anchor(self):
        self._anchor = self._index

    def reset(self):
        self._index = self._anchor

    def peek(self):
        if self._index + 1 < len(self.lines):
            return self.lines[self._index+1]
        return None

    @staticmethod
    def normalize(lines):
        line_buffer = []
        code_fence = ''
        for line in lines:
            if line.startswith(('```', '~~~')):
                if not code_fence:
                    line_buffer.append('\n')
                    code_fence = line[:3]
                elif line.startswith(code_fence):
                    code_fence = ''
            line_buffer.append(line.replace('\t', '    ').replace('\r\n', '\n'))
        return line_buffer


def tokenize(iterable, token_types, root=None):
    """
    Searches for token_types in iterable, and applies fallback_token
    to lines in between.

    Args:
        content (list[str]): user input lines to be parsed.
        token_types (list): a list of block-level token constructors.
        fallback_token (block_token.BlockToken): token for unmatched lines.

    Yields:
        block-level token instances.
    """
    lines = FileWrapper(iterable)
    for line in lines:
        for token_type in token_types:
            try:
                if token_type.start(line):
                    content = [line]
                    content.extend(token_type.read(lines))
                    token = token_type(content)
                    if root and hasattr(token, 'store_footnotes'):
                        token.store_footnotes(root)
                    else:
                        yield token
                    break
            except MismatchException as e:
                if e.lines is not None:
                    content = [line]
                    content.extend(e.lines)
                    yield token_types[-1](content)
                    break

