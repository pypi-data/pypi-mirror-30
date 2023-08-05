from .tools import simple2data
from .tools import data2simplerst

def collect_simple_table(lines, index):
    output = []
    top_line = lines[index]
    while index < len(lines) and not lines[index] == '':
        output.append(lines[index])
        index += 1

    text = '\n'.join(output)
    table, spans, use_headers, headers_row = simple2data(text)
    simple_table = data2simplerst(table, spans, use_headers, headers_row)

    return simple_table, index