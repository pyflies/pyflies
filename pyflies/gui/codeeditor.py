import re
from PyQt4 import QtGui


class CodeEditor(QtGui.QPlainTextEdit):

    def __init__(self, *args, **kwargs):
        super(CodeEditor, self).__init__(*args, **kwargs)
        self.highlighter = PyFliesHighlighter(self.document())
        self.setLineWrapMode(self.NoWrap)

        font = QtGui.QFont("")
        font.setStyleHint(QtGui.QFont.TypeWriter)
        self.setFont(font)

    def highlight_error(self, line, col):
        cursor = self.textCursor()
        cursor.movePosition(QtGui.QTextCursor.Start)
        cursor.movePosition(QtGui.QTextCursor.NextBlock,
                            QtGui.QTextCursor.MoveAnchor, line-1)
        cursor.movePosition(QtGui.QTextCursor.NextCharacter,
                            QtGui.QTextCursor.MoveAnchor, col-1)
        self.setTextCursor(cursor)


class PyFliesHighlighter(QtGui.QSyntaxHighlighter):
    """
    Syntax highlighter for the pyFlies language.
    """
    keywords = [
        'and', 'or',
        'experiment', 'test', 'conditions', 'stimuli', 'screen', 'target',
        'structure',
        'output', 'responses',
        'all', 'fixation', 'error', 'correct',
        'practice', 'randomize'
    ]

    stimuli_types = [
        'shape', 'sound', 'image', 'text'
    ]

    stimuli_params = [
        'duration', 'position', 'keep', 'fillColor', 'lineWidth'
    ]

    operators = [
            '='
    ]

    braces = [
        '\{', '\}', '\(', '\)', '\[', '\]',
    ]

    def __init__(self, document):
        QtGui.QSyntaxHighlighter.__init__(self, document)

        # Multi-line rules (start expr., end expr., state,
        #                   style, style delimiters)
        multi_line_rules = [
            ("/\*", "\*/", 1, STYLES['string2'], True),
            ('"', '"', 2, STYLES['string2'], True),
            (r'\bscreen\b\s*(\w+)\s*{', '}', 3, STYLES['screen'], False),
        ]

        rules = []

        # Keyword, operator, and brace rules
        rules += [(r'\b%s\b' % w, 0, STYLES['keyword'])
                  for w in PyFliesHighlighter.keywords]
        rules += [(r'\b%s\b' % w, 0, STYLES['stimuli_types'])
                  for w in PyFliesHighlighter.stimuli_types]
        rules += [(r'\b%s\b' % w, 0, STYLES['stimuli_params'])
                  for w in PyFliesHighlighter.stimuli_params]
        rules += [(r'%s' % o, 0, STYLES['operator'])
                  for o in PyFliesHighlighter.operators]
        rules += [(r'%s' % b, 0, STYLES['brace'])
                  for b in PyFliesHighlighter.braces]

        # All other rules
        rules += [
            # Double-quoted string, possibly containing escape sequences
            (r'"[^"\\]*(\\.[^"\\]*)*"', 0, STYLES['string']),
            # Single-quoted string, possibly containing escape sequences
            (r"'[^'\\]*(\\.[^'\\]*)*'", 0, STYLES['string']),

            # 'test' followed by an identifier
            (r'\btest\b\s*(\w+)', 1, STYLES['def']),
            # 'screen' followed by an identifier
            (r'\bscreen\b\s*(\w+)', 1, STYLES['def']),
            # 'target' followed by an identifier
            (r'\btarget\b\s*(\w+)', 1, STYLES['def']),

            # From '//' until a newline
            (r'\/\/[^\n]*', 0, STYLES['comment']),

            # Numeric literals
            (r'\b[+-]?[0-9]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?0[xX][0-9A-Fa-f]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\b', 0,
             STYLES['numbers']),
        ]

        # Build a regex object for each pattern
        self.rules = [(re.compile(pat), index, fmt)
                      for (pat, index, fmt) in rules]
        self.multiline_rules = [
            (re.compile(pat_start), re.compile(pat_end), state, style,
             style_delimiters)
            for (pat_start, pat_end, state, style,
                 style_delimiters) in multi_line_rules]

    def highlightBlock(self, text):
        """Apply syntax highlighting to the given block of text.
        """
        # Do other syntax formatting
        for regex, nth, format in self.rules:
            for match in regex.finditer(text):
                length = len(match.group(nth))
                self.setFormat(match.start(nth), length, format)

        self.setCurrentBlockState(0)

        # Do multi-line rules
        for multi_line_rule in self.multiline_rules:
            in_multiline = self.highlight_multiline(text, *multi_line_rule)
            if in_multiline:
                break

    def highlight_multiline(self, text, start_delimiter, end_delimiter,
                            in_state, style, style_delimiters):
        prev_state = self.previousBlockState()

        if prev_state > 0 and prev_state != in_state:
            # If there is multiline state but not for current in_state return
            # and continue to the next multiline highlight.
            return False

        curr_index = 0
        if prev_state > 0:
            # If in multiline try first to find end delimiter.
            end_match = end_delimiter.search(text)

            # If not found we style whole line and change the state of
            # the line to notify higlighter that we are still in multiline
            # state.
            if not end_match:
                self.setFormat(0, len(text), style)
                self.setCurrentBlockState(in_state)
                return True
            else:
                # If found style to end delimiter, change current position
                # index and continue.
                end_match_index = end_match.start()
                if style_delimiters:
                    text_len = end_match_index + len(end_match.group())
                else:
                    text_len = end_match_index
                self.setFormat(0, text_len, style)
                curr_index = text_len

        start_match = start_delimiter.search(text, curr_index)
        while start_match:
            start_index = start_match.start()
            end_match = end_delimiter.search(text, start_index +
                                             len(start_match.group()))

            if not end_match:
                self.setCurrentBlockState(in_state)
                if style_delimiters:
                    text_len = len(text) - start_index
                    self.setFormat(start_index, text_len, style)
                else:
                    text_len = len(text) - start_index - \
                                len(start_match.group())
                    self.setFormat(start_index + len(start_match.group()),
                                   text_len, style)
                return True
            else:
                if style_delimiters:
                    text_len = end_match.start() - start_index + \
                                len(end_match.group())
                    self.setFormat(start_index, text_len, style)
                else:
                    text_len = end_match.start() - start_index
                    self.setFormat(start_index + len(start_index.group()),
                                   text_len, style)

                start_match = start_delimiter.search(text,
                                                     start_index + text_len)


def format(color, style=''):
    """Return a QTextCharFormat with the given attributes.
    """
    _color = QtGui.QColor()
    _color.setNamedColor(color)

    _format = QtGui.QTextCharFormat()
    _format.setForeground(_color)
    if 'bold' in style:
        _format.setFontWeight(QtGui.QFont.Bold)
    if 'italic' in style:
        _format.setFontItalic(True)

    return _format


# Syntax styles that can be shared by all languages
STYLES = {
    'keyword': format('blue'),
    'operator': format('red'),
    'brace': format('darkGray'),
    'def': format('black', 'bold'),
    'string': format('magenta'),
    'string2': format('darkMagenta'),
    'comment': format('darkGreen', 'italic'),
    'numbers': format('brown'),
    'screen': format('darkGreen'),
    'stimuli_types': format('darkRed'),
    'stimuli_params': format('darkGray'),
}
