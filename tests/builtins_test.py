import typing

import pytest

from krdsrw.builtins import DictBase
from krdsrw.builtins import ListBase


class TestListBase:
    def test_instantiate(self):
        assert ListBase() is not None  # no error
        assert ListBase([]) is not None  # no error
        assert ListBase([ 2, 4, 6, 8 ]) is not None  # no error

    def test_eq_operator(self):
        o = ListBase()
        assert o == []

        o = ListBase([])
        assert o == []

        o = ListBase([ 1, 2, 3 ])
        assert o == [ 1, 2, 3 ]

    def test_append(self):
        o = ListBase()
        o.append(4)
        o.append(5)
        o.append(6)
        assert o == [ 4, 5, 6 ]

        o = ListBase([ 1, 2, 3 ])
        o.append(4)
        o.append(5)
        o.append(6)
        assert o == [ 1, 2, 3, 4, 5, 6 ]

    def test_extend(self):
        o = ListBase()
        o.extend([ 4, 5, 6 ])
        assert o == [ 4, 5, 6 ]

        o = ListBase([ 1, 2, 3 ])
        o.extend([ 4, 5, 6 ])
        assert o == [ 1, 2, 3, 4, 5, 6 ]

    def test_clear(self):
        o = ListBase()
        o.clear()
        assert o == []

        o = ListBase([1])
        o.clear()
        assert o == []

        o = ListBase([ 1, 2, 3 ])
        o.clear()
        assert o == []

    def test_copy(self):
        o = ListBase()
        assert isinstance(o, ListBase)
        assert o.copy() == []

        o = ListBase([ 1, 2, 3 ])
        assert isinstance(o, ListBase)
        assert o.copy() == [ 1, 2, 3 ]

    def test_count(self):
        o = ListBase()
        assert o.count(9) == 0

        o = ListBase([ 1, 2, 3 ])
        assert o.count(9) == 0

        o = ListBase([9])
        assert o.count(9) == 1

        o = ListBase([ 9, 9, 9 ])
        assert o.count(9) == 3

        o = ListBase([ 1, 9 ])
        assert o.count(9) == 1

        o = ListBase([ 9, 1 ])
        assert o.count(9) == 1

        o = ListBase([ 1, 9, 1 ])
        assert o.count(9) == 1

        o = ListBase([ 9, 1, 9 ])
        assert o.count(9) == 2

    def test_insert(self):
        o = ListBase()
        o.insert(0, 6)
        o.insert(0, 5)
        o.insert(0, 4)
        assert o == [ 4, 5, 6 ]

        o = ListBase([ 1, 2, 3 ])
        o.insert(0, 6)
        o.insert(0, 5)
        o.insert(0, 4)
        assert o == [ 4, 5, 6, 1, 2, 3 ]

        o = ListBase([ 1, 2, 3 ])
        o.insert(1, 4)
        o.insert(3, 5)
        o.insert(5, 6)
        assert o == [ 1, 4, 2, 5, 3, 6 ]

        o = ListBase([ 1, 2, 3 ])
        o.insert(3, 6)
        o.insert(2, 5)
        o.insert(1, 4)
        assert o == [ 1, 4, 2, 5, 3, 6 ]

    def test_remove(self):
        o = ListBase()
        with pytest.raises(ValueError):
            o.remove(9)

        o = ListBase([9])
        o.remove(9)
        assert o == []

        o = ListBase([ 9, 1 ])
        o.remove(9)
        assert o == [1]

        o = ListBase([ 1, 9 ])
        o.remove(9)
        assert o == [1]

        o = ListBase([ 1, 9, 3 ])
        o.remove(9)
        assert o == [ 1, 3 ]

        o = ListBase([ 9, 1, 2 ])
        o.remove(9)
        assert o == [ 1, 2 ]

        o = ListBase([ 1, 2, 9 ])
        o.remove(9)
        assert o == [ 1, 2 ]

        o = ListBase([ 9, 9, 9 ])
        o.remove(9)
        assert o == [ 9, 9 ]

        o = ListBase([ 1, 2, 9, 9 ])
        o.remove(9)
        assert o == [ 1, 2, 9 ]

        o = ListBase([ 9, 1, 2, 9 ])
        o.remove(9)
        assert o == [ 1, 2, 9 ]

        o = ListBase([ 1, 9, 2, 9, 3 ])
        o.remove(9)
        assert o == [ 1, 2, 9, 3 ]

    def test_pop(self):
        o = ListBase()
        with pytest.raises(IndexError):
            o.pop(0)

        o = ListBase()
        with pytest.raises(IndexError):
            o.pop(999)

        o = ListBase([ 1, 2, 3 ])
        assert o.pop(0) == 1

        o = ListBase([ 1, 2, 3 ])
        assert o.pop(1) == 2

        o = ListBase([ 1, 2, 3 ])
        assert o.pop(2) == 3

        o = ListBase([ 1, 2, 3 ])
        assert o.pop(-1) == 3

        o = ListBase([ 1, 2, 3 ])
        assert o.pop(-2) == 2

        o = ListBase([ 1, 2, 3 ])
        assert o.pop(-3) == 1

        with pytest.raises(IndexError):
            o = ListBase([ 1, 2, 3 ])
            o.pop(-4)

        with pytest.raises(IndexError):
            o = ListBase([ 1, 2, 3 ])
            o.pop(3)

        with pytest.raises(IndexError):
            o = ListBase([ 1, 2, 3 ])
            o.pop(-999)

        with pytest.raises(IndexError):
            o = ListBase([ 1, 2, 3 ])
            o.pop(999)

    def test_index(self):
        o = ListBase()
        with pytest.raises(ValueError):
            o.index(9)

        o = ListBase([ 1, 2, 3 ])
        with pytest.raises(ValueError):
            o.index(9)

        o = ListBase([9])
        assert o.index(9) == 0

        o = ListBase([ 9, 9 ])
        assert o.index(9) == 0

        o = ListBase([ 9, 9, 9 ])
        assert o.index(9) == 0

        o = ListBase([ 9, 2, 3 ])
        assert o.index(9) == 0

        o = ListBase([ 1, 9, 3 ])
        assert o.index(9) == 1

        o = ListBase([ 1, 2, 9 ])
        assert o.index(9) == 2

        o = ListBase([ 9, 2, 9 ])
        assert o.index(9) == 0

        o = ListBase([ 9, 9, 3 ])
        assert o.index(9) == 0

        o = ListBase([ 1, 9, 9 ])
        assert o.index(9) == 1

        o = ListBase([ 1, 2, 3, 4, 5 ])
        with pytest.raises(ValueError):
            o.index(9, 0)

        o = ListBase([ 9, 2, 3, 4, 9 ])
        assert o.index(9, 0) == 0

        o = ListBase([ 9, 2, 3, 4, 5 ])
        assert o.index(9, 0) == 0

        o = ListBase([ 1, 2, 3, 4, 9 ])
        assert o.index(9, 0) == 4

        o = ListBase([ 1, 2, 9, 4, 5 ])
        assert o.index(9, 0) == 2

        o = ListBase([ 9, 9, 3, 4, 5 ])
        assert o.index(9, 0) == 0

        o = ListBase([ 1, 9, 9, 4, 5 ])
        assert o.index(9, 0) == 1

        o = ListBase([ 1, 2, 9, 9, 5 ])
        assert o.index(9, 0) == 2

        o = ListBase([ 1, 2, 3, 9, 9 ])
        assert o.index(9, 0) == 3

        o = ListBase([ 9, 2, 3, 4, 9 ])
        assert o.index(9, 3) == 4

        o = ListBase([ 1, 2, 3, 4, 5 ])
        with pytest.raises(ValueError):
            o.index(9, 3)

        o = ListBase([ 9, 2, 3, 4, 5 ])
        with pytest.raises(ValueError):
            o.index(9, 3)

        o = ListBase([ 1, 2, 3, 4, 9 ])
        assert o.index(9, 3) == 4

        o = ListBase([ 1, 2, 9, 4, 5 ])
        with pytest.raises(ValueError):
            o.index(9, 3)

        o = ListBase([ 9, 9, 3, 4, 5 ])
        with pytest.raises(ValueError):
            o.index(9, 3)

        o = ListBase([ 1, 9, 9, 4, 5 ])
        with pytest.raises(ValueError):
            o.index(9, 3)

        o = ListBase([ 1, 2, 9, 9, 5 ])
        assert o.index(9, 3) == 3

        o = ListBase([ 1, 2, 3, 9, 9 ])
        assert o.index(9, 3) == 3

        o = ListBase([ 1, 2, 3, 4, 5 ])
        with pytest.raises(ValueError):
            o.index(9, 0, 3)

        o = ListBase([ 9, 2, 3, 4, 9 ])
        assert o.index(9, 0, 3) == 0

        o = ListBase([ 9, 2, 3, 4, 5 ])
        assert o.index(9, 0, 3) == 0

        o = ListBase([ 1, 2, 3, 4, 9 ])
        with pytest.raises(ValueError):
            o.index(9, 0, 3)

        o = ListBase([ 1, 2, 9, 4, 5 ])
        assert o.index(9, 0, 3) == 2

        o = ListBase([ 9, 9, 3, 4, 5 ])
        assert o.index(9, 0, 3) == 0

        o = ListBase([ 1, 9, 9, 4, 5 ])
        assert o.index(9, 0, 3) == 1

        o = ListBase([ 1, 2, 9, 9, 5 ])
        assert o.index(9, 0, 3) == 2

        o = ListBase([ 1, 2, 3, 9, 9 ])
        with pytest.raises(ValueError):
            o.index(9, 0, 3)

        o = ListBase([ 9, 2, 3, 4, 9 ])
        assert o.index(9, 3, 5) == 4

        o = ListBase([ 1, 2, 3, 4, 5 ])
        with pytest.raises(ValueError):
            o.index(9, 3, 5)

        o = ListBase([ 9, 2, 3, 4, 5 ])
        with pytest.raises(ValueError):
            o.index(9, 3, 5)

        o = ListBase([ 1, 2, 3, 4, 9 ])
        assert o.index(9, 3, 5) == 4

        o = ListBase([ 1, 2, 9, 4, 5 ])
        with pytest.raises(ValueError):
            o.index(9, 3, 5)

        o = ListBase([ 9, 9, 3, 4, 5 ])
        with pytest.raises(ValueError):
            o.index(9, 3, 5)

        o = ListBase([ 1, 9, 9, 4, 5 ])
        with pytest.raises(ValueError):
            o.index(9, 3, 5)

        o = ListBase([ 1, 2, 9, 9, 5 ])
        assert o.index(9, 3, 5) == 3

        o = ListBase([ 1, 2, 3, 9, 9 ])
        assert o.index(9, 3, 5) == 3

        o = ListBase([ 1, 2, 3, 4, 9 ])
        assert o.index(9, 0, 6) == 4

        o = ListBase([ 1, 2, 3, 4, 9 ])
        assert o.index(9, 0, 999) == 4

        o = ListBase([ 9, 2, 3, 4, 9 ])
        assert o.index(9, 0, 999) == 0

        o = ListBase([ 9, 2, 3, 4, 9 ])
        assert o.index(9, 0, 999) == 0

        o = ListBase([ 9, 2, 9, 4, 9 ])
        assert o.index(9, 0, 999) == 0

        o = ListBase([ 1, 2, 9, 4, 5 ])
        assert o.index(9, 0, 999) == 2

        o = ListBase([ 1, 2, 3, 4, 9 ])
        assert o.index(9, -1, 999) == 4

        o = ListBase([ 1, 2, 3, 4, 5 ])
        with pytest.raises(ValueError):
            o.index(9, -1, 1)

        o = ListBase([ 1, 2, 3, 4, 9 ])
        with pytest.raises(ValueError):
            o.index(9, -1, 1)

        o = ListBase([ 9, 2, 3, 4, 9 ])
        with pytest.raises(ValueError):
            o.index(9, -1, 1)

        o = ListBase([ 9, 2, 3, 4, 5 ])
        with pytest.raises(ValueError):
            o.index(9, -1, 1)

        o = ListBase([ 9, 2, 9, 4, 9 ])
        with pytest.raises(ValueError):
            o.index(9, -1, 1)

        o = ListBase([ 1, 2, 9, 4, 5 ])
        with pytest.raises(ValueError):
            o.index(9, -1, 1)

        o = ListBase([ 1, 2, 3, 4, 5 ])
        with pytest.raises(ValueError):
            o.index(9, -3, 5)

        o = ListBase([ 1, 2, 3, 4, 9 ])
        assert o.index(9, -3, 5) == 4

        o = ListBase([ 9, 2, 3, 4, 9 ])
        assert o.index(9, -3, 5) == 4

        o = ListBase([ 9, 2, 3, 4, 5 ])
        with pytest.raises(ValueError):
            o.index(9, -3, 5)

        o = ListBase([ 9, 2, 9, 4, 9 ])
        assert o.index(9, -3, 5) == 2

        o = ListBase([ 1, 2, 9, 4, 5 ])
        assert o.index(9, -3, 5) == 2

        o = ListBase([ 1, 2, 3, 4, 5 ])
        with pytest.raises(ValueError):
            o.index(9, -4, -2)

        o = ListBase([ 1, 2, 3, 4, 9 ])
        with pytest.raises(ValueError):
            o.index(9, -4, -2)

        o = ListBase([ 9, 2, 3, 4, 9 ])
        with pytest.raises(ValueError):
            o.index(9, -4, -2)

        o = ListBase([ 9, 2, 3, 4, 5 ])
        with pytest.raises(ValueError):
            o.index(9, -4, -2)

        o = ListBase([ 9, 2, 9, 4, 9 ])
        assert o.index(9, -4, -2) == 2

        o = ListBase([ 1, 2, 9, 4, 5 ])
        assert o.index(9, -4, -2) == 2

    def test_sort(self):
        o = ListBase()
        o.sort()
        assert o == []

        o = ListBase([ 1, 2, 3, 4, 5 ])
        o.sort()
        assert o == [ 1, 2, 3, 4, 5 ]

        o = ListBase([ 5, 4, 3, 2, 1 ])
        o.sort()
        assert o == [ 1, 2, 3, 4, 5 ]

        o = ListBase([ 1, 5, 2, 4, 3 ])
        o.sort()
        assert o == [ 1, 2, 3, 4, 5 ]

        o = ListBase([ 1, 2, 3, 4, 5 ])
        o.sort(key=lambda n: n * 2 if n % 2 == 0 else n)
        assert o == [ 1, 3, 2, 5, 4 ]

        o = ListBase([ 5, 4, 3, 2, 1 ])
        o.sort(key=lambda n: n * 2 if n % 2 == 0 else n)
        assert o == [ 1, 3, 2, 5, 4 ]

        o = ListBase([ 1, 5, 2, 4, 3 ])
        o.sort(key=lambda n: n * 2 if n % 2 == 0 else n)
        assert o == [ 1, 3, 2, 5, 4 ]

        o = ListBase([ 1, 2, 3, 4, 5 ])
        o.sort(reverse=True)
        assert o == [ 5, 4, 3, 2, 1 ]

        o = ListBase([ 5, 4, 3, 2, 1 ])
        o.sort(reverse=True)
        assert o == [ 5, 4, 3, 2, 1 ]

        o = ListBase([ 1, 5, 2, 4, 3 ])
        o.sort(reverse=True)
        assert o == [ 5, 4, 3, 2, 1 ]

        o = ListBase([ 1, 2, 3, 4, 5 ])
        o.sort(key=lambda n: n * 2 if n % 2 == 0 else n, reverse=True)
        assert o == [ 4, 5, 2, 3, 1 ]

        o = ListBase([ 5, 4, 3, 2, 1 ])
        o.sort(key=lambda n: n * 2 if n % 2 == 0 else n, reverse=True)
        assert o == [ 4, 5, 2, 3, 1 ]

        o = ListBase([ 1, 5, 2, 4, 3 ])
        o.sort(key=lambda n: n * 2 if n % 2 == 0 else n, reverse=True)
        assert o == [ 4, 5, 2, 3, 1 ]

    def test_reverse(self):
        o = ListBase()
        o.reverse()
        assert o == []

        o = ListBase([ 1, 2, 3, 4, 5 ])
        o.reverse()
        assert o == [ 5, 4, 3, 2, 1 ]

    def test_allowed(self):
        class CustomClass(ListBase[int]):
            @typing.override
            def _is_allowed(self, value: int) -> bool:
                return isinstance(value, int)

        o = CustomClass()  # no error
        assert o is not None

        o = CustomClass([ 1, 2, 3 ])  # no error
        assert o == [ 1, 2, 3 ]

        o = CustomClass([ 1, 2, 3 ])
        o[1] = 9  # no error
        assert o == [ 1, 9, 3 ]

        o = CustomClass([ 1, 2, 3 ])
        with pytest.raises(ValueError):
            o[1] = 'INVALID_VALUE'

        o = CustomClass()
        o.append(9)  # no error
        assert o == [9]

        o = CustomClass()
        with pytest.raises(ValueError):
            o.append('INVALID_VALUE')

        o = CustomClass()
        o.extend([ 1, 2, 3 ])
        assert o == [ 1, 2, 3 ]

        o = CustomClass()
        with pytest.raises(ValueError):
            o.extend([ 1, 2, 'INVALID_VALUE'])

        o = CustomClass()
        with pytest.raises(ValueError):
            o.insert(0, 'INVALID_VALUE')

        o = CustomClass([ 1, 2, 3 ])
        with pytest.raises(ValueError):
            o.insert(1, 'INVALID_VALUE')

        o = CustomClass()
        o += [ 1, 2, 3 ]  # no error
        assert o == [ 1, 2, 3 ]

        o = CustomClass()
        with pytest.raises(ValueError):
            o += [ 1, 'INVALID_VALUE', 3 ]

        o = CustomClass([ 1, 2, 3 ])
        o[2:3] = [ 4, 5, 6 ]  # no error
        assert o == [ 1, 2, 4, 5, 6 ]

        o = CustomClass([ 1, 2, 3 ])
        with pytest.raises(ValueError):
            o[2:3] = [ 4, 'INVALID_VALUE', 6 ]

        o = CustomClass([ 1, 2, 3 ])
        o[0:2] = [ 4, 5, 6 ]  # no error
        assert o == [ 4, 5, 6, 3 ]

        o = CustomClass([ 1, 2, 3 ])
        with pytest.raises(ValueError):
            o[0:2] = [ 4, 'INVALID_VALUE', 6 ]

        o = CustomClass([ 1, 2, 3 ])
        o[1:999] = [ 4, 5, 6 ]  # no error
        assert o == [ 1, 4, 5, 6 ]

        o = CustomClass([ 1, 2, 3 ])
        with pytest.raises(ValueError):
            o[1:999] = [ 4, 'INVALID_VALUE', 6 ]

    def test_transform(self):
        class CustomClass(ListBase[int]):
            @typing.override
            def _transform(self, value: int) -> int:
                return value**2

        o = CustomClass()  # no error
        assert o is not None

        o = CustomClass()
        o.append(8)
        assert o == [64]

        o = CustomClass([ 2, 4, 6, 8 ])
        assert o == [ 4, 16, 36, 64 ]

        o = CustomClass([ 2, 4, 6, 8 ])
        o[1] = 12  # no error
        assert o == [ 4, 144, 36, 64 ]

        o = CustomClass()
        o.append(4)
        assert o == [16]

        o = CustomClass()
        o.extend([ 1, 2, 3 ])
        assert o == [ 1, 4, 9 ]

        o = CustomClass()
        o.insert(0, 4)
        assert o == [16]

        o = CustomClass([ 1, 2, 3 ])
        o.insert(1, 5)
        assert o == [ 1, 25, 4, 9 ]

        o = CustomClass()
        o += [ 1, 2, 3 ]
        assert o == [ 1, 4, 9 ]

        o = CustomClass()
        o += [ 1, 2, 3 ]
        assert o == [ 1, 4, 9 ]

        o = CustomClass([ 1, 2, 3 ])
        o[2:3] = [ 4, 5, 6 ]
        assert o == [ 1, 4, 16, 25, 36 ]

        o = CustomClass([ 1, 2, 3 ])
        o[0:2] = [ 4, 5, 6 ]
        assert o == [ 16, 25, 36, 9 ]

        o = CustomClass([ 1, 2, 3 ])
        o[1:999] = [ 4, 5, 6 ]
        assert o == [ 1, 16, 25, 36 ]

    def test_modified(self):
        o = ListBase()
        assert not o.is_modified

        o = ListBase()
        o.append(2)
        assert o.is_modified

        o = ListBase([ 2, 4, 6, 8 ])
        assert not o.is_modified

        o = ListBase([ 2, 4, 6, 8 ])
        o[1] = 24
        assert o.is_modified

        o = ListBase()
        o.extend([ 1, 2, 3 ])
        assert o.is_modified

        o = ListBase()
        o.insert(0, 4)
        assert o.is_modified

        o = ListBase([ 1, 2, 3 ])
        o.insert(1, 5)
        assert o.is_modified

        o = ListBase()
        o += [ 1, 2, 3 ]
        assert o.is_modified

        o = ListBase([ 1, 2, 3 ])
        o[2:3] = [ 4, 5, 6 ]
        assert o.is_modified

        o = ListBase([ 1, 2, 3 ])
        o[0:2] = [ 4, 5, 6 ]
        assert o.is_modified

        o = ListBase([ 1, 2, 3 ])
        o[1:9] = [ 4, 5, 6 ]
        assert o.is_modified

        o = ListBase([ 1, 2, 3 ])
        o[-1:0] = [ 4, 5, 6 ]
        assert o.is_modified

        o = ListBase([ 1, 2, 3 ])
        o[-9:0] = [ 4, 5, 6 ]
        assert o.is_modified

        o = ListBase([ 1, 2, 3 ])
        o[-1:9] = [ 4, 5, 6 ]
        assert o.is_modified

        o = ListBase([ 1, 2, 3 ])
        o[-9:9] = [ 4, 5, 6 ]
        assert o.is_modified

    def test_chain(self):
        class CustomClass(ListBase[typing.Any]):
            pass

        o2 = CustomClass()
        o = CustomClass([o2])
        assert not o.is_modified
        assert not o2.is_modified

        o2 = CustomClass()
        o = CustomClass([o2])
        o.append(o2)
        assert not o2.is_modified
        assert o.is_modified

        o = CustomClass([ 1, 2, 3 ])
        o2 = CustomClass([ 4, 5, 6 ])
        o.append(o2)
        assert o == [ 1, 2, 3, [ 4, 5, 6 ] ]

        o2 = CustomClass([ 4, 5, 5 ])
        o = CustomClass([ 1, 2, o2 ])
        assert not o2.is_modified
        assert not o.is_modified

        o2 = CustomClass([ 4, 5, 5 ])
        o = CustomClass([ 1, 2, o2 ])
        o.append(9)
        assert o.is_modified
        assert not o2.is_modified

        o2 = CustomClass([ 4, 5, 5 ])
        o = CustomClass([ 1, 2, o2 ])
        o2.append(9)
        assert not o.is_modified
        assert o2.is_modified

        o3 = CustomClass([ 5, 6 ])
        o2 = CustomClass([ 3, 4, o3 ])
        o = CustomClass([ 1, 2, o2 ])
        assert o == [ 1, 2, [ 3, 4, [ 5, 6 ] ] ]
        assert o2 == [ 3, 4, [ 5, 6 ] ]
        assert o3 == [ 5, 6 ]
        assert not o.is_modified
        assert not o2.is_modified
        assert not o3.is_modified

        o3 = CustomClass([ 5, 6 ])
        o2 = CustomClass([ 3, 4, o3 ])
        o = CustomClass([ 1, 2, o2 ])
        o3.append(9)
        assert o == [ 1, 2, [ 3, 4, [ 5, 6, 9 ] ] ]
        assert o2 == [ 3, 4, [ 5, 6, 9 ] ]
        assert o3 == [ 5, 6, 9 ]
        assert not o.is_modified
        assert not o2.is_modified
        assert o3.is_modified

        o3 = CustomClass([ 5, 6 ])
        o2 = CustomClass([ 3, 4, o3 ])
        o = CustomClass([ 1, 2, o2 ])
        o2.append(9)
        assert o == [ 1, 2, [ 3, 4, [ 5, 6 ], 9 ] ]
        assert o2 == [ 3, 4, [ 5, 6 ], 9 ]
        assert o3 == [ 5, 6 ]
        assert not o.is_modified
        assert o2.is_modified
        assert not o3.is_modified

        o3 = CustomClass([ 5, 6 ])
        o2 = CustomClass([ 3, 4, o3 ])
        o = CustomClass([ 1, 2, o2 ])
        o.append(9)
        assert o == [ 1, 2, [ 3, 4, [ 5, 6 ] ], 9 ]
        assert o2 == [ 3, 4, [ 5, 6 ] ]
        assert o3 == [ 5, 6 ]
        assert o.is_modified
        assert not o2.is_modified
        assert not o3.is_modified


