def collect_line_block(lines, index):
    leading_space = lines[index].replace(lines[index].lstrip(), '')
    output = []
    while index < len(lines) and (lines[index].startswith(leading_space + '| ') or lines[index] == leading_space + '|'):
        output.append(lines[index])
        index += 1
    return '\n'.join(output), index