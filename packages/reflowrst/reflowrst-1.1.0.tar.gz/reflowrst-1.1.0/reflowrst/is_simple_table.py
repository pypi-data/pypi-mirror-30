from .tools import is_only

def is_simple_table(lines, index):
    '''This algorithm requires that there be no blank lines inside your table'''
    current_index = index
    if is_only(lines[current_index], ['=', ' ']):
        count = 1
        top_line = lines[current_index]
        current_index += 1
        while current_index < len(lines) and not lines[current_index] == '':
            if lines[current_index] == top_line:
                count += 1
            current_index += 1
        if count == 3:
            return True
    else:
        return False