def alpha_in_word(word):
    for char in word:
        if char.isalpha():
            return True
    return False

def is_citation(lines, index):
    '''this must be called after the footnote checker'''
    if not lines[index].lstrip().startswith('.. ['):
        return False

    words = lines[index].lstrip().split(' ')
    if not words[1].endswith(']'):
        return False
    if alpha_in_word(words[1]):
        return True

    return False