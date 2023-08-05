def other_colon_present(words):
    for word in words:
        if word.endswith(':') and not word.endswith('\\:'):
            return True
    return False

def is_field(lines, index):
    words = lines[index].lstrip().split(' ')
    if not words[0].startswith(':'):
        return False

    if not other_colon_present(words):
        return False

    elif not words[0] == '::':
        return True
    else:
        return False