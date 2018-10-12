import datetime

def set_spacing(*layouts, h=0, v=0):
    for layout in layouts:
        layout.setHorizontalSpacing(h)
        layout.setVerticalSpacing(v)

def get_photo_number(path_to_photo):
    return path_to_photo.split('/')[-1]

def str_to_date(str_date):
    year, month, day = [int(i) for i in str_date.split('/')]
    return datetime.date(year, month, day)

def format_date(date):
    """
    Format date from 'yyyy-mm-dd' to 'dd.mm.yyyy'
    :param date:
    :return: str
    """
    date = date.split('-')
    date.reverse()
    return '.'.join(date)

def title_text(line_edit):
    text = line_edit.text()
    if len(text) == 1:
        line_edit.setText(text.title())