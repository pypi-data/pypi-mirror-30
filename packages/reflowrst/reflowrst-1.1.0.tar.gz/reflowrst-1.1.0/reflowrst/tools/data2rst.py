import math

def getSpan(spans, row, column):
    """checks if a row,column is in spans"""
    for i in range(len(spans)):
        if [row, column] in spans[i]:
            return spans[i]
    return None


def lineBreak(count, symbol):
    """makes a string that is count long of symbol"""
    x = ""
    for i in range(0, count):
        x = x + symbol
    return x

def getSpanColumnCount(span):
    """Gets the number of columns inluded in a span"""
    columns = 1
    first_column = span[0][1]
    for i in range(len(span)):
        if span[i][1] > first_column:
            columns += 1
            first_column = span[i][1]
    return columns

def sortSpans(spans):
    """Ensure the first cell of each span is the text cell"""
    for span in range(len(spans)):
        spans[span] = sorted(spans[span])
    return spans

def addCushions(table):
    """adds space to start and end of each item in a list of lists"""
    for row in range(len(table)):
        for column in range(len(table[row])):
            lines = table[row][column].split("\n")
            for i in range(len(lines)):
                if not lines[i] == "":
                    lines[i] = " " + lines[i].rstrip() + " "
            table[row][column] = "\n".join(lines)
    return table

def isOnly(text, char_list):
    text = text.strip()
    if text == '':
        return False
    for i in range(len(text)):
        if text[i] not in char_list:
            return False
    return True

class TableTypeError(Exception):
    """Raised if a Table is not a List of Lists"""

class TableContentError(Exception):
    """Raised if a Table is empty or has inconsistent column counts"""

class SpanError(Exception):
    """
    Raised if the spans in any spangroup are not touching or
    the span is not square
    """


