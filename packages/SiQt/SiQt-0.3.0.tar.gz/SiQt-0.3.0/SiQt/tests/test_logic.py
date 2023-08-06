
from SiQt.dep_resolv import check_depflags


def test_check_depflags():
    dep_flags = {'a': True, 'b': False, 'c': True, 'd': False}
    assert check_depflags(dep_flags, ['a', 'c'])
    assert not check_depflags(dep_flags, ['a', 'd'])
    assert not check_depflags(dep_flags, ['a', 'b', 'd'])
    assert check_depflags(dep_flags, 'a')
    assert check_depflags(dep_flags, 'a and c')
    assert not check_depflags(dep_flags, 'a and d')
    assert not check_depflags(dep_flags, 'a and c and d')
    assert check_depflags(dep_flags, 'a or d')
    assert check_depflags(dep_flags, 'c and (a or d)')
    assert check_depflags(dep_flags, 'c and not d')
    assert check_depflags(dep_flags, '(c or d) and (not d or b)')
