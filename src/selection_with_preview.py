import os
import sys
from typing import Callable, Iterable, Literal

import urwid


class FocusChangeAwareListBox(urwid.ListBox):
    """List box that executes a callback each time focus inside changes"""
    def __init__(self, body: urwid.ListWalker | Iterable[urwid.Widget], callback):
        super().__init__(body)
        self._focus_callback = callback

    def change_focus(self, size: tuple[int, int], position,
            offset_inset: int = 0, coming_from: Literal["above", "below"] | None = None,
            cursor_coords: tuple[int, int] | None = None, snap_rows: int | None = None,
    ) -> None:
        self._focus_callback(self.body[position])
        return super().change_focus(size, position, offset_inset, coming_from, cursor_coords, snap_rows)


class SelectionWithPreview(urwid.WidgetWrap):
    def __init__(
            self, options: Iterable[str], preview: Callable[[str], str],
            options_title: str = "Options", preview_title: str = "Preview"
        ):
        self._options = [
            urwid.CheckBox(f) for f in options
        ]
        list_walker = urwid.SimpleFocusListWalker([
            urwid.AttrMap(box, None, focus_map="reversed") for box in self._options
        ])

        def _on_focus_change(wrapped_button):
            self.preview_text.set_text(preview(wrapped_button._original_widget.get_label()))

        file_list_box = urwid.LineBox(
            FocusChangeAwareListBox(list_walker, callback=_on_focus_change),
            title=options_title
        )
        DEFAULT_TEXT = (("/"*200) + "\n") * 80  # TODO: Replace this with urwid.Filler
        self.preview_text = urwid.Text(
            DEFAULT_TEXT, wrap="clip"
        )
        preview_box = urwid.LineBox(
            urwid.Scrollable(self.preview_text), title=preview_title
        )

        self.columns = urwid.Columns(
            [("weight", 0.3, file_list_box), ("weight", 0.7, preview_box)],
            dividechars=1,
        )
        super().__init__(self.columns)
        if self._options:
            _on_focus_change(list_walker[0])


    def selected(self) -> list[str]:
        return [box.get_label() for box in self._options if box.state]