class Cell():
    """Holds the text and data for an rst text cell"""
    def __init__(self, text, row, column, row_count, column_count):
        self.text = text
        self.row = row
        self.column = column
        self.row_count = row_count
        self.column_count = column_count

    @property
    def left_sections(self):
        lines = self.text.split('\n')
        sections = 0
        for i in range(len(lines)):
            if lines[i].startswith('+'):
                sections += 1
        return sections - 1

    @property
    def right_sections(self):
        lines = self.text.split('\n')
        sections = 0
        for i in range(len(lines)):
            if lines[i].endswith('+'):
                sections += 1
        return sections - 1

    @property
    def top_sections(self):
        top_line = self.text.split('\n')[0]
        return len(top_line.split('+')) - 2

    @property
    def bottom_sections(self):
        bottom_line = self.text.split('\n')[-1]
        return len(bottom_line.split('+')) - 2

    @property
    def is_header(self):
        bottom_line = self.text.split('\n')[-1]
        return isOnly(bottom_line, ['+', '='])

    def h_center_cell(self):
        lines = self.text.split('\n')
        cell_width = len(lines[0]) - 2

        truncated_lines = []
        for i in range(1, len(lines) - 1):
            truncated = lines[i][2:len(lines[i]) - 2].rstrip()
            truncated_lines.append(truncated)

        truncated_lines.append('')
        truncated_lines.insert(0, '')

        max_line_length = len(max(truncated_lines, key=len))
        remainder = cell_width - max_line_length
        left_width = math.floor(remainder / 2)
        left_space = lineBreak(left_width, ' ')

        for i in range(len(truncated_lines)):
            truncated_lines[i] = left_space + truncated_lines[i]
            right_width = cell_width - len(truncated_lines[i])
            truncated_lines[i] += lineBreak(right_width, ' ')


        for i in range(1, len(lines) - 1):
            lines[i] = lines[i][0] + truncated_lines[i] + lines[i][-1]

        self.text = '\n'.join(lines)
        self.v_center_cell()

    def v_center_cell(self):
        lines = self.text.split('\n')
        cell_width = len(lines[0]) - 2

        truncated_lines = []
        for i in range(1, len(lines) - 1):
            truncated = lines[i][1:len(lines[i]) - 1]
            truncated_lines.append(truncated)

        total_height = len(truncated_lines)

        above_trash_count = 0
        for i in range(len(truncated_lines)):
            if truncated_lines[i].rstrip() == '':
                above_trash_count += 1
            else:
                break

        below_trash_count = 0
        for i in reversed(range(len(truncated_lines))):
            if truncated_lines[i].rstrip() == '':
                below_trash_count += 1
            else:
                break

        significant_lines = truncated_lines[above_trash_count: len(truncated_lines) - below_trash_count]

        remainder = total_height - len(significant_lines)
        blank = lineBreak(cell_width, ' ')
        above_height = math.floor(remainder / 2)
        for i in range(0, above_height):
            significant_lines.insert(0, blank)

        below_height = math.ceil(remainder / 2)
        for i in range(0, below_height):
            significant_lines.append(blank)

        significant_lines.insert(0, '')
        significant_lines.append('')

        for i in range(1, len(lines) - 1):
            lines[i] = lines[i][0] + significant_lines[i] + lines[i][-1]

        self.text = '\n'.join(lines)


    def __lt__(self, other):
        """For sorting instances of this class"""
        return [self.row, self.column] < [other.row, other.column]

    def mergeableDirection(self, other):
        """Determines the direction in which two cells can be merged"""
        self_left = self.column
        self_right = self.column + self.column_count
        self_top = self.row
        self_bottom = self.row + self.row_count

        other_left = other.column
        other_right = other.column + other.column_count
        other_top = other.row
        other_bottom = other.row + other.row_count

        if (self_right == other_left and self_top == other_top and
                self_bottom == other_bottom and self.right_sections >= other.left_sections):
            return "RIGHT"
        elif (self_left == other_left and self_right == other_right and
                self_top == other_bottom and self.top_sections >= other.bottom_sections):
            return "TOP"
        elif (self_left == other_left and
              self_right == other_right and
              self_bottom == other_top and self.bottom_sections >= other.top_sections):
            return "BOTTOM"
        elif (self_left == other_right and
              self_top == other_top and
              self_bottom == other_bottom and self.left_sections >= other.right_sections):
            return "LEFT"
        else:
            return "NONE"

    def merge(self, other):
        """attempts to merge two cells"""

        self_lines = self.text.split("\n")
        other_lines = other.text.split("\n")

        if self.mergeableDirection(other) == "RIGHT":
            for i in range(len(self_lines)):
                self_lines[i] = self_lines[i] + other_lines[i][1::]
            self.text = "\n".join(self_lines)
            self.column_count += other.column_count
            return True
        elif self.mergeableDirection(other) == "TOP":
            if self_lines[0].count('+') > other_lines[-1].count('+'):
                other_lines.pop(-1)
            else:
                self_lines.pop(0)
            other_lines.extend(self_lines)
            self.text = "\n".join(other_lines)
            self.row_count += other.row_count
            self.row = other.row
            self.column = other.column
            return True
        elif self.mergeableDirection(other) == "BOTTOM":
            if self_lines[-1].count('+') > other_lines[0].count('+') or self.is_header:
                other_lines.pop(0)
            else:
                self_lines.pop(-1)
            self_lines.extend(other_lines)
            self.text = "\n".join(self_lines)
            self.row_count += other.row_count
            return True
        elif self.mergeableDirection(other) == "LEFT":
            for i in range(len(self_lines)):
                self_lines[i] = other_lines[i][0:-1] + self_lines[i]
            self.text = "\n".join(self_lines)
            self.column_count += other.column_count
            self.row = other.row
            self.column = other.column
            return True
        else:
            return False

def getLongestLineLength(text):
    """Get the length longest line in a paragraph"""
    lines = text.split("\n")
    length = 0
    for i in range(len(lines)):
        if len(lines[i]) > length:
            length = len(lines[i])
    return length


def getSpanRowCount(span):
    """Gets the number of rows included in a span"""
    rows = 1
    first_row = span[0][0]
    for i in range(len(span)):
        if span[i][0] > first_row:
            rows += 1
            first_row = span[i][0]
    return rows

def getSpanColumnCount(span):
    """Gets the number of rows included in a span"""
    first_column = span[0][1]
    column = first_column
    for pair in span:
        if pair[1] > column:
            column = pair[1]
    return (column - first_column) + 1

def getTotalSpanHeight(span, heights):
    """Sum the row heights of a span"""
    start_row = span[0][0]
    row_count = getSpanRowCount(span)
    total_height = 0
    for i in range(start_row, start_row + row_count):
        total_height += heights[i]
    total_height += row_count - 1
    return total_height


def getTotalSpanWidth(span, widths):
    """Sum the widths of a span"""
    start_column = span[0][1]
    column_count = getSpanColumnCount(span)
    total_width = 0
    for i in range(start_column, start_column + column_count):
        total_width += widths[i]
    total_width += column_count - 1
    return total_width


def mergeCells(cells):
    """Loop through list of cells and piece them together one by one"""
    current = 0
    while len(cells) > 1:
        count = 0
        while count < len(cells):
            if cells[current].merge(cells[count]):
                if current > count:
                    current -= 1
                cells.pop(count)
            else:
                count += 1
        current += 1
        if current >= len(cells):
            current = 0
    return cells[0].text


def makeTextCell(table, span, widths, heights, use_headers):
    """Creates an rst text Cell"""
    width = getTotalSpanWidth(span, widths)
    height = getTotalSpanHeight(span, heights)
    text_row = span[0][0]
    text_column = span[0][1]
    text = table[text_row][text_column]

    lines = text.split("\n")
    for i in range(len(lines)):
        width_difference = width - len(lines[i])
        lines[i] = lines[i] + lineBreak(width_difference, " ")

    height_difference = height - len(lines)
    empty_lines = []
    for i in range(0, height_difference):
        empty_lines.append(lineBreak(width, " "))
    lines.extend(empty_lines)

    output = ["+" + lineBreak(width, "-") + "+"]
    for i in range(0, height):
        output.append("|" + lines[i] + "|")

    if use_headers and span[0][0] == 0:
        symbol = "="
    else:
        symbol = "-"
    output.append("+" + lineBreak(width, symbol) + "+")

    text = "\n".join(output)
    row_count = getSpanRowCount(span)
    column_count = getSpanColumnCount(span)
    cell = Cell(text, text_row, text_column, row_count, column_count)

    return cell


def getHeights(table, spans):
    """get the heights of the rows of the output table"""
    span_remainders = {}
    for span in spans:
        span_remainders[str(span)] = 0

    heights = []
    for row in table:
        heights.append(-1)

    for row in range(len(table)):
        for column in range(len(table[row])):
            text = table[row][column]
            span = getSpan(spans, row, column)
            row_count = getSpanRowCount(span)
            height = len(text.split('\n'))
            if row_count == 1 and height > heights[row]:
                heights[row] = height

    for row in range(len(table)):
        for column in range(len(table[row])):
            span = getSpan(spans, row, column)
            row_count = getSpanRowCount(span)
            if row_count > 1:
                text_row = span[0][0]
                text_column = span[0][1]
                text = table[text_row][text_column]
                height = len(text.split('\n')) - (row_count - 1)
                add_row = 0
                while height > sum(heights[text_row:text_row + row_count]):
                    heights[text_row + add_row] += 1
                    if add_row + 1 < row_count:
                        add_row += 1
                    else:
                        add_row = 0
    return heights

