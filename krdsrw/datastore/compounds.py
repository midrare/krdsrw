from __future__ import annotations
import base64
import json
import sys
import typing

from . import auto
from . import keys
from . import names
from .constants import UTF8STR_TYPE_INDICATOR
from .constants import BYTE_TYPE_INDICATOR
from .cursor import Cursor
from .error import *
from .basics import Bool
from .basics import Byte
from .basics import Char
from .basics import Short
from .basics import Int
from .basics import Long
from .basics import Float
from .basics import Double
from .basics import Utf8Str
from .template import Template
from .templatized import CheckedDict
from .templatized import TemplatizedDict
from .templatized import TemplatizedList
from .value import Value

MIN_PYTHON_VERSION: typing.Final[typing.Tuple[int, int]] = (3, 7)
if sys.version_info < MIN_PYTHON_VERSION:
    print(
        "Requires Python >= %s. (Ordered dicts is required.)" %
        ".".join([str(i) for i in MIN_PYTHON_VERSION]),
        file=sys.stderr,
    )
    sys.exit(1)

T = typing.TypeVar("T", bound=Value)


class Array(Value, typing.Generic[T]):
    def __init__(self, template: Template[T]):
        self._template: Template[T] = template
        self._value: TemplatizedList[T] = TemplatizedList(template)

    @property
    def value(self) -> TemplatizedList[T]:
        return self._value

    @property
    def template(self) -> Template[T]:
        return self._template

    def read(self, cursor: Cursor):
        self._value.clear()
        size = cursor.read_int()
        for _ in range(size):
            e = self._template.instantiate()
            e.read(cursor)
            self._value.append(e)

    def write(self, cursor: Cursor):
        cursor.write_int(len(self._value))
        for e in self._value:
            e.write(cursor)

    def __eq__(self, other: Array) -> bool:
        if isinstance(other, self.__class__):
            return (
                self._value == other._value
                and self._template == other._template
            )
        return False


class DateTime(Value):
    def __init__(self):
        self._value: None | int = -1  # -1 is null

    @property
    def value(self) -> None | int:
        return self._value

    @value.setter
    def value(self, value: None | int):
        if value is not None and not isinstance(value, int):
            raise TypeError(f"Value is not of class {int.__name__}")
        self._value = value

    def read(self, cursor: Cursor):
        self._value = cursor.read_long()

    def write(self, cursor: Cursor):
        cursor.write_long(
            self._value if self._value is not None and self._value >= 0 else -1
        )

    def __eq__(self, other: Value) -> bool:
        if isinstance(other, self.__class__):
            v1 = (
                self._value
                if self._value is not None and self._value >= 0 else -1
            )
            v2 = (
                other._value
                if other._value is not None and other._value >= 0 else -1
            )
            return v1 == v2
        return super().__eq__(other)


class DynamicMap(Value):
    def __init__(self):
        self._value: typing.Dict[str, Value] = CheckedDict(str, Value)

    @property
    def value(self) -> typing.Dict[str, Value]:
        return self._value

    def read(self, cursor: Cursor):
        self._value.clear()
        size = cursor.read_int()
        for i in range(size):
            field_name = cursor.read_utf8str()
            field_value = auto.read_auto(cursor)
            self._value[field_name] = field_value

    def write(self, cursor: Cursor):
        cursor.write_int(len(self._value))
        for key, value in self._value.items():
            cursor.write_utf8str(key)
            auto.write_auto(cursor, value)

    def __eq__(self, other: Value) -> bool:
        if isinstance(other, self.__class__):
            return self._value == other.value
        return super().__eq__(other)


class FixedMap(Value):
    def __init__(
        self,
        required: typing.Dict[str,
                              Template],
        optional: None | typing.Dict[str,
                                     Template] = None,
    ):
        self._required_templates: typing.Dict[str, Template] = dict(required)
        self._optional_templates: typing.Dict[
            str,
            Template] = (dict(optional) if optional else {})

        templates = (required or {}) | (optional or {})
        self._value: TemplatizedDict[str, Value] = TemplatizedDict(templates)
        for k in required.keys():
            self._value.instantiate_and_put(k)

    @property
    def value(self) -> TemplatizedDict[str, Value]:
        return self._value

    @property
    def required(self) -> typing.List[str]:
        return list((self._required_templates or {}).keys())

    @property
    def optional(self) -> typing.List[str]:
        return list((self._optional_templates or {}).keys())

    def read(self, cursor: Cursor):
        self._value.clear()

        for field_name, field_template in self._required_templates.items():
            if not self._read_next_field(cursor, field_name, field_template):
                raise FieldNotFoundError(
                    'Expected field with name "%s" but was not found' %
                    field_name
                )

        for field_name, field_template in self._optional_templates.items():
            if not self._read_next_field(cursor, field_name, field_template):
                break

    def _read_next_field(
        self,
        cursor: Cursor,
        field_name: str,
        field_template: Template
    ) -> bool:
        cursor.save()
        try:
            o = field_template.instantiate()
            o.read(cursor)
            self._value[field_name] = o
            cursor.unsave()
            return True
        except UnexpectedDataTypeError:
            cursor.restore()

        return False

    def write(self, cursor: Cursor):
        for field_name, field_template in self._required_templates.items():
            value = self._value.get(field_name)
            value.write(cursor)

        for field_name, field_template in self._optional_templates.items():
            value = self._value.get(field_name)
            if value is None:
                break
            value.write(cursor)

    def __eq__(self, other: Value) -> bool:
        if isinstance(other, self.__class__):
            return (
                self._required_templates == other._required_templates
                and self._optional_templates == other._optional_templates
                and self._value == other._value
            )
        return super().__eq__(other)

    def __str__(self) -> str:
        d = { k: v for k, v in self._value.items() if v is not None }
        return f"{self.__class__.__name__}{str(d)}"


