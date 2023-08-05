def collect_literal_block(lines, index):
    leading_space = lines[index].replace(lines[index].lstrip(), '')
    output = []
    while index < len(lines) and (lines[index].startswith(' ') or lines[index] == ''):
        output.append(lines[index])
        index += 1
    return '\n'.join(output), index