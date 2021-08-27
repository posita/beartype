#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype code-based type validation classes** (i.e.,
:mod:`beartype`-specific classes enabling callers to define PEP-compliant
validators from arbitrary caller-defined classes tested via explicitly
supported object introspectors efficiently generating stack-free code).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                              }....................
# All "FIXME:" comments for this submodule reside in this package's "__init__"
# submodule to improve maintainability and readability here.

# ....................{ IMPORTS                           }....................
from beartype.roar import BeartypeValeSubscriptionException
from beartype.vale._valeisabc import _IsABC
from beartype._vale._valesnip import VALE_CODE_CHECK_ISSUBCLASS_format
from beartype._vale._valesub import _SubscriptedIs
from beartype._util.cache.utilcachecall import callable_cached
from beartype._util.cls.utilclstest import (
    TestableTypes,
    is_type_subclass,
)
from beartype._util.cls.pep.utilpep3119 import die_unless_type_issubclassable
from beartype._util.func.utilfuncscope import (
    CallableScope,
    add_func_scope_attr,
)
from beartype._util.utilobject import get_object_name

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ CLASSES ~ type                    }....................
class IsSubclass(_IsABC):
    '''
    **Beartype type inheritance validator factory** (i.e., object creating and
    returning a new beartype validator when subscripted (indexed) by any class,
    validating that :mod:`beartype`-decorated callable parameters and returns
    annotated by :attr:`typing.Annotated` type hints subscripted by that
    validator subclass that class).

    This class efficiently validates that callable parameters and returns are
    subclasses of the arbitrary class subscripting (indexing) this factory. Any
    :mod:`beartype`-decorated callable parameter or return annotated by a
    :attr:`typing.Annotated` type hint subscripted by this factory subscripted
    by any class (e.g., ``typing.Annotated[type,
    beartype.vale.IsSubclass[{cls}]]`` for any class ``{cls}``) validates that
    parameter or return value to be a subclass of that class.

    This factory is a generalization of the :pep:`484`-compliant
    :attr:`typing.Type` and :pep:`585`-compliant :class:`type` type hint
    factories, because this factory does everything those factories do and
    substantially more. Superficially, :attr:`typing.Type` and :class:`type`
    type hints also validate that callable parameters and returns are
    subclasses of the classes subscripting those hints. The similarity ends
    there, however. Those hints only narrowly apply to callable parameters and
    returns; meanwhile, this factory produces beartype validators universally
    applying to both:

    * Callable parameters and returns.
    * **Attributes** of callable parameters and returns via the
      :class:`beartype.vale.IsAttr` factory.

    **This factory incurs no time performance penalties at call time.** Whereas
    the general-purpose :class:`beartype.vale.Is` factory necessarily calls
    the caller-defined callable subscripting that factory at call time and thus
    incurs a minor time performance penalty, this factory efficiently reduces
    to one-line tests in :mod:`beartype`-generated wrapper functions *without*
    calling any callables and thus incurs *no* time performance penalties.

    Examples
    ----------
    .. code-block:: python

       # Import the requisite machinery.
       >>> from beartype import beartype
       >>> from beartype.vale import IsAttr, IsSubclass
       >>> from typing import Annotated
       >>> import numpy as np

       # Type hint matching only NumPy arrays of floats of arbitrary precision,
       # generating code resembling:
       #    (isinstance(array, np.ndarray) and
       #     np.issubdtype(array.dtype, np.floating))
       >>> NumpyFloatArray = Annotated[
       ...     np.ndarray, IsAttr['dtype', IsAttr['type', IsSubclass[np.floating]]]]

       # Type hint matching only NumPy arrays of integers of arbitrary
       # precision, generating code resembling:
       #    (isinstance(array, np.ndarray) and
       #     np.issubdtype(array.dtype, np.integer))
       >>> NumpyIntArray = Annotated[
       ...     np.ndarray, IsAttr['dtype', IsAttr['type', IsSubclass[np.integer]]]]

       # NumPy arrays of well-known real number series.
       >>> E_APPROXIMATIONS = np.array(
       ...     [1+1, 1+1+1/2, 1+1+1/2+1/6, 1+1+1/2+1/6+1/24,])
       >>> FACTORIALS = np.array([1, 2, 6, 24, 120, 720, 5040, 40320, 362880,])

       # Annotate callables by those type hints.
       >>> @beartype
       ... def round_int(array: NumpyFloatArray) -> NumpyIntArray:
       ...     """
       ...     NumPy array of integers rounded from the passed NumPy array of
       ...     floating-point numbers to the nearest 64-bit integer.
       ...     """
       ...     return np.around(array).astype(np.int64)

       # Call those callables with parameters satisfying those hints.
       >>> round_int(E_APPROXIMATIONS)
       [2, 3, 3, 3]

       # Call those callables with parameters violating those hints.
       >>> round_int(FACTORIALS)
       beartype.roar.BeartypeCallHintPepParamException: @beartyped round_int()
       parameter array="array([ 1, 2, 6, 24, 120, 720, 5040, 40320, ...])"
       violates type hint typing.Annotated[numpy.ndarray, IsAttr['dtype',
       IsAttr['type', IsSubclass[numpy.floating]]]], as "array([ 1, 2, 6, 24,
       120, 720, 5040, 40320, ...])" violates validator IsAttr['dtype',
       IsAttr['type', IsSubclass[numpy.floating]]]

    See Also
    ----------
    :class:`beartype.vale.Is`
        Further commentary.
    '''

    # ..................{ DUNDERS                           }..................
    @callable_cached
    def __class_getitem__(
        cls, base_classes: TestableTypes) -> _SubscriptedIs:
        '''
        :pep:`560`-compliant dunder method creating and returning a new
        beartype validator validating type inheritance against at least one of
        the passed classes, suitable for subscripting :pep:`593`-compliant
        :attr:`typing.Annotated` type hints.

        This method is memoized for efficiency.

        Parameters
        ----------
        base_classes : TestableTypes
            One or more arbitrary classes to validate inheritance against.

        Returns
        ----------
        _SubscriptedIs
            Beartype validator encapsulating this validation.

        Raises
        ----------
        BeartypeValeSubscriptionException
            If this factory was subscripted by either:

            * *No* arguments.
            * Two or more arguments.

        See Also
        ----------
        :class:`IsAttr`
            Usage instructions.
        '''

        # Machine-readable string representing this type or tuple of types.
        base_classes_repr = ''

        # If this factory was subscripted by either no arguments *OR* two or
        # more arguments...
        if isinstance(base_classes, tuple):
            # If this factory was subscripted by *NO* arguments, raise an
            # exception.
            if not base_classes:
                raise BeartypeValeSubscriptionException(
                    f'{repr(cls)} subscripted by empty tuple.')
            # Else, this factory was subscripted by two or more arguments.

            # If any such argument is *NOT* an issubclassable type, raise an
            # exception.
            for base_class in base_classes:
                die_unless_type_issubclassable(
                    cls=base_class,
                    exception_cls=BeartypeValeSubscriptionException,
                )

                # Append the fully-qualified name of this type to this string.
                base_classes_repr += f'{get_object_name(base_class)}, '
            # Else, all such arguments are issubclassable types.

            # Strip the suffixing ", " from this string for readability.
            base_classes_repr = base_classes_repr[:-2]
        # Else, this factory was subscripted by one argument. In this case...
        else:
            # If this argument is *NOT* an issubclassable type, raise an
            # exception.
            die_unless_type_issubclassable(
                cls=base_classes,
                exception_cls=BeartypeValeSubscriptionException,
            )
            # Else, this argument is an issubclassable type.

            # Fully-qualified name of this type.
            base_classes_repr = get_object_name(base_classes)

        # Callable inefficiently validating against this type.
        is_valid = lambda pith: is_type_subclass(pith, base_classes)

        # Dictionary mapping from the name to value of each local attribute
        # referenced in the "is_valid_code" snippet defined below.
        is_valid_code_locals: CallableScope = {}

        # Name of a new parameter added to the signature of wrapper functions
        # whose value is this type or tuple of types, enabling this type or
        # tuple of types to be tested in those functions *WITHOUT* additional
        # stack frames.
        param_name_base_cls = add_func_scope_attr(
            attr=base_classes, attr_scope=is_valid_code_locals)

        # Code snippet efficiently validating against this type.
        is_valid_code = VALE_CODE_CHECK_ISSUBCLASS_format(
            param_name_base_cls=param_name_base_cls)

        # Create and return this subscription.
        return _SubscriptedIs(
            is_valid=is_valid,
            is_valid_code=is_valid_code,
            is_valid_code_locals=is_valid_code_locals,

            # Intentionally pass this subscription's machine-readable
            # representation as a string rather than lambda function returning
            # a string, as this string is safely, immediately, and efficiently
            # constructable from these arguments' representation.
            get_repr=f'{cls.__name__}[{base_classes_repr}]',
        )