class Json(Value):
    def __init__(self):
        self._value: None | bool | int | float | str | list | dict = None

    @property
    def value(self) -> None | bool | int | float | str | list | dict:
        return self._value

    @value.setter
    def value(self, value: None | bool | int | float | str | list | dict):
        if value is not None and not isinstance(
            value,
            (bool | int | float | str | list | dict)
        ):
            class_names = [
                c.__name__ for c in [bool | int | float | str | list | dict]
            ]
            raise TypeError(
                f"value is not any of types {', '.join(class_names)}"
            )
        self._value = value

    def read(self, cursor: Cursor):
        s = cursor.read_utf8str()
        self._value = json.loads(s) if s is not None and s else None

    def write(self, cursor: Cursor):
        s = json.dumps(self._value) if self._value is not None else ""
        cursor.write_utf8str(s)

    def __eq__(self, other: Value) -> bool:
        if isinstance(other, self.__class__):
            return self._value == other._value
        return super().__eq__(other)


class LastPageRead(Value):  # also known as LPR. LPR is kindle position info
    EXTENDED_LPR_VERSION: int = 2

    def __init__(self):
        super().__init__()
        self._pos: Position = Position()
        self._timestamp: int = -1
        self._lpr_version: int = -1

    @property
    def pos(self) -> Position:
        return self._pos

    @property
    def lpr_version(self) -> None | int:
        return self._lpr_version

    @lpr_version.setter
    def lpr_version(self, value: None | int):
        if value is not None and not isinstance(value, int):
            raise TypeError(f"value is not of type {int.__name__}")
        self._lpr_version = value

    @property
    def timestamp(self) -> int:
        return self._timestamp

    @timestamp.setter
    def timestamp(self, value: int):
        if value is not None and not isinstance(value, int):
            raise TypeError(f"value is not of type {int.__name__}")
        self._timestamp = value

    def read(self, cursor: Cursor):
        self._pos.value = None
        self._pos.prefix = None
        self._timestamp = -1
        self._lpr_version = -1

        type_byte = cursor.peek()
        if type_byte == UTF8STR_TYPE_INDICATOR:
            # old LPR version'
            self._pos.read(cursor)
        elif type_byte == BYTE_TYPE_INDICATOR:
            # new LPR version
            self._lpr_version = cursor.read_byte()
            self._pos.read(cursor)
            self._timestamp = int(cursor.read_long())
        else:
            raise UnexpectedFieldError(
                "Expected Utf8Str or byte but got %d" % type_byte
            )

    def write(self, cursor: Cursor):
        # XXX may cause problems if kindle expects the original LPR format version when datastore file is re-written
        if self._timestamp is None or self._timestamp < 0:
            # old LPR version
            self._pos.write(cursor)
        else:
            # new LPR version
            lpr_version = max(self.EXTENDED_LPR_VERSION, self._lpr_version)
            cursor.write_byte(lpr_version)
            self._pos.write(cursor)
            cursor.write_long(self._timestamp)

    def __eq__(self, other: Value) -> bool:
        if isinstance(other, self.__class__):
            return (
                self._pos == other._pos and self._timestamp == other.timestamp
                and self._lpr_version == other._lpr_version
            )
        return super().__eq__(other)

    def __str__(self) -> str:
        return (
            self.__class__.__name__ + ":" + str({
                "lpr_version": self._lpr_version,
                "timestamp": self._timestamp,
                "pos": self._pos,
            })
        )


