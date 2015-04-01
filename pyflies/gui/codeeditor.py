import re
from PyQt4 import QtGui, QtCore


class CodeEditor(QtGui.QPlainTextEdit):

    def __init__(self, *args, **kwargs):
        super(CodeEditor, self).__init__(*args, **kwargs)
        self.highlighter = PyFliesHighlighter(self.document())

    def highlight_error(self, line):
        # TODO: Line highlight
        pass


class PyFliesHighlighter(QtGui.QSyntaxHighlighter):
    """
    Syntax highlighter for the pyFlies language.
    Based on Python syntax highlighter from
    https://wiki.python.org/moin/PyQt/Python%20syntax%20highlighting
    """
    # Python keywords
    keywords = [
        'and', 'or',
        'experiment', 'test', 'conditions', 'stimuli', 'screen', 'target',
        'structure',
        'output', 'responses',
        'all', 'fixation', 'error',
        'shape', 'sound', 'image',
        'duration', 'position', 'keep', 'fillColor', 'lineWidth',
        'practice', 'randomize'
    ]

    # Python operators
    operators = [
            '='
    ]

    # Python braces
    braces = [
        '\{', '\}', '\(', '\)', '\[', '\]',
    ]

    def __init__(self, document):
        QtGui.QSyntaxHighlighter.__init__(self, document)

        # Multi-line strings (expression, flag, style)
        self. multi_line_rules = [
            (QtCore.QRegExp("'''"), QtCore.QRegExp("'''"), 1,
             STYLES['string2']),
            (QtCore.QRegExp('"""'), QtCore.QRegExp('"""'), 2,
             STYLES['string2'])]

        rules = []

        # Keyword, operator, and brace rules
        rules += [(r'\b%s\b' % w, 0, STYLES['keyword'])
                  for w in PyFliesHighlighter.keywords]
        rules += [(r'%s' % o, 0, STYLES['operator'])
                  for o in PyFliesHighlighter.operators]
        rules += [(r'%s' % b, 0, STYLES['brace'])
                  for b in PyFliesHighlighter.braces]

        # All other rules
        rules += [
            # Tripple quoted strings
            (r"'''(.|\n)*'''", 0, STYLES['string']),
            (r'"""(.|\n)*"""', 0, STYLES['string']),

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

            # From '/*' until '*/'
            (r'\/\*(.|\n)*?\*\/', 0, STYLES['comment']),

            # Numeric literals
            (r'\b[+-]?[0-9]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?0[xX][0-9A-Fa-f]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\b', 0,
             STYLES['numbers']),
        ]

        # Build a regex object for each pattern
        self.rules = [(re.compile(pat, re.DOTALL), index, fmt)
                      for (pat, index, fmt) in rules]

    def highlightBlock(self, text):
        """Apply syntax highlighting to the given block of text.
        """
        print('Formating:', text)
        # Do other syntax formatting
        for regex, nth, format in self.rules:
            for match in regex.finditer(text):
                length = len(match.group(nth))
                self.setFormat(match.start(nth), length, format)

        # Do multi-line rules
        for multi_line_rule in self.multi_line_rules:
            in_multiline = self.match_multiline(text, *multi_line_rule)
            if in_multiline:
                break

    def match_multiline(self, text, start_delimiter, end_delimiter,
                        in_state, style):
        """Do highlighting of multi-line strings. ``delimiter`` should be a
        ``QRegExp`` for triple-single-quotes or triple-double-quotes, and
        ``in_state`` should be a unique integer to represent the corresponding
        state changes when inside those strings. Returns True if we're still
        inside a multi-line string when this function is finished.
        """
        # If inside triple-single quotes, start at 0
        if self.previousBlockState() == in_state:
            start = 0
            add = 0
        # Otherwise, look for the delimiter on this line
        else:
            start = start_delimiter.indexIn(text)
            # Move past this match
            add = start_delimiter.matchedLength()

        # As long as there's a delimiter match on this line...
        while start >= 0:
            # Look for the ending delimiter
            end = end_delimiter.indexIn(text, start + add)
            # Ending delimiter on this line?
            if end >= add:
                length = end - start + add + end_delimiter.matchedLength()
                self.setCurrentBlockState(0)
            # No; multi-line string
            else:
                self.setCurrentBlockState(in_state)
                length = len(text) - start + add
            # Apply formatting
            self.setFormat(start, length, style)
            # Look for the next match
            start = start_delimiter.indexIn(text, start + length)

        # Return True if still inside a multi-line string, False otherwise
        return self.currentBlockState() == in_state


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
    'self': format('black', 'italic'),
    'numbers': format('brown'),
}
