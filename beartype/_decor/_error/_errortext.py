#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype error-handling string munging utilities** (i.e., functions returning
substrings intended to be embedded in strings explaining type hint violations).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype._util.text.utiltextlabel import label_type
from beartype._util.text.utiltextrepr import represent_object

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ REPRESENTERS                      }....................
def represent_pith(pith: object) -> str:
    '''
    Human-readable description of the passed **pith** (i.e., arbitrary object
    violating the current type check) intended to be embedded in an exception
    message explaining this violation.

    Parameters
    ----------
    pith : object
        Arbitrary object violating the current type check.

    Returns
    ----------
    str
        Human-readable description of this object.
    '''

    # 
    return f'{label_type(type(pith))} {represent_object(pith)}'
