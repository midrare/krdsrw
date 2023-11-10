from . import datastore


class FontPrefs:
    def __init__(self, _value: datastore.NamedValue):
        assert (
            not _value or _value.name == datastore.names.FONT_PREFS
        ), "wrong value class"
        # NamedValue -> FixedMap -> TemplatizedDict[font.prefs]
        self._value: datastore.NamedValue = _value

    @property
    def type_face(self) -> None | str:
        v = self._value.value.value.get(datastore.keys.FONT_PREFS_TYPEFACE)
        return v.value if v else None

    @type_face.setter
    def type_face(self, value: None | str):
        v = self._value.value.value.compute_if_absent(
            datastore.keys.FONT_PREFS_TYPEFACE
        )
        v.value = value

    @property
    def line_spacing(self) -> int:
        v = self._value.value.value.get(datastore.keys.FONT_PREFS_LINE_SP)
        return v.value if v else -1

    @line_spacing.setter
    def line_spacing(self, value: int):
        v = self._value.value.value.compute_if_absent(
            datastore.keys.FONT_PREFS_LINE_SP
        )
        v.value = value

    @property
    def size(self) -> int:
        v = self._value.value.value.get(datastore.keys.FONT_PREFS_SIZE)
        return v.value if v else -1

    @size.setter
    def size(self, value: int):
        v = self._value.value.value.compute_if_absent(
            datastore.keys.FONT_PREFS_SIZE
        )
        v.value = value

    @property
    def align(self) -> int:
        v = self._value.value.value.get(datastore.keys.FONT_PREFS_ALIGN)
        return v.value if v else -1

    @align.setter
    def align(self, value: int):
        v = self._value.value.value.compute_if_absent(
            datastore.keys.FONT_PREFS_ALIGN
        )
        v.value = value

    @property
    def inset_top(self) -> int:
        v = self._value.value.value.get(datastore.keys.FONT_PREFS_INSET_TOP)
        return v.value if v else -1

    @inset_top.setter
    def inset_top(self, value: int):
        v = self._value.value.value.compute_if_absent(
            datastore.keys.FONT_PREFS_INSET_TOP
        )
        v.value = value

    @property
    def inset_left(self) -> int:
        v = self._value.value.value.get(datastore.keys.FONT_PREFS_INSET_LEFT)
        return v.value if v else -1

    @inset_left.setter
    def inset_left(self, value: int):
        v = self._value.value.value.compute_if_absent(
            datastore.keys.FONT_PREFS_INSET_LEFT
        )
        v.value = value

    @property
    def inset_bottom(self) -> int:
        v = self._value.value.value.get(datastore.keys.FONT_PREFS_INSET_BOTTOM)
        return v.value if v else -1

    @inset_bottom.setter
    def inset_bottom(self, value: int):
        v = self._value.value.value.compute_if_absent(
            datastore.keys.FONT_PREFS_INSET_BOTTOM
        )
        v.value = value

    @property
    def inset_right(self) -> int:
        v = self._value.value.value.get(datastore.keys.FONT_PREFS_INSET_RIGHT)
        return v.value if v else -1

    @inset_right.setter
    def inset_right(self, value: int):
        v = self._value.value.value.compute_if_absent(
            datastore.keys.FONT_PREFS_INSET_RIGHT
        )
        v.value = value

    @property
    def unknown1(self) -> int:
        v = self._value.value.value.get(datastore.keys.FONT_PREFS_UNKNOWN_1)
        return v.value if v else -1

    @unknown1.setter
    def unknown1(self, value: int):
        v = self._value.value.value.compute_if_absent(
            datastore.keys.FONT_PREFS_UNKNOWN_1
        )
        v.value = value

    @property
    def bold(self) -> int:
        v = self._value.value.value.get(datastore.keys.FONT_PREFS_BOLD)
        return v.value if v else -1

    @bold.setter
    def bold(self, value: int):
        v = self._value.value.value.compute_if_absent(
            datastore.keys.FONT_PREFS_BOLD
        )
        v.value = value

    @property
    def user_sideloadable_font(self) -> None | str:
        v = self._value.value.value.get(
            datastore.keys.FONT_PREFS_USER_SIDELOADABLE_FONT
        )
        return v.value if v else None

    @user_sideloadable_font.setter
    def user_sideloadable_font(self, value: None | str):
        v = self._value.value.value.compute_if_absent(
            datastore.keys.FONT_PREFS_USER_SIDELOADABLE_FONT
        )
        v.value = value

    @property
    def custom_font_index(self) -> int:
        v = self._value.value.value.get(
            datastore.keys.FONT_PREFS_CUSTOM_FONT_INDEX
        )
        return v.value if v else -1

    @custom_font_index.setter
    def custom_font_index(self, value: int):
        v = self._value.value.value.compute_if_absent(
            datastore.keys.FONT_PREFS_CUSTOM_FONT_INDEX
        )
        v.value = value

    @property
    def mobi7_system_font(self) -> None | str:
        v = self._value.value.value.get(
            datastore.keys.FONT_PREFS_MOBI_7_SYSTEM_FONT
        )
        return v.value if v else None

    @mobi7_system_font.setter
    def mobi7_system_font(self, value: None | str):
        v = self._value.value.value.compute_if_absent(
            datastore.keys.FONT_PREFS_MOBI_7_SYSTEM_FONT
        )
        v.value = value

    @property
    def mobi7_restore_font(self) -> None | bool:
        v = self._value.value.value.get(
            datastore.keys.FONT_PREFS_MOBI_7_RESTORE_FONT
        )
        return v.value if v else None

    @custom_font_index.setter
    def custom_font_index(self, value: None | bool):
        v = self._value.value.value.compute_if_absent(
            datastore.keys.FONT_PREFS_MOBI_7_RESTORE_FONT
        )
        v.value = value
