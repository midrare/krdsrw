import typing

BYTE_SIZE: typing.Final[int] = 1
BOOL_SIZE: typing.Final[int] = 1
CHAR_SIZE: typing.Final[int] = 2
SHORT_SIZE: typing.Final[int] = 2
INT_SIZE: typing.Final[int] = 4
LONG_SIZE: typing.Final[int] = 8
FLOAT_SIZE: typing.Final[int] = 4
DOUBLE_SIZE: typing.Final[int] = 8

BOOL_TYPE_INDICATOR: typing.Final[int] = 0  # 1-byte bool 0=false, 1=true
INT_TYPE_INDICATOR: typing.Final[int] = 1  # 4-byte signed integer
LONG_TYPE_INDICATOR: typing.Final[int] = 2  # 8-byte signed integer
UTF8STR_TYPE_INDICATOR: typing.Final[int] = (
    # 1-byte bool true if str is empty
    # then 2-byte str length (may be 0)
    # then UTF-8 str bytes of aforementioned length (empty if bool is True)
    3
)
DOUBLE_TYPE_INDICATOR: typing.Final[int] = 4  # 8-byte float
SHORT_TYPE_INDICATOR: typing.Final[int] = 5  # 2 byte signed integer
FLOAT_TYPE_INDICATOR: typing.Final[int] = 6  # 4-byte float
BYTE_TYPE_INDICATOR: typing.Final[int] = 7  # signed byte
CHAR_TYPE_INDICATOR: typing.Final[int] = 9  # single character
OBJECT_BEGIN_TYPE_INDICATOR: typing.Final[int] = (
    -2
)  # named object data structure (name [utf] + data)
OBJECT_END_TYPE_INDICATOR: typing.Final[int] = -1  # end of data for object