class TestDictBase:
    def test_instantiate(self):
        o = DictBase()  # no error
        assert o == {}

        o = DictBase({})  # no error
        assert o == {}

        o = DictBase({ 'a': 1, 'b': 2, 'c': 3 })
        assert o == { 'a': 1, 'b': 2, 'c': 3 }

    def test_eq_operator(self):
        o = DictBase()
        assert o == {}

        o = DictBase({})
        assert o == {}

        o = DictBase({ 'a': 1, 'b': 2, 'c': 3 })
        assert o == { 'a': 1, 'b': 2, 'c': 3 }

    def test_getitem_operator(self):
        o = DictBase()
        with pytest.raises(KeyError):
            o['a']

        o = DictBase({ 'a': 1, 'b': 2, 'c': 3 })
        assert o['a'] == 1

        o = DictBase({ 'a': 1, 'b': 2, 'c': 3 })
        with pytest.raises(KeyError):
            o['x']

    def test_setitem_operator(self):
        o = DictBase()
        o['x'] = -1
        assert o == { 'x': -1 }

        o = DictBase({ 'a': 1, 'b': 2, 'c': 3 })
        o['x'] = -1
        assert o == { 'a': 1, 'b': 2, 'c': 3, 'x': -1 }

        o = DictBase({ 'a': 1, 'b': 2, 'c': 3 })
        o['b'] = -1
        o['x'] = -2
        assert o == { 'a': 1, 'b': -1, 'c': 3, 'x': -2 }

    def test_or_operator(self):
        class CustomClass(DictBase[str, int]):
            @typing.override
            def _is_value_writable(
                self,
                value: typing.Any,
                key: typing.Any,
            ) -> bool:
                return isinstance(key, str) and isinstance(value, int)

        o = CustomClass({ 'a': 1 }) | { 'b': 2 }  # no error
        assert isinstance(o, CustomClass)
        assert o == { 'a': 1, 'b': 2 }

        with pytest.raises(ValueError):
            o = CustomClass({ 'a': 1 }) | { 'b': b'B'}

        o = { 'a': 1 } | CustomClass({ 'b': 2 })
        assert o == { 'a': 1, 'b': 2 }

        o = { 'a': b'A'} | CustomClass({ 'b': 2 })
        assert o == { 'a': b'A', 'b': 2 }

    def test_ior_operator(self):
        class CustomClass(DictBase[str, int]):
            @typing.override
            def _is_value_writable(
                self,
                value: typing.Any,
                key: typing.Any,
            ) -> bool:
                return isinstance(key, str) and isinstance(value, int)

        o = CustomClass({ 'a': 1 })
        with pytest.raises(ValueError):
            o |= { 'b': 'INVALID_VALUE'}

        o = CustomClass({ 'a': 1 })
        o |= { 'b': 2 }
        assert isinstance(o, CustomClass)
        assert o == { 'a': 1, 'b': 2 }

        o = { 'a': 1 }
        o |= CustomClass({ 'b': 2 })
        assert o == { 'a': 1, 'b': 2 }

    def test_len_operator(self):
        o = DictBase()
        assert len(o) == 0

        o = DictBase({ 'a': 1, 'b': 2, 'c': 3 })
        assert len(o) == 3

    def test_del_operator(self):
        o = DictBase()
        with pytest.raises(KeyError):
            del o['a']

        o = DictBase({ 'a': 1, 'b': 2, 'c': 3 })
        del o['a']
        assert o == { 'b': 2, 'c': 3 }

    def test_in_operator(self):
        o = DictBase()
        assert 'a' not in o

        o = DictBase({ 'a': 1, 'b': 2, 'c': 3 })
        assert 'a' in o

    def test_iter_operator(self):
        o = DictBase()
        assert list(iter(o)) == []

        o = DictBase({ 'a': 1, 'b': 2, 'c': 3 })
        assert list(iter(o)) == [ 'a', 'b', 'c']

    def test_reversed_operator(self):
        o = DictBase()
        assert list(reversed(o)) == []

        o = DictBase({ 'a': 1, 'b': 2, 'c': 3 })
        assert list(reversed(o)) == [ 'c', 'b', 'a']

        o = DictBase({ 'a': 1, 'b': 2, 'c': 3 })
        o['a'] = 9
        assert list(reversed(o)) == [ 'c', 'b', 'a']

        o = DictBase({ 'a': 1, 'b': 2, 'c': 3 })
        o['d'] = 9
        assert list(reversed(o)) == [ 'd', 'c', 'b', 'a']

    def test_update(self):
        o = DictBase()
        o.update({ 'x': -1, 'y': -2, 'z': -3 })
        assert o == { 'x': -1, 'y': -2, 'z': -3 }

        o = DictBase({ 'a': 1, 'b': 2, 'c': 3 })
        o.update({ 'x': -1, 'y': -2, 'z': -3 })
        assert o == { 'a': 1, 'b': 2, 'c': 3, 'x': -1, 'y': -2, 'z': -3 }

        o = DictBase({ 'a': 1, 'b': 2, 'c': 3 })
        o.update({ 'a': -1, 'x': -2 })
        assert o == { 'a': -1, 'b': 2, 'c': 3, 'x': -2 }

    def test_setdefault(self):
        o = DictBase()
        o.setdefault('x', -1)
        o.setdefault('y', -2)
        o.setdefault('z', -3)
        assert o == { 'x': -1, 'y': -2, 'z': -3 }

        o = DictBase({ 'a': 1, 'b': 2, 'c': 3 })
        o.setdefault('x', -1)
        o.setdefault('y', -2)
        o.setdefault('z', -3)
        assert o == { 'a': 1, 'b': 2, 'c': 3, 'x': -1, 'y': -2, 'z': -3 }

        o = DictBase({ 'a': 1, 'b': 2, 'c': 3 })
        o.setdefault('a', -1)
        o.setdefault('x', -2)
        assert o == { 'a': 1, 'b': 2, 'c': 3, 'x': -2 }

    def test_clear(self):
        o = DictBase()
        o.clear()
        assert o == {}

        o = DictBase({ 'a': 1, 'b': 2, 'c': 3 })
        o.clear()
        assert o == {}

    def test_copy(self):
        o = DictBase()
        assert isinstance(o, DictBase)
        assert o.copy() == {}

        o = DictBase({ 'a': 1, 'b': 2, 'c': 3 })
        assert isinstance(o, DictBase)
        assert o.copy() == { 'a': 1, 'b': 2, 'c': 3 }

    def test_fromkeys(self):
        o = DictBase.fromkeys([], 0)
        assert o == {}

        o = DictBase.fromkeys([ 'a', 'b', 'c'], 0)
        assert o == { 'a': 0, 'b': 0, 'c': 0 }

        o = DictBase.fromkeys([])
        assert o == {}

        o = DictBase.fromkeys([ 'a', 'b', 'c'])
        assert o == { 'a': None, 'b': None, 'c': None }

    def test_get(self):
        o = DictBase()
        assert o.get('a') is None

        o = DictBase()
        assert o.get('a', 123) == 123

        o = DictBase({ 'a': 1, 'b': 2, 'c': 3 })
        assert o.get('a') == 1

        o = DictBase({ 'a': 1, 'b': 2, 'c': 3 })
        assert o.get('x') is None

        o = DictBase({ 'a': 1, 'b': 2, 'c': 3 })
        assert o.get('x', 9) == 9

    def test_items(self):
        o = DictBase()
        assert list(o.items()) == []

        o = DictBase({ 'a': 1, 'b': 2, 'c': 3 })
        assert list(o.items()) == [('a', 1), ('b', 2), ('c', 3)]

    def test_keys(self):
        o = DictBase()
        assert list(o.keys()) == []

        o = DictBase({ 'a': 1, 'b': 2, 'c': 3 })
        assert list(o.keys()) == [ 'a', 'b', 'c']

        o = DictBase({ 'a': 1, 'b': 2, 'c': 3 })
        o['a'] = 5
        assert list(o.keys()) == [ 'a', 'b', 'c']

        o = DictBase({ 'a': 1, 'b': 2, 'c': 3 })
        o['d'] = 5
        assert list(o.keys()) == [ 'a', 'b', 'c', 'd']

    def test_values(self):
        o = DictBase()
        assert list(o.values()) == []

        o = DictBase({ 'a': 1, 'b': 2, 'c': 3 })
        assert list(o.values()) == [ 1, 2, 3 ]

        o = DictBase({ 'a': 1, 'b': 2, 'c': 3 })
        o['a'] = 5
        assert list(o.values()) == [ 5, 2, 3 ]

        o = DictBase({ 'a': 1, 'b': 2, 'c': 3 })
        o['d'] = 5
        assert list(o.values()) == [ 1, 2, 3, 5 ]

    def test_pop(self):
        o = DictBase()
        with pytest.raises(KeyError):
            o.pop('a')

        o = DictBase()
        assert o.pop('a', 0) == 0

        o = DictBase({ 'a': 1, 'b': 2, 'c': 3 })
        assert o.pop('a', 9) == 1

        o = DictBase({ 'a': 1, 'b': 2, 'c': 3 })
        with pytest.raises(KeyError):
            assert o.pop('x') == 9

        o = DictBase({ 'a': 1, 'b': 2, 'c': 3 })
        assert o.pop('x', 9) == 9

    def test_popitem(self):
        o = DictBase()
        with pytest.raises(KeyError):
            o.popitem()

        o = DictBase({ 'a': 1, 'b': 2, 'c': 3 })
        assert o.popitem() == ('c', 3)

        o = DictBase({ 'a': 1, 'b': 2, 'c': 3 })
        o['a'] = 5
        assert o.popitem() == ('c', 3)

        o = DictBase({ 'a': 1, 'b': 2, 'c': 3 })
        o['x'] = -1
        assert o.popitem() == ('x', -1)

    def test_is_writable(self):
        class CustomClass(DictBase[str, int]):
            @typing.override
            def _is_key_writable(
                self,
                key: typing.Any,
            ) -> bool:
                return isinstance(key, str) and len(key) <= 1

            @typing.override
            def _is_value_writable(
                self,
                value: typing.Any,
                key: typing.Any,
            ) -> bool:
                return isinstance(key, str) \
                and len(key) <= 1 \
                and isinstance(value, int)

        o = CustomClass({ 'a': 1, 'b': 2, 'c': 3 })  # no error
        assert o == { 'a': 1, 'b': 2, 'c': 3 }

        with pytest.raises(ValueError):
            CustomClass({ 'a': b'AAA', 'b': b'BBB', 'c': b'CCC'})

        with pytest.raises(KeyError):
            CustomClass({ 'aa': 1, 'bb': 2, 'cc': 3 })

        with pytest.raises(KeyError):
            CustomClass({ 'aa': b'AAA', 'bb': b'BBB', 'cc': b'CCC'})

        o = CustomClass()
        o.setdefault('a', 9)
        assert o == { 'a': 9 }

        with pytest.raises(KeyError):
            o = CustomClass()
            o.setdefault('aa', 4)

        with pytest.raises(ValueError):
            o = CustomClass()
            o.setdefault('a', b'ZZZ')  # type: ignore

        with pytest.raises(KeyError):
            o = CustomClass()
            o.setdefault('aa', b'ZZZ')  # type: ignore

        o = CustomClass()
        o.update({ 'a': 123, 'b': 456 })
        assert o == { 'a': 123, 'b': 456 }

        o = CustomClass()
        with pytest.raises(ValueError):
            o.update({ 'a': 12, 'b': 4.5 })  # type: ignore

        o = CustomClass()
        with pytest.raises(KeyError):
            o.update({ 'aa': b'AAA', 'bb': b'BBB'})  # type: ignore

        o = CustomClass()
        o |= { 'a': 1, 'b': 2, 'c': 3 }  # no error
        assert o == { 'a': 1, 'b': 2, 'c': 3 }

        with pytest.raises(ValueError):
            o = CustomClass()
            o |= { 'a': b'AAA', 'b': 2, 'c': 3 }

        with pytest.raises(KeyError):
            o = CustomClass()
            o |= { 'aa': 1, 'b': 2, 'c': 3 }

        with pytest.raises(KeyError):
            o = CustomClass()
            o |= { 'aa': b'AAA', 'b': 2, 'c': 3 }

        o = CustomClass()
        o['a'] = 1  # no error
        assert o == { 'a': 1 }

        with pytest.raises(ValueError):
            o = CustomClass()
            o['a'] = b'AAA'  # type: ignore

        with pytest.raises(KeyError):
            o = CustomClass()
            o['aaa'] = 1

        with pytest.raises(KeyError):
            o = CustomClass()
            o['aaa'] = b'AAA'  # type: ignore

        o = CustomClass.fromkeys([ 'a', 'b', 'c'], 0)  # no error
        assert o == { 'a': 0, 'b': 0, 'c': 0 }

        with pytest.raises(KeyError):
            o = CustomClass.fromkeys([ 'a', 'bb', 'c'], 0)

        with pytest.raises(ValueError):
            o = CustomClass.fromkeys([ 'a', 'b', 'c'], b'ZZZ')  # type: ignore

        with pytest.raises(KeyError):
            o = CustomClass.fromkeys([ 'aa', 'bb', 'c'], b'ZZZ')  # type: ignore

        with pytest.raises(ValueError):
            o = CustomClass.fromkeys([ 'a', 'bb', 'c'], b'ZZZ')  # type: ignore

    def test_transform_key(self):
        class CustomClass(DictBase[str, int]):
            @typing.override
            def _transform_key(self, key: typing.Any) -> str:
                return key.capitalize()

        o = CustomClass({ 'a': 1, 'b': 2, 'c': 3 })
        assert o == { 'A': 1, 'B': 2, 'C': 3 }

        o = CustomClass.fromkeys([ 'a', 'b', 'c'], 3)
        assert o == { 'A': 3, 'B': 3, 'C': 3 }

        o = CustomClass()
        o.setdefault('a', 3)
        assert o == { 'A': 3 }

        o = CustomClass()
        o.update({ 'a': 1, 'b': 2 })
        assert o == { 'A': 1, 'B': 2 }

        o = CustomClass()
        o |= { 'a': 1, 'b': 2, 'c': 3 }
        assert o == { 'A': 1, 'B': 2, 'C': 3 }

        o = CustomClass()
        o['a'] = 3
        assert o == { 'A': 3 }

        o = CustomClass({ 'a': 1, 'b': 2, 'c': 3 })
        o.setdefault('a', 9)
        assert o == { 'A': 1, 'B': 2, 'C': 3 }

        o = CustomClass({ 'a': 1, 'b': 2, 'c': 3 })
        o.setdefault('x', 9)
        assert o == { 'A': 1, 'B': 2, 'C': 3, 'X': 9 }

        o = CustomClass({ 'a': 1, 'b': 2, 'c': 3 })
        o.update({ 'a': 5, 'b': 6 })
        assert o == { 'A': 5, 'B': 6, 'C': 3 }

        o = CustomClass({ 'a': 1, 'b': 2, 'c': 3 })
        o |= { 'a': 4, 'b': 5, 'c': 6 }
        assert o == { 'A': 1, 'B': 2, 'C': 3 }

        o = CustomClass({ 'a': 1, 'b': 2, 'c': 3 })
        o |= { 'a': 4, 'd': 7, 'c': 6, 'e': 8 }
        assert o == { 'A': 1, 'B': 2, 'C': 3, 'D': 7, 'E': 8 }

        o = CustomClass({ 'a': 1, 'b': 2, 'c': 3 })
        o['a'] = 10
        assert o == { 'A': 10, 'B': 2, 'C': 3 }

        o = CustomClass({ 'a': 1, 'b': 2, 'c': 3 })
        o['x'] = 10
        assert o == { 'A': 1, 'B': 2, 'C': 3, 'X': 10 }

        o = CustomClass({ 'a': 1, 'B': 2 })
        assert o['a'] == 1

        o = CustomClass({ 'a': 1, 'B': 2 })
        assert o['A'] == 1

        o = CustomClass({ 'a': 1, 'B': 2 })
        assert o['b'] == 2

        o = CustomClass({ 'a': 1, 'B': 2 })
        assert o['B'] == 2

        o = CustomClass({ 'a': 1, 'B': 2 })
        del o['a']  # no error
        assert o == { 'B': 2 }

        o = CustomClass({ 'a': 1, 'B': 2 })
        del o['A']  # no error
        assert o == { 'B': 2 }

        o = CustomClass({ 'a': 1, 'B': 2 })
        del o['b']  # no error
        assert o == { 'A': 1 }

        o = CustomClass({ 'a': 1, 'B': 2 })
        del o['B']  # no error
        assert o == { 'A': 1 }

        o = CustomClass({ 'a': 1, 'B': 2 })
        with pytest.raises(KeyError):
            del o['c']

        o = CustomClass({ 'a': 1, 'B': 2 })
        assert o.get('a') == 1

        o = CustomClass({ 'a': 1, 'B': 2 })
        assert o.get('A') == 1

        o = CustomClass({ 'a': 1, 'B': 2 })
        assert o.get('b') == 2

        o = CustomClass({ 'a': 1, 'B': 2 })
        assert o.get('B') == 2

        o = CustomClass({ 'a': 1, 'B': 2 })
        assert o.get('B') == 2

        o = CustomClass({ 'a': 1, 'B': 2 })
        assert o.get('c') is None

        o = CustomClass({ 'a': 1, 'B': 2 })
        assert o.pop('a') == 1

        o = CustomClass({ 'a': 1, 'B': 2 })
        assert o.pop('A') == 1

        o = CustomClass({ 'a': 1, 'B': 2 })
        assert o.pop('b') == 2

        o = CustomClass({ 'a': 1, 'B': 2 })
        assert o.pop('B') == 2

        o = CustomClass({ 'a': 1, 'B': 2 })
        assert o.pop('B') == 2

        with pytest.raises(KeyError):
            o = CustomClass({ 'a': 1, 'B': 2 })
            o.pop('c')

        o = CustomClass({ 'a': 1, 'B': 2 })
        assert 'a' in o

        o = CustomClass({ 'a': 1, 'B': 2 })
        assert 'A' in o

        o = CustomClass({ 'a': 1, 'B': 2 })
        assert 'b' in o

        o = CustomClass({ 'a': 1, 'B': 2 })
        assert 'B' in o

        with pytest.raises(KeyError):
            o = CustomClass()
            del o['a']

        o = CustomClass({ 'a': 1 })
        del o['a']  # no error
        assert o == {}

        o = CustomClass({ 'a': 1 })
        del o['A']  # no error
        assert o == {}

        o = CustomClass({ 'a': 1 })
        del o['A']  # no error
        assert o == {}

        o = CustomClass({ 'a': 1, 'b': 2, 'c': 3 })
        del o['a']  # no error
        assert o == { 'B': 2, 'C': 3 }

        o = CustomClass({ 'a': 1, 'b': 2, 'c': 3 })
        del o['A']  # no error
        assert o == { 'B': 2, 'C': 3 }

    def test_transform_value(self):
        class CustomClass(DictBase[str, int]):
            @typing.override
            def _transform_value(
                self,
                value: typing.Any,
                key: None | typing.Any = None,
            ) -> int:
                return value**2

        o = CustomClass({ 'a': 1, 'b': 2, 'c': 3 })
        assert o == { 'a': 1, 'b': 4, 'c': 9 }

        o = CustomClass.fromkeys([ 'a', 'b', 'c'], 3)
        assert o == { 'a': 9, 'b': 9, 'c': 9 }

        o = CustomClass()
        o.setdefault('a', 3)
        assert o == { 'a': 9 }

        o = CustomClass()
        o.update({ 'a': 1, 'b': 2 })
        assert o == { 'a': 1, 'b': 4 }

        o = CustomClass()
        o |= { 'a': 1, 'b': 2, 'c': 3 }
        assert o == { 'a': 1, 'b': 4, 'c': 9 }

        o = CustomClass()
        o['a'] = 3
        assert o == { 'a': 9 }

        o = CustomClass({ 'a': 1, 'b': 2, 'c': 3 })
        o.setdefault('a', 9)
        assert o == { 'a': 1, 'b': 4, 'c': 9 }

        o = CustomClass({ 'a': 1, 'b': 2, 'c': 3 })
        o.setdefault('x', 9)
        assert o == { 'a': 1, 'b': 4, 'c': 9, 'x': 81 }

        o = CustomClass({ 'a': 1, 'b': 2, 'c': 3 })
        o.update({ 'a': 5, 'b': 6 })
        assert o == { 'a': 25, 'b': 36, 'c': 9 }

        o = CustomClass({ 'a': 1, 'b': 2, 'c': 3 })
        o |= { 'a': 4, 'b': 5, 'c': 6 }
        assert o == { 'a': 1, 'b': 4, 'c': 9 }

        o = CustomClass({ 'a': 1, 'b': 2, 'c': 3 })
        o |= { 'a': 4, 'd': 7, 'c': 6, 'e': 8 }
        assert o == { 'a': 1, 'b': 4, 'c': 9, 'd': 49, 'e': 64 }

        o = CustomClass({ 'a': 1, 'b': 2, 'c': 3 })
        o['a'] = 10
        assert o == { 'a': 100, 'b': 4, 'c': 9 }

        o = CustomClass({ 'a': 1, 'b': 2, 'c': 3 })
        o['x'] = 10
        assert o == { 'a': 1, 'b': 4, 'c': 9, 'x': 100 }

    def test_is_readable(self):
        class CustomClass(DictBase[typing.Any, typing.Any]):
            @typing.override
            def _is_key_readable(self, key: typing.Any) -> bool:
                return isinstance(key, str) and len(key) <= 1

        o = CustomClass({ 'a': 1, 'b': 2, 'c': 3 })
        assert o['a'] == 1

        o = CustomClass({ 'a': 1, 'b': 2, 'c': 3 })
        with pytest.raises(KeyError):
            o['bb']

        o = CustomClass({ 'a': 1, 'b': 2, 'c': 3 })
        with pytest.raises(KeyError):
            o['x']

        o = CustomClass({ 'a': 1, 'b': 2, 'c': 3 })
        with pytest.raises(KeyError):
            o['xx']

        o = CustomClass({ 'a': 1, 'b': 2, 'c': 3 })
        assert o.get('a') == 1

        o = CustomClass({ 'a': 1, 'b': 2, 'c': 3 })
        assert o.get('bb') is None

        o = CustomClass({ 'a': 1, 'b': 2, 'c': 3 })
        assert o.get('x') is None

        o = CustomClass({ 'a': 1, 'b': 2, 'c': 3 })
        assert o.get('xx') is None

        o = CustomClass({ 'a': 1, 'b': 2, 'c': 3 })
        assert o.pop('a') == 1

        o = CustomClass({ 'a': 1, 'b': 2, 'c': 3 })
        with pytest.raises(KeyError):
            assert o.pop('bb')

        o = CustomClass({ 'a': 1, 'b': 2, 'c': 3 })
        with pytest.raises(KeyError):
            assert o.pop('x')

        o = CustomClass({ 'a': 1, 'b': 2, 'c': 3 })
        with pytest.raises(KeyError):
            assert o.pop('xx')

        o = CustomClass({ 'a': 1, 'b': 2, 'c': 3 })
        assert o.pop('a', None) == 1

        o = CustomClass({ 'a': 1, 'b': 2, 'c': 3 })
        assert o.pop('bb', None) is None

        o = CustomClass({ 'a': 1, 'b': 2, 'c': 3 })
        assert o.pop('x', None) is None

        o = CustomClass({ 'a': 1, 'b': 2, 'c': 3 })
        assert o.pop('xx', None) is None

        o = CustomClass({ 'a': 1, 'b': 2, 'c': 3 })
        assert 'a' in o

        o = CustomClass({ 'a': 1, 'b': 2, 'c': 3 })
        assert 'bb' not in o

        o = CustomClass({ 'a': 1, 'b': 2, 'c': 3 })
        assert 'x' not in o

        o = CustomClass({ 'a': 1, 'b': 2, 'c': 3 })
        assert 'xx' not in o

    def test_is_deletable(self):
        class CustomClass(DictBase[typing.Any, typing.Any]):
            @typing.override
            def _is_key_deletable(self, key: typing.Any) -> typing.Any:
                return not isinstance(key, str) or not key.startswith('req_')

        with pytest.raises(KeyError):
            o = CustomClass()
            del o['a']

        with pytest.raises(KeyError):
            o = CustomClass()
            del o['req_a']

        o = CustomClass({ 'a': 1 })
        del o['a']  # no error
        assert o == {}

        with pytest.raises(KeyError):
            o = CustomClass({ 'req_a': 1 })
            del o['req_a']

        with pytest.raises(KeyError):
            o = CustomClass({ 'a': 1 })
            del o['req_a']

        o = CustomClass({ 'a': 1, 'b': 2, 'c': 3 })
        del o['a']  # no error
        assert o == { 'b': 2, 'c': 3 }

        with pytest.raises(KeyError):
            o = CustomClass({ 'a': 1, 'b': 2, 'c': 3 })
            del o['req_a']

        with pytest.raises(KeyError):
            o = CustomClass({ 'req_a': 1, 'req_b': 2, 'req_c': 3 })
            del o['req_a']

    def test_is_modified(self):
        o = DictBase()
        assert not o.is_modified

        o = DictBase({ 'a': 1, 'b': 2, 'c': 3 })
        assert not o.is_modified

        o = DictBase()
        o['x'] = -1
        assert o.is_modified

        o = DictBase({ 'a': 1, 'b': 2, 'c': 3 })
        o['x'] = -1
        assert o.is_modified

        o = DictBase({ 'a': 1, 'b': 2, 'c': 3 })
        o['b'] = -1
        assert o.is_modified

        o = DictBase({ 'a': 1, 'b': 2, 'c': 3 })
        # write of identical value is not same object identity
        # so it counts as a modification
        o['a'] = 1
        assert o.is_modified

        o = DictBase({ 'a': 1 })
        o |= { 'b': 2 }
        assert o.is_modified

        o = DictBase({ 'a': 1, 'b': 2, 'c': 3 })
        del o['a']
        assert o.is_modified

        o = DictBase()
        o.update({ 'x': -1, 'y': -2, 'z': -3 })
        assert o.is_modified

        o = DictBase({ 'a': 1, 'b': 2, 'c': 3 })
        o.update({ 'x': -1, 'y': -2, 'z': -3 })
        assert o.is_modified

        o = DictBase({ 'a': 1, 'b': 2, 'c': 3 })
        o.update({ 'a': -1, 'x': -2 })
        assert o.is_modified

        o = DictBase()
        o.setdefault('a', 9)
        assert o.is_modified

        o = DictBase({ 'a': 1, 'b': 2, 'c': 3 })
        o.setdefault('a', 9)
        assert not o.is_modified

        o = DictBase()
        o.clear()
        assert not o.is_modified

        o = DictBase({ 'a': 1, 'b': 2, 'c': 3 })
        o.clear()
        assert o.is_modified

        o = DictBase()
        o.pop('a', 0)
        assert not o.is_modified

        o = DictBase({ 'a': 1, 'b': 2, 'c': 3 })
        o.pop('a', 9)
        assert o.is_modified

        o = DictBase({ 'a': 1, 'b': 2, 'c': 3 })
        o.pop('x', 9)
        assert not o.is_modified

        o = DictBase({ 'a': 1, 'b': 2, 'c': 3 })
        o.popitem()
        assert o.is_modified

    def test_postulate(self):
        class CustomClass(DictBase[typing.Any, typing.Any]):
            @typing.override
            def _make_postulate(self, key: typing.Any) -> None | typing.Any:
                return True

        o = CustomClass()
        assert o['a0'] is True

        o = CustomClass()
        o['a0']  # no error
        assert o == {}

        o = CustomClass()
        o['a0']  # no error
        assert not o

    def test_chain_nested(self):
        class Chain(DictBase[typing.Any, typing.Any]):
            @typing.override
            def _make_postulate(self, key: typing.Any) -> None | typing.Any:
                return self.__class__()

        o = Chain()
        o['a0'] = 'lorem'
        assert o == { 'a0': 'lorem'}

        o = Chain()
        o['a0'] = 'lorem'
        o['a1']['b0'] = 'ipsum'
        assert o == { 'a0': 'lorem', 'a1': { 'b0': 'ipsum'} }

        o = Chain()
        o['a0'] = 'lorem'
        o['a1']['b0'] = 'ipsum'
        o['a1']['b1']['c0'] = 'dolor'
        assert o == {
            'a0': 'lorem',
            'a1': {
                'b0': 'ipsum',
                'b1': {
                    'c0': 'dolor'
                }
            }
        }

        o = Chain()
        o['a0'] = 'lorem'
        o['a1']['b0'] = 'ipsum'
        o['a1']['b1']['c0'] = 'dolor'
        o['a1']['b1']['c1']['d0'] = 'sit'
        assert o == {
            'a0': 'lorem',
            'a1': {
                'b0': 'ipsum',
                'b1': {
                    'c0': 'dolor',
                    'c1': {
                        'd0': 'sit'
                    }
                }
            }
        }

        o = Chain()
        o['a0'] = 'lorem'
        o['a1']['b0'] = 'ipsum'
        o['a1']['b1']['c0'] = 'dolor'
        o['a1']['b1']['c1']['d0'] = 'sit'
        o['a1']['b1']['c1']['d1']['e0'] = 'amet'
        assert o == {
            'a0': 'lorem',
            'a1': {
                'b0': 'ipsum',
                'b1': {
                    'c0': 'dolor',
                    'c1': {
                        'd0': 'sit',
                        'd1': {
                            'e0': "amet"
                        }
                    }
                }
            }
        }

    def test_chain_links_are_retained(self):
        class Chain(DictBase[typing.Any, typing.Any]):
            @typing.override
            def _make_postulate(self, key: typing.Any) -> None | typing.Any:
                return self.__class__()

        o = Chain()
        o['a0'] = 'lorem'
        assert o == { 'a0': "lorem"}

        o = Chain()
        o['a0']['b0'] = 'lorem'
        assert o == { 'a0': { 'b0': "lorem"} }

        o = Chain()
        o['a0']['b0']['c0'] = 'lorem'
        assert o == { 'a0': { 'b0': { 'c0': "lorem"} } }

        o = Chain()
        o['a0']['b0']['c0']['d0'] = 'lorem'
        assert o == { 'a0': { 'b0': { 'c0': { 'd0': "lorem"} } } }

        o = Chain()
        o['a0']['b0']['c0']['d0']['e0'] = 'lorem'
        assert o == { 'a0': { 'b0': { 'c0': { 'd0': { 'e0': "lorem"} } } } }

    def test_chain_is_empty_after_read(self):
        class Chain(DictBase[typing.Any, typing.Any]):
            @typing.override
            def _make_postulate(self, key: typing.Any) -> None | typing.Any:
                return self.__class__()

        o = Chain()
        o['a0']
        assert o == {}

        o = Chain()
        o['a0']['b0']
        assert o == {}

        o = Chain()
        o['a0']['b0']['c0']
        assert o == {}

        o = Chain()
        o['a0']['b0']['c0']['d0']
        assert o == {}

        o = Chain()
        o['a0']['b0']['c0']['d0']['e0']
        assert o == {}

    def test_chain_explicit_write_is_prioritized(self):
        class Chain(DictBase[typing.Any, typing.Any]):
            @typing.override
            def _make_postulate(self, key: typing.Any) -> None | typing.Any:
                return self.__class__()

        o = Chain()
        o['a0']['b0']['c0']['d0']['e0']
        o['a0'] = True
        assert o == { 'a0': True }

        o = Chain()
        o2 = o['a0']['b0']['c0']['d0']['e0']
        o['a0'] = True
        o2['f0'] = True
        assert o == { 'a0': True }

        o = Chain()
        o['a0']['b0']['c0']['d0']['e0']
        o['a0']['b0'] = True
        assert o == { 'a0': { 'b0': True } }

        o = Chain()
        o2 = o['a0']['b0']['c0']['d0']['e0']
        o['a0']['b0'] = True
        o2['f0'] = True
        assert o == { 'a0': { 'b0': True } }

    def test_chain_identities_are_persistent(self):
        class Chain(DictBase[typing.Any, typing.Any]):
            @typing.override
            def _make_postulate(self, key: typing.Any) -> None | typing.Any:
                return self.__class__()

        o = Chain()
        o2 = o['a0']
        assert o['a0'] is o2

        o = Chain()
        o2 = o['a0']['b0']
        assert o['a0']['b0'] is o2

        o = Chain()
        o2 = o['a0']['b0']['c0']
        assert o['a0']['b0']['c0'] is o2

        o = Chain()
        o2 = o['a0']['b0']['c0']['d0']
        assert o['a0']['b0']['c0']['d0'] is o2

        o = Chain()
        o2 = o['a0']['b0']['c0']['d0']['e0']
        assert o['a0']['b0']['c0']['d0']['e0'] is o2

        o = Chain()
        o2 = o['a0']
        o['a0']['b0']['c0']['d0']['e0'] = True
        assert o['a0'] is o2

        o = Chain()
        o2 = o['a0']['b0']
        o['a0']['b0']['c0']['d0']['e0'] = True
        assert o['a0']['b0'] is o2

        o = Chain()
        o2 = o['a0']['b0']['c0']
        o['a0']['b0']['c0']['d0']['e0'] = True
        assert o['a0']['b0']['c0'] is o2

        o = Chain()
        o2 = o['a0']['b0']['c0']['d0']
        o['a0']['b0']['c0']['d0']['e0'] = True
        assert o['a0']['b0']['c0']['d0'] is o2

        o = Chain()
        o2 = o['a0']
        o['a0']['b0']['c0']['d0']['e0']
        assert o['a0'] is o2

        o = Chain()
        o2 = o['a0']['b0']
        o['a0']['b0']['c0']['d0']['e0']
        assert o['a0']['b0'] is o2

        o = Chain()
        o2 = o['a0']['b0']['c0']
        o['a0']['b0']['c0']['d0']['e0']
        assert o['a0']['b0']['c0'] is o2

        o = Chain()
        o2 = o['a0']['b0']['c0']['d0']
        o['a0']['b0']['c0']['d0']['e0']
        assert o['a0']['b0']['c0']['d0'] is o2

        o = Chain()
        o2 = o['a0']['b0']['c0']['d0']['e0']
        o['a0']['b0']['c0']['d0']['e0']
        assert o['a0']['b0']['c0']['d0']['e0'] is o2
