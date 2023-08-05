def collect_citation(lines, index):
    output = []
    output.append(lines[index])
    index += 1

    while index < len(lines):
        if (
          not lines[index] == '' and
          not lines[index].lstrip().startswith('.. ')
        ):
            output.append(lines[index].lstrip())
            index += 1
        else:
            return ' '.join(output), index
    return ' '.join(output), index