class Position(Value):
    PREFIX_VERSION1: int = 0x01

    def __init__(self):
        self._chunk_eid: None | int = -1
        self._chunk_pos: None | int = -1
        self._value: None | int = -1

    @property
    def chunk_eid(self) -> None | int:
        return self._chunk_eid

    @chunk_eid.setter
    def chunk_eid(self, value: None | int):
        if value is not None and not isinstance(value, int):
            raise TypeError(f"value is not of type {int.__name__}")
        self._chunk_eid = value

    @property
    def chunk_pos(self) -> None | int:
        return self._chunk_pos

    @chunk_pos.setter
    def chunk_pos(self, value: None | int):
        if value is not None and not isinstance(value, int):
            raise TypeError(f"value is not of type {int.__name__}")
        self._chunk_pos = value

    @property
    def value(self) -> None | int:
        return self._value

    @value.setter
    def value(self, value: None | int):
        if value is not None and not isinstance(value, int):
            raise TypeError(f"value is not of type {int.__name__}")
        self._value = value

    def read(self, cursor: Cursor):
        s = cursor.read_utf8str()
        split = s.split(":", 2)
        if len(split) > 1:
            b = base64.b64decode(split[0])
            version = b[0]
            if version == self.PREFIX_VERSION1:
                self._chunk_eid = int.from_bytes(b[1:5], "little")
                self._chunk_pos = int.from_bytes(b[5:9], "little")
            else:
                # TODO throw a proper exception
                raise Exception(
                    "Unrecognized position version 0x%02x" % version
                )
            self._value = int(split[1])
        else:
            self._value = int(s)

    def write(self, cursor: Cursor):
        s = ""
        if (
            self._chunk_eid is not None and self._chunk_eid >= 0
            and self._chunk_pos is not None and self._chunk_pos >= 0
        ):
            b_version = self.PREFIX_VERSION1.to_bytes(1, "little", signed=False)
            b_eid = self._chunk_eid.to_bytes(4, "little", signed=False)
            b_pos = self._chunk_pos.to_bytes(4, "little", signed=False)
            s += base64.b64encode(b_version + b_eid + b_pos).decode("ascii")
            s += ":"
        s += str(
            self._value if self._value is not None and self._value >= 0 else -1
        )
        cursor.write_utf8str(s)

    def __eq__(self, other: Value) -> bool:
        if isinstance(other, self.__class__):
            val1 = (
                self._value
                if self._value is not None and self._value >= 0 else -1
            )
            val2 = (
                other._value
                if other._value is not None and other._value >= 0 else -1
            )
            eid1 = (
                self._chunk_eid if self._chunk_eid is not None
                and self._chunk_eid >= 0 else None
            )
            eid2 = (
                other._chunk_eid if other._chunk_eid is not None
                and other._chunk_eid >= 0 else None
            )
            pos1 = (
                self._chunk_pos if self._chunk_pos is not None
                and self._chunk_pos >= 0 else None
            )
            pos2 = (
                other._chunk_pos if other._chunk_pos is not None
                and other._chunk_pos >= 0 else None
            )
            return val1 == val2 and eid1 == eid2 and pos1 == pos2
        return super().__eq__(other)

    def __str__(self) -> str:
        d = {
            "chunk_eid": self._chunk_eid,
            "chunk_pos": self._chunk_pos,
            "char_pos": self._value,
        }
        d = {
            k: v
            for k,
            v in d.items()
            if v is not None and not (isinstance(v,
                                                 int) or v >= 0)
        }
        return f"{self.__class__.__name__}{str(d)}"


class SwitchMap(Value):
    def __init__(
        self,
        id_to_name: typing.Dict[int,
                                str],
        id_to_template: typing.Dict[int,
                                    Template],
    ):
        self._id_to_name: typing.Dict[int, str] = dict(id_to_name)
        self._id_to_template: typing.Dict[int, Template] = dict(id_to_template)
        self._name_to_id: typing.Dict[str,
                                      int] = {
                                          v: k
                                          for k,
                                          v in id_to_name.items()
                                      }

        ids = set(id_to_name.keys()) | set(id_to_template.keys())
        templates = {
            k: Template(NamedValue,
                        id_to_name[k],
                        id_to_template[k])
            for k in ids
        }
        self._value: TemplatizedDict[int,
                                     NamedValue] = TemplatizedDict(templates)

    @property
    def value(self) -> TemplatizedDict[int, NamedValue]:
        return self._value

    def _make_value(self, key: int) -> NamedValue:
        name = self._id_to_name.get(key)
        template = self._id_to_template.get(key)
        return NamedValue(name, template)

    def read(self, cursor: Cursor):
        self._value.clear()
        size = cursor.read_int()
        for i in range(size):
            field_id = cursor.read_int()
            if field_id not in self._id_to_name:
                raise UnexpectedFieldError(
                    'Unrecognized field ID "%d"' % field_id
                )
            name = NamedValue.peek_name(cursor)
            if self._id_to_name[field_id] != name:
                raise UnexpectedFieldError(
                    'Expected name "%s" but got "%s"' %
                    (name,
                     self._id_to_name[field_id])
                )
            template = self._id_to_template.get(field_id)
            value = NamedValue(name, template)
            value.read(cursor)
            self._value[field_id] = value

    def write(self, cursor: Cursor):
        id_to_non_null_value = {
            k: v
            for k,
            v in self._value.items()
            if v is not None
        }
        cursor.write_int(len(id_to_non_null_value))
        for field_id, field_value in id_to_non_null_value.items():
            cursor.write_int(field_id)
            field_value.write(cursor)

    def __eq__(self, other: Value) -> bool:
        if isinstance(other, self.__class__):
            id_to_non_null_value1 = {
                k: v
                for k,
                v in self._value.items()
                if v is not None
            }
            id_to_non_null_value2 = {
                k: v
                for k,
                v in other._value.items()
                if v is not None
            }
            return (
                self._id_to_name == other._id_to_name
                and id_to_non_null_value1 == id_to_non_null_value2
                and self._id_to_template == other._id_to_template
            )

    def names(self) -> typing.List[str]:
        return list(self._name_to_id.keys())

    def ids(self) -> typing.List[int]:
        return list(self._id_to_name.keys())

    def name_to_id(self, name: str) -> None | int:
        return self._name_to_id.get(name)

    def id_to_name(self, id: int) -> None | str:
        return self._id_to_name.get(id)


