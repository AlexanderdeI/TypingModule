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
