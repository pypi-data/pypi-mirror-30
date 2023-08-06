from bs4.element import ResultSet   # beautifulsoup4 module
from bs4.element import Tag
from bs4.element import NavigableString


def _indent(depth):
    return '    ' * depth

def _dump_dom(dom, i, strip_text, max_depth, depth=0):
    lines = []
    if isinstance(dom, NavigableString):
        if strip_text:
            lines.append('{}[{}] Text({})'.format(_indent(depth), i, dom.strip()))
        else:
            lines.append('{}[{}] Text({})'.format(_indent(depth), i, dom.replace('\n', '\\n').replace('\t', '\\t')))
    else:
        lines.append('{}[{}] <{}> {} Contents({})'.format(_indent(depth), i, dom.name, dom.attrs, len(dom.contents)))
    
    if depth+1 >= max_depth and isinstance(dom, Tag):
        lines.append('{} [.] ...'.format(_indent(depth+1)))
    elif isinstance(dom, Tag):
        for i, d in enumerate(dom.contents):
            lines += _dump_dom(d, i, strip_text, max_depth, depth+1)
    
    return lines

def dump_dom(dom, strip_text=True, max_depth=6):
    lines = []
    if isinstance(dom, ResultSet):
        lines.append('bs4.element.ResultSet size({})'.format(len(dom)))
        for i, d in enumerate(dom):
            lines += _dump_dom(d, i, strip_text, max_depth)
    elif isinstance(dom, Tag):
        lines += _dump_dom(dom, 0, strip_text, max_depth)
    else:
        lines.append(str(dom))

    return '\n'.join(lines)


if __name__ == '__main__':
    pass