class TimeZoneOffset(Value):
    def __init__(self):
        self._value: None | int = None  # -1 is null

    @property
    def value(self) -> None | int:
        return self._value

    @value.setter
    def value(self, value: None | int):
        if value is not None and not isinstance(value, int):
            raise TypeError(f"value is not of type {int.__name__}")
        self._value = value

    def read(self, cursor: Cursor):
        self._value = cursor.read_long()

    def write(self, cursor: Cursor):
        cursor.write_long(
            self._value if self._value is not None and self._value >= 0 else -1
        )

    def __eq__(self, other: Value) -> bool:
        if isinstance(other, self.__class__):
            v1 = (
                self._value
                if self._value is not None and self._value >= 0 else -1
            )
            v2 = (
                other._value
                if other._value is not None and other._value >= 0 else -1
            )
            return v1 == v2

        return super().__eq__(other)


class NamedValue(Value, typing.Generic[T]):
    DEMARCATION_BEGIN: int = 254
    DEMARCATION_END: int = 255

    def __init__(self, name: str, template: None | Template[T] = None):
        self._name: str = name
        self._template: Template[T] = template or NAME_TO_TEMPLATE.get(name)
        self._value: T = self._template.instantiate()

    @property
    def name(self) -> str:
        return self._name

    @property
    def template(self) -> Template[T]:
        return self._template

    @property
    def value(self) -> T:
        return self._value

    @value.setter
    def value(self, o: T):
        if not isinstance(o, self._template.cls):
            raise TypeError(
                f"Value is not of class {self._template.cls.__name__}"
            )
        self._value = o

    @staticmethod
    def peek_name(cursor: Cursor) -> None | str:
        name = None
        cursor.save()
        ch = cursor.read()
        if ch == NamedValue.DEMARCATION_BEGIN:
            name = cursor.read_utf8str(False)
        cursor.restore()
        return name

    @staticmethod
    def peek_value_cls(cursor: Cursor) -> None | type:
        cls = None
        cursor.save()
        ch = cursor.read()
        if ch == NamedValue.DEMARCATION_BEGIN:
            name = cursor.read_utf8str(False)
            template = NAME_TO_TEMPLATE.get(name)
            cls = template.cls
        cursor.restore()
        return cls

    def read(self, cursor: Cursor):
        if not cursor.eat(NamedValue.DEMARCATION_BEGIN):
            raise DemarcationError(
                "Starting demarcation not found @%d" % cursor.tell()
            )

        name = cursor.read_utf8str(False)
        if name != self._name:
            raise UnexpectedNameError(
                'Expected named value "%s" but got "%s"' % (self._name,
                                                            name)
            )

        value = self._template.instantiate()
        value.read(cursor)

        if not cursor.eat(NamedValue.DEMARCATION_END):
            raise DemarcationError(
                "Ending demarcation not found @%d" % cursor.tell()
            )

        self._value = value

    def write(self, cursor: Cursor):
        cursor.write(NamedValue.DEMARCATION_BEGIN)
        cursor.write_utf8str(self._name, False)
        self._value.write(cursor)
        cursor.write(NamedValue.DEMARCATION_END)

    def __eq__(self, other: Value) -> bool:
        if isinstance(other, self.__class__):
            return (
                self._name == other._name and self._template == other._template
                and self._value == other._value
            )
        return super().__eq__(other)

    def __str__(self) -> str:
        return "%s{%s: %s}" % (
            self.__class__.__name__,
            self._name,
            self._template.cls.__name__,
        )


class NameMap(Value):
    def __init__(self):
        self._value: TemplatizedDict[str,
                                     NamedValue] = TemplatizedDict(
                                         self._make_value
                                     )

    @property
    def value(self) -> TemplatizedDict[str, NamedValue]:
        return self._value

    def read(self, cursor: Cursor):
        self._value.clear()
        size = cursor.read_int()
        for i in range(size):
            name = NamedValue.peek_name(cursor)
            value = NamedValue(name)
            value.read(cursor)
            self._value[name] = value

    def write(self, cursor: Cursor):
        cursor.write_int(len(self._value))
        for name, value in self._value.items():
            assert name == value.name, "name mismatch"
            value.write(cursor)

    def __eq__(self, other: Value) -> bool:
        if isinstance(other, self.__class__):
            return self._value == other.value
        return super().__eq__(other)

    @staticmethod
    def _make_value(name: str) -> NamedValue:
        return NamedValue(name)


