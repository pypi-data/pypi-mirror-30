from .is_field import is_field
from .tools import get_field_name
from .tools import space_fill

def collect_field(lines, index, interspace):
    output = []
    words = lines[index].strip().split(' ')

    field_name, words = get_field_name(words)

    leading_space = lines[index].replace(lines[index].lstrip(), '')
    first_line = leading_space + field_name + interspace + ' '.join(words).strip()
    output.append(first_line)

    lspace = leading_space + space_fill(len(field_name), ' ') + interspace

    index += 1
    new_lined = False
    while index < len(lines):
        if (not is_field(lines, index) and
                not lines[index] == '' and lines[index].startswith(lspace)):
            if not new_lined:
                output.append(lines[index].lstrip() + ' ')
            else:
                output.append(lspace + lines[index].lstrip() + ' ')
                new_lined = False
            index += 1
        elif not is_field(lines, index) and index < len(lines) - 1 and lines[index + 1].startswith(leading_space + ' '):
            output.append('\n')
            output.append(lines[index].lstrip())
            new_lined = True
            index += 1
        else:
            return ' '.join(output), index
    return ''.join(output), index
