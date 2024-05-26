def walk_widgets(parent):
    """Generator function to walk through all child widgets of a given parent widget."""
    for child in parent.winfo_children():
        yield child
        if child.winfo_children():
            yield from walk_widgets(child)