# basics
BYTE_TEMPLATE: Template[Byte] = Template(Byte)
CHAR_TEMPLATE: Template[Char] = Template(Char)
BOOL_TEMPLATE: Template[Bool] = Template(Bool)
SHORT_TEMPLATE: Template[Short] = Template(Short)
INT_TEMPLATE: Template[Int] = Template(Int)
LONG_TEMPLATE: Template[Long] = Template(Long)
FLOAT_TEMPLATE: Template[Float] = Template(Float)
DOUBLE_TEMPLATE: Template[Double] = Template(Double)
UTF8STR_TEMPLATE: Template[Utf8Str] = Template(Utf8Str)

# composites
JSON_TEMPLATE: Template[Json] = Template(Json)
POSITION_TEMPLATE: Template[Position] = Template(Position)
DATETIME_TEMPLATE: Template[DateTime] = Template(DateTime)
LAST_PAGE_READ_TEMPLATE: Template[LastPageRead] = Template(LastPageRead)
DYNAMIC_MAP_TEMPLATE: Template[DynamicMap] = Template(DynamicMap)
TIMEZONE_OFFSET_TEMPLATE: Template[TimeZoneOffset] = Template(TimeZoneOffset)

ARRAY_BYTE_TEMPLATE: Template[Array[Byte]] = Template(Array, BYTE_TEMPLATE)
ARRAY_CHAR_TEMPLATE: Template[Array[Char]] = Template(Array, CHAR_TEMPLATE)
ARRAY_BOOL_TEMPLATE: Template[Array[Bool]] = Template(Array, BOOL_TEMPLATE)
ARRAY_SHORT_TEMPLATE: Template[Array[Short]] = Template(Array, SHORT_TEMPLATE)
ARRAY_INT_TEMPLATE: Template[Array[Int]] = Template(Array, INT_TEMPLATE)
ARRAY_LONG_TEMPLATE: Template[Array[Long]] = Template(Array, LONG_TEMPLATE)
ARRAY_FLOAT_TEMPLATE: Template[Array[Float]] = Template(Array, FLOAT_TEMPLATE)
ARRAY_DOUBLE_TEMPLATE: Template[Array[Double]
                                ] = Template(Array,
                                             DOUBLE_TEMPLATE)
ARRAY_UTF8STR_TEMPLATE: Template[Array[UTF8STR_TEMPLATE]
                                 ] = Template(Array,
                                              UTF8STR_TEMPLATE)

# timer.average.calculator.distribution.normal
TIMER_AVERAGE_CALCULATOR_DISTRIBUTION_NORMAL_TEMPLATE = Template(
    FixedMap,
    {
        keys.TIMER_AVG_DISTRIBUTION_COUNT: LONG_TEMPLATE,
        keys.TIMER_AVG_DISTRIBUTION_SUM: DOUBLE_TEMPLATE,
        keys.TIMER_AVG_DISTRIBUTION_SUM_OF_SQUARES: DOUBLE_TEMPLATE,
    },
)

# timer.average.calculator.outliers
TIMER_AVERAGE_CALCULATOR_OUTLIERS_TEMPLATE = Template(Array, DOUBLE_TEMPLATE)

# timer.average.calculator
TIMER_AVERAGE_CALCULATOR_TEMPLATE = Template(
    FixedMap,
    {
        keys.TIMER_AVG_SAMPLES_1:
            ARRAY_DOUBLE_TEMPLATE,
        keys.TIMER_AVG_SAMPLES_2:
            ARRAY_DOUBLE_TEMPLATE,
        keys.TIMER_AVG_NORMAL_DISTRIBUTIONS:
            Template(
                Array,
                TIMER_AVERAGE_CALCULATOR_DISTRIBUTION_NORMAL_TEMPLATE
            ),
        keys.TIMER_AVG_OUTLIERS:
            Template(Array,
                     TIMER_AVERAGE_CALCULATOR_OUTLIERS_TEMPLATE),
    },
)

# timer.model
TIMER_MODEL_TEMPLATE = Template(
    FixedMap,
    {
        keys.TIMER_VERSION: LONG_TEMPLATE,
        keys.TIMER_TOTAL_TIME: LONG_TEMPLATE,
        keys.TIMER_TOTAL_WORDS: LONG_TEMPLATE,
        keys.TIMER_TOTAL_PERCENT: DOUBLE_TEMPLATE,
        keys.TIMER_AVERAGE_CALCULATOR: TIMER_AVERAGE_CALCULATOR_TEMPLATE,
    },
)

# timer.data.store
TIMER_DATA_STORE_TEMPLATE = Template(
    FixedMap,
    {
        keys.TIMERV1_STORE_ON: BOOL_TEMPLATE,
        keys.TIMERV1_STORE_READING_TIMER_MODEL: TIMER_MODEL_TEMPLATE,
        keys.TIMERV1_STORE_VERSION: INT_TEMPLATE,
    },
)

