#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype error-handling string munging unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._decor._error._errortext` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                             }....................
def test_represent_pith() -> None:
    '''
    Test the
    :func:`beartype._decor._error._errortext.represent_pith` function.
    '''

    # Defer heavyweight imports.
    from beartype._decor._error._errortext import represent_pith

    # Custom type to be represented below.
    class CustomType(object):
        def __repr__(self) -> str: return (
            'Collaborator‐ily brambling unspiritually')

    # Assert this representer represents builtin types in the expected way.
    repr_builtin = represent_pith(42)
    assert 'int' in repr_builtin
    assert '42' in repr_builtin

    # Assert this representer represents custom types in the expected way.
    repr_nonbuiltin = represent_pith(CustomType())
    assert 'CustomType' in repr_nonbuiltin
    assert 'Collaborator‐ily brambling unspiritually' in repr_nonbuiltin
