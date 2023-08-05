from .tools import is_only

def is_transition(lines, index):
    transition_characters = [
        '~',
        '`',
        '!',
        '@',
        '#',
        '$',
        '%',
        '^',
        '&',
        '*',
        '(',
        ')',
        '-',
        '_',
        '+',
        '=',
        '{',
        '[',
        ']'
        '}'
        ';',
        ':',
        ',',
        '<',
        '.',
        '>',
        '?',
        '/',
        '|',
        '\\'
    ]
    for character in transition_characters:
        if is_only(lines[index], character) and len(lines[index]) >= 4:
            return True

    return False