# page.history.record
PAGE_HISTORY_RECORD_TEMPLATE = Template(
    FixedMap,
    {
        keys.PAGE_HISTORY_POS: POSITION_TEMPLATE,
        keys.PAGE_HISTORY_TIME: DATETIME_TEMPLATE,
    },
)

# font.prefs
FONT_PREFS_TEMPLATE = Template(
    FixedMap,
    {
        keys.FONT_PREFS_TYPEFACE: UTF8STR_TEMPLATE,
        keys.FONT_PREFS_LINE_SP: INT_TEMPLATE,
        keys.FONT_PREFS_SIZE: INT_TEMPLATE,
        keys.FONT_PREFS_ALIGN: INT_TEMPLATE,
        keys.FONT_PREFS_INSET_TOP: INT_TEMPLATE,
        keys.FONT_PREFS_INSET_LEFT: INT_TEMPLATE,
        keys.FONT_PREFS_INSET_BOTTOM: INT_TEMPLATE,
        keys.FONT_PREFS_INSET_RIGHT: INT_TEMPLATE,
        keys.FONT_PREFS_UNKNOWN_1: INT_TEMPLATE,
    },
    {
        keys.FONT_PREFS_BOLD: INT_TEMPLATE,
        keys.FONT_PREFS_USER_SIDELOADABLE_FONT: UTF8STR_TEMPLATE,
        keys.FONT_PREFS_CUSTOM_FONT_INDEX: INT_TEMPLATE,
        keys.FONT_PREFS_MOBI_7_SYSTEM_FONT: UTF8STR_TEMPLATE,
        keys.FONT_PREFS_MOBI_7_RESTORE_FONT: BOOL_TEMPLATE,
        keys.FONT_PREFS_READING_PRESET_SELECTED: UTF8STR_TEMPLATE,
    },
)

# fpr
FPR_TEMPLATE = Template(
    FixedMap,
    {
        keys.FPR_POS: POSITION_TEMPLATE,
    },
    {
        keys.FPR_TIMESTAMP: DATETIME_TEMPLATE,
        keys.FPR_TIMEZONE_OFFSET: TIMEZONE_OFFSET_TEMPLATE,
        keys.FPR_COUNTRY: UTF8STR_TEMPLATE,
        keys.FPR_DEVICE: UTF8STR_TEMPLATE,
    },
)

# updated_lpr
UPDATED_LPR_TEMPLATE = Template(
    FixedMap,
    {
        keys.UPDATED_LPR_POS: POSITION_TEMPLATE,
    },
    {
        keys.UPDATED_LPR_TIMESTAMP: DATETIME_TEMPLATE,
        keys.UPDATED_LPR_TIMEZONE_OFFSET: TIMEZONE_OFFSET_TEMPLATE,
        keys.UPDATED_LPR_COUNTRY: UTF8STR_TEMPLATE,
        keys.UPDATED_LPR_DEVICE: UTF8STR_TEMPLATE,
    },
)

# apnx.key
APNX_KEY_TEMPLATE = Template(
    FixedMap,
    {
        keys.APNX_ASIN: UTF8STR_TEMPLATE,
        keys.APNX_CDE_TYPE: UTF8STR_TEMPLATE,
        keys.APNX_SIDECAR_AVAILABLE: BOOL_TEMPLATE,
        keys.APNX_OPN_TO_POS: ARRAY_INT_TEMPLATE,
        keys.APNX_FIRST: INT_TEMPLATE,
        keys.APNX_UNKNOWN_1: INT_TEMPLATE,
        keys.APNX_UNKNOWN_2: INT_TEMPLATE,
        keys.APNX_PAGE_MAP: UTF8STR_TEMPLATE,
    },
)

# fixed.layout.data
FIXED_LAYOUT_DATA_TEMPLATE = Template(
    FixedMap,
    {
        keys.FIXED_LAYOUT_DATA_UNKNOWN_1: BOOL_TEMPLATE,
        keys.FIXED_LAYOUT_DATA_UNKNOWN_2: BOOL_TEMPLATE,
        keys.FIXED_LAYOUT_DATA_UNKNOWN_3: BOOL_TEMPLATE,
    },
)

# sharing.limits
SHARING_LIMITS_TEMPLATE = Template(
    FixedMap,
    {
        # TODO discover structure for sharing.limits
        keys.SHARING_LIMITS_ACCUMULATED:
            None
    },
)

# language.store
LANGUAGE_STORE_TEMPLATE = Template(
    FixedMap,
    {
        keys.LANGUAGE_STORE_LANGUAGE: UTF8STR_TEMPLATE,
        keys.LANGUAGE_STORE_UNKNOWN_1: INT_TEMPLATE,
    },
)

# periodicals.view.state
PERIODICALS_VIEW_STATE_TEMPLATE = Template(
    FixedMap,
    {
        keys.PERIODICALS_UNKNOWN_1: UTF8STR_TEMPLATE,
        keys.PERIODICALS_UNKNOWN_2: INT_TEMPLATE,
    },
)

