def is_literal_block(lines, index):
    if index == 0:
        return False
    if not lines[index].startswith(' '):
        return False
    if lines[index - 1] != '':
        return False

    current_index = index - 1

    while current_index > 0 and lines[current_index] == '':
        current_index -= 1

    if lines[current_index].endswith('::'):
        return True

    return False