def getWidths(table, spans):
    """Get the widths of the columns of the output table"""

    widths = []
    for column in table[0]:
        widths.append(3)

    for row in range(len(table)):
        for column in range(len(table[row])):
            span = getSpan(spans, row, column)
            column_count = getSpanColumnCount(span)
            if column_count == 1:
                text_row = span[0][0]
                text_column = span[0][1]
                text = table[text_row][text_column]
                length = getLongestLineLength(text)
                if length > widths[column]:
                    widths[column] = length

    for row in range(len(table)):
        for column in range(len(table[row])):
            span = getSpan(spans, row, column)
            column_count = getSpanColumnCount(span)
            if column_count > 1:
                text_row = span[0][0]
                text_column = span[0][1]
                text = table[text_row][text_column]
                length = getLongestLineLength(text)
                end_column = text_column + column_count
                available_space = sum(widths[text_column: end_column])
                available_space += column_count - 1
                while length > available_space:
                    for i in range(text_column, end_column):
                        widths[i] += 1
                        available_space = sum(widths[text_column: end_column])
                        available_space += column_count - 1
                        if length <= available_space:
                            break
    return widths


def convertToSpans(table, spans):
    """Converts all cells to spans"""
    new_spans = []
    for row in range(len(table)):
        for column in range(len(table[row])):
            span = getSpan(spans, row, column)
            if not span:
                new_spans.append([[row, column]])
    new_spans.extend(spans)
    new_spans = list(sorted(new_spans))
    return new_spans

def checkTable(table):
    """Checks to make sure that each row has the same number of columns"""
    if not type(table) is list:
        raise(TableTypeError("Table must be a list of lists"))
    if len(table) == 0:
        raise(TableContentError("Table must contain at least one row and one column"))
    for i in range(len(table)):
        if not type(table[i]) is list:
            raise(TableTypeError("Table must be a list of lists of strings"))
        if not len(table[i]) == len(table[0]):
            raise(TableContentError("Each row must have the same number of columns"))


def checkSpan(span):
    """Check the spans in a spangroup"""
    if not type(span) is list:
        raise(SpanError("Spans must be a list/tuple of lists"))
    for pair in span:
        if not type(pair) is list:
            raise(SpanError("Spans must be a list/tuple of lists"))
        if not len(pair) == 2:
            raise(SpanError("Spans must be a [Row, Column] pair of integers"))

    total_rows = getSpanRowCount(span)
    total_columns = getSpanColumnCount(span)

    if not len(span) == total_rows * total_columns:
        raise SpanError('Somethings wrong with the span group: ' + str(span))

    checked = [span.pop(0)]

    while len(span) > 0:
        row = span[0][0]
        col = span[0][1]
        matched = False

        for i in range(len(checked)):
            if row == checked[i][0] and abs(col - checked[i][1]) == 1:
                matched = True

            elif abs(row - checked[i][0]) == 1 and col == checked[i][1]:
                matched = True

        if matched:
            checked.append(span.pop(0))

        else:
            checked.extend(span)
            raise SpanError('Somethings wrong with the span group: ' + str(checked))

def data2rst(table, spans=[[[0, 0]]], use_headers=True, center_cells=False, center_headers=False):
    checkTable(table)

    for row in range(len(table)):
        for column in range(len(table[row])):
            table[row][column] = str(table[row][column])

    table = addCushions(table)
    spans = sortSpans(spans)

    for span in spans:
        span = list(span)
        checkSpan(span)

    spans = convertToSpans(table, spans)

    widths = getWidths(table, spans)
    heights = getHeights(table, spans)

    cells = []
    for span in spans:
        cell = makeTextCell(table, span, widths, heights, use_headers)
        cells.append(cell)
    cells = list(sorted(cells))

    if center_cells:
        for cell in cells:
            if not cell.is_header:
                cell.h_center_cell()

    if center_headers:
        for cell in cells:
            if cell.is_header:
                cell.h_center_cell()

    output = mergeCells(cells)

    return output