# purchase.state.data
PURCHASE_STATE_DATA_TEMPLATE = Template(
    FixedMap,
    {
        keys.PURCHASE_STATE: INT_TEMPLATE,
        keys.PURCHASE_TIME: DATETIME_TEMPLATE,
    },
)

# timer.data.store.v2
TIMER_DATA_STOREV2_TEMPLATE = Template(
    FixedMap,
    {
        keys.TIMERV2_ON: BOOL_TEMPLATE,
        keys.TIMERV2_READING_TIMER_MODEL: TIMER_MODEL_TEMPLATE,
        keys.TIMERV2_VERSION: INT_TEMPLATE,
        keys.TIMERV2_LAST_OPTION: INT_TEMPLATE,
    },
)

# book.info.store
BOOK_INFO_STORE_TEMPLATE = Template(
    FixedMap,
    {
        keys.BOOK_INFO_NUM_WORDS: LONG_TEMPLATE,
        keys.BOOK_INFO_PERCENT_OF_BOOK: DOUBLE_TEMPLATE,
    },
)

# page.history.store
PAGE_HISTORY_STORE_TEMPLATE = Template(Array, PAGE_HISTORY_RECORD_TEMPLATE)

# reader.state.preferences
READER_STATE_PREFERENCES_TEMPLATE = Template(
    FixedMap,
    {
        keys.READER_PREFS_FONT_PREFERENCES: FONT_PREFS_TEMPLATE,
        keys.READER_PREFS_LEFT_MARGIN: INT_TEMPLATE,
        keys.READER_PREFS_RIGHT_MARGIN: INT_TEMPLATE,
        keys.READER_PREFS_TOP_MARGIN: INT_TEMPLATE,
        keys.READER_PREFS_BOTTOM_MARGIN: INT_TEMPLATE,
        keys.READER_PREFS_UNKNOWN_1: BOOL_TEMPLATE,
    },
)

# annotation.personal.bookmark
# annotation.personal.clip_article
# annotation.personal.highlight
# annotation.personal.note
ANNOTATION_PERSONAL_ELEMENT_TEMPLATE = Template(
    FixedMap,
    {
        keys.ANNOTATION_START_POS: POSITION_TEMPLATE,
        keys.ANNOTATION_END_POS: POSITION_TEMPLATE,
        keys.ANNOTATION_CREATION_TIME: DATETIME_TEMPLATE,
        keys.ANNOTATION_LAST_MODIFICATION_TIME: DATETIME_TEMPLATE,
        keys.ANNOTATION_TEMPLATE: UTF8STR_TEMPLATE,
    },
    {
        keys.ANNOTATION_NOTE: UTF8STR_TEMPLATE,
    },
)

# saved.avl.interval.tree (child)
SAVED_AVL_INTERVAL_TREE_BOOKMARK_TEMPLATE = Template(
    NamedValue,
    names.ANNOTATION_PERSONAL_BOOKMARK
)
SAVED_AVL_INTERVAL_TREE_HIGHLIGHT_TEMPLATE = Template(
    NamedValue,
    names.ANNOTATION_PERSONAL_HIGHLIGHT
)
SAVED_AVL_INTERVAL_TREE_NOTE_TEMPLATE = Template(
    NamedValue,
    names.ANNOTATION_PERSONAL_NOTE
)
SAVED_AVL_INTERVAL_TREE_CLIP_ARTICLE_TEMPLATE = Template(
    NamedValue,
    names.ANNOTATION_PERSONAL_CLIP_ARTICLE
)

# saved.avl.interval.tree
SAVED_AVL_INTERVAL_TREE_BOOKMARKS_TEMPLATE = Template(
    Array,
    SAVED_AVL_INTERVAL_TREE_BOOKMARK_TEMPLATE
)
SAVED_AVL_INTERVAL_TREE_HIGHLIGHTS_TEMPLATE = Template(
    Array,
    SAVED_AVL_INTERVAL_TREE_HIGHLIGHT_TEMPLATE
)
SAVED_AVL_INTERVAL_TREE_NOTES_TEMPLATE = Template(
    Array,
    SAVED_AVL_INTERVAL_TREE_NOTE_TEMPLATE
)
SAVED_AVL_INTERVAL_TREE_CLIP_ARTICLES_TEMPLATE = Template(
    Array,
    SAVED_AVL_INTERVAL_TREE_CLIP_ARTICLE_TEMPLATE
)

# annotation.cache.object
ANNOTATION_CACHE_OBJECT_TEMPLATE = Template(
    SwitchMap,
    {
        keys.ANNOTATION_BOOKMARKS: names.SAVED_AVL_INTERVAL_TREE,
        keys.ANNOTATION_HIGHLIGHTS: names.SAVED_AVL_INTERVAL_TREE,
        keys.ANNOTATION_NOTES: names.SAVED_AVL_INTERVAL_TREE,
        keys.ANNOTATION_CLIP_ARTICLES: names.SAVED_AVL_INTERVAL_TREE,
    },
    {
        keys.ANNOTATION_BOOKMARKS:
            SAVED_AVL_INTERVAL_TREE_BOOKMARKS_TEMPLATE,
        keys.ANNOTATION_HIGHLIGHTS:
            SAVED_AVL_INTERVAL_TREE_HIGHLIGHTS_TEMPLATE,
        keys.ANNOTATION_NOTES:
            SAVED_AVL_INTERVAL_TREE_NOTES_TEMPLATE,
        keys.ANNOTATION_CLIP_ARTICLES:
            SAVED_AVL_INTERVAL_TREE_CLIP_ARTICLES_TEMPLATE,
        # keys.ANNOTATION_BOOKMARKS: Template(
        #     NamedValue, names.SAVED_AVL_INTERVAL_TREE, SAVED_AVL_INTERVAL_TREE_BOOKMARKS_TEMPLATE),
        # keys.ANNOTATION_HIGHLIGHTS: Template(
        #     NamedValue, names.SAVED_AVL_INTERVAL_TREE, SAVED_AVL_INTERVAL_TREE_HIGHLIGHTS_TEMPLATE),
        # keys.ANNOTATION_NOTES: Template(
        #     NamedValue, names.SAVED_AVL_INTERVAL_TREE, SAVED_AVL_INTERVAL_TREE_NOTES_TEMPLATE),
        # keys.ANNOTATION_CLIP_ARTICLES: Template(
        #     NamedValue, names.SAVED_AVL_INTERVAL_TREE, SAVED_AVL_INTERVAL_TREE_CLIP_ARTICLES_TEMPLATE)
    },
)

NAME_TO_TEMPLATE = {
    names.CLOCK_DATA_STORE: None,
    names.DICTIONARY: UTF8STR_TEMPLATE,
    names.LPU: None,
    names.PDF_CONTRAST: None,
    names.SYNC_LPR: BOOL_TEMPLATE,
    names.TPZ_LINE_SPACING: None,
    names.XRAY_OTA_UPDATE_STATE: None,
    names.XRAY_SHOWING_SPOILERS: None,
    names.XRAY_SORTING_STATE: None,
    names.XRAY_TAB_STATE: None,
    names.DICT_PREFS_V_2: DYNAMIC_MAP_TEMPLATE,
    names.END_ACTIONS: DYNAMIC_MAP_TEMPLATE,
    names.READER_METRICS: DYNAMIC_MAP_TEMPLATE,
    names.START_ACTIONS: DYNAMIC_MAP_TEMPLATE,
    names.TRANSLATOR: DYNAMIC_MAP_TEMPLATE,
    names.WIKIPEDIA: DYNAMIC_MAP_TEMPLATE,
    names.BUY_ASIN_RESPONSE_DATA: JSON_TEMPLATE,
    names.NEXT_IN_SERIES_INFO_DATA: JSON_TEMPLATE,
    names.PRICE_INFO_DATA: JSON_TEMPLATE,
    names.ERL: POSITION_TEMPLATE,
    names.LPR: LAST_PAGE_READ_TEMPLATE,
    names.FPR: FPR_TEMPLATE,
    names.UPDATED_LPR: UPDATED_LPR_TEMPLATE,
    names.APNX_KEY: APNX_KEY_TEMPLATE,  # APNX is "Amazon page num xref" (i.e. page num map)
    names.FIXED_LAYOUT_DATA: FIXED_LAYOUT_DATA_TEMPLATE,
    names.SHARING_LIMITS: SHARING_LIMITS_TEMPLATE,
    names.LANGUAGE_STORE: LANGUAGE_STORE_TEMPLATE,
    names.PERIODICALS_VIEW_STATE: PERIODICALS_VIEW_STATE_TEMPLATE,
    names.PURCHASE_STATE_DATA: PURCHASE_STATE_DATA_TEMPLATE,
    names.TIMER_DATA_STORE: TIMER_DATA_STORE_TEMPLATE,
    names.TIMER_DATA_STORE_V2: TIMER_DATA_STOREV2_TEMPLATE,
    names.BOOK_INFO_STORE: BOOK_INFO_STORE_TEMPLATE,
    names.PAGE_HISTORY_STORE: PAGE_HISTORY_STORE_TEMPLATE,
    names.READER_STATE_PREFERENCES: READER_STATE_PREFERENCES_TEMPLATE,
    names.FONT_PREFS: FONT_PREFS_TEMPLATE,
    names.ANNOTATION_CACHE_OBJECT: ANNOTATION_CACHE_OBJECT_TEMPLATE,
    names.ANNOTATION_PERSONAL_BOOKMARK: ANNOTATION_PERSONAL_ELEMENT_TEMPLATE,
    names.ANNOTATION_PERSONAL_HIGHLIGHT: ANNOTATION_PERSONAL_ELEMENT_TEMPLATE,
    names.ANNOTATION_PERSONAL_NOTE: ANNOTATION_PERSONAL_ELEMENT_TEMPLATE,
    names.ANNOTATION_PERSONAL_CLIP_ARTICLE: ANNOTATION_PERSONAL_ELEMENT_TEMPLATE,
}
