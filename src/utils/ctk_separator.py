from customtkinter import CTkProgressBar
from typing import Any, Optional, Union, Tuple


def CTkWindowSeparator(
    master: Any,
    size: int = 2,
    length: int = 75,
    multiply: int = 200,
    orientation: str = "Horizontal",
    color: Optional[Union[str, Tuple[str, str]]] = None,
):
    SetColor = color
    LineLength = length / 100 * multiply
    if orientation == "Horizontal":
        Separator = CTkProgressBar(master=master, height=size, width=LineLength)
    else:
        Separator = CTkProgressBar(master=master, width=size, height=LineLength)
    Separator.configure(progress_color=SetColor, fg_color=SetColor)
    return Separator
