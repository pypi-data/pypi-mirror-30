def is_line_block(lines, index):
    if lines[index].lstrip().startswith('| '):
        return True
    elif lines[index].lstrip() == '|':
        return True
    return False