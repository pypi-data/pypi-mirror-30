from sys import stdout
from argparse import ArgumentParser, FileType
try:
    from markdown import markdown
except ImportError:
    markdown = None

html_header = """<!doctype html>
<html>
<head>
<title>Tabmaker - %s</title>
<style>
%s</style>
</head>
<body>
"""

parser = ArgumentParser()

parser.add_argument(
    'in_file',
    metavar='FILE',
    type=FileType('r'),
    help='The file to convert'
)
parser.add_argument(
    'out_file',
    nargs='?',
    metavar='FILE',
    type=FileType('w'),
    default=stdout,
    help='The file to write the output to (defaults to stdout)'
)
parser.add_argument(
    '--html',
    action='store_true',
    help='Output as HTML'
)
parser.add_argument(
    '--style-sheet',
    type=FileType('r'),
    default=None,
    help='The stylesheet to use'
)
parser.add_argument(
    '-p',
    '--pad_char',
    metavar='CHARACTER',
    help='The character to use for padding'
)


def main():
    """Main entry point."""
    args = parser.parse_args()
    if args.html and markdown is None:
        print('Cannot output as HTML, markdown is not available.')
        raise SystemExit
    if args.pad_char is None:
        if args.html:
            args.pad_char = '&nbsp;'
        else:
            args.pad_char = ' '
    output = []  # Use '\n'.join() to make text.
    flines = args.in_file.readlines()
    for l in flines:
        line = ''
        grab = False  # Set to True when we're grabbing chords
        chords = ''
        chord_length = 0
        l = l.replace('\n', '')
        for c in l:
            if c == '[':
                while chord_length > 0:
                    line += '.'
                    chord_length -= 1
                grab = True
            elif c == ']':
                grab = 0
            else:
                if grab:
                    chord_length += 1
                    chords += c
                else:
                    if not chord_length:
                        chords += args.pad_char
                    else:
                        chord_length -= 1
                    line += c
        if chords.strip(args.pad_char):
            output.append(chords)
        if args.html:
            output.append('')
        output.append(line)
        if args.html:
            output.append('')
    output = '\n'.join(output)
    if args.html:
        if args.style_sheet is None:
            style = ''
        else:
            style = args.style_sheet.read()
        output = markdown(output)
        output += '\n</body>\n</html>'
        output = (
            html_header % (
                args.in_file.name,
                style
            )
        ) + output
    args.out_file.write(output)


if __name__ == '__main__':
    main()
