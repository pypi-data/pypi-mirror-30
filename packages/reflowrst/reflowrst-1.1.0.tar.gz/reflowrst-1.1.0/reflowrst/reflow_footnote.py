from .reflow_paragraph import reflow_paragraph

def reflow_footnote(text, space):
    leading_space = text.replace(text.lstrip(), '')
    text = text.lstrip()[2::].lstrip()

    paragraph = reflow_paragraph(text, space, leading_space + '   ')
    return leading_space + '.. ' + paragraph.lstrip()