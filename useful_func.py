import datetime

def set_spacing(*layouts, h=0, v=0):
    for layout in layouts:
        layout.setHorizontalSpacing(h)
        layout.setVerticalSpacing(v)

def disable_widget(*widgets):
    for widget in widgets:
        widget.setDisabled(True)

def enable_widget(*widgets):
    for widget in widgets:
        widget.setEnabled(True)

def get_photo_number(path_to_photo):
    return path_to_photo.split('/')[-1]

def str_to_date(str_date):
    year, month, day = [int(i) for i in str_date.split('/')]
    return datetime.date(year, month, day)
