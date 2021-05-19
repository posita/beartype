#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype decorator general-purpose code snippets.**

This private submodule *only* defines **code snippets** (i.e., triple-quoted
pure-Python code constants formatted and concatenated together into wrapper
functions implementing type-checking for decorated callables).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype._util.text.utiltextmagic import CODE_INDENT_1

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ CODE                              }....................
CODE_SIGNATURE = f'''def {{func_wrapper_name}}(
    *args,{{func_wrapper_params}}{CODE_INDENT_1}**kwargs
):'''
'''
PEP-agnostic code snippet declaring the signature of the wrapper function
type-checking the decorated callable.
'''

# ....................{ CODE ~ arg                        }....................
# To avoid colliding with the names of arbitrary caller-defined parameters, the
# beartype-specific parameter names *MUST* be prefixed by "__beartype_".

ARG_NAME_FUNC = '__beartype_func'
'''
Name of the **private decorated callable parameter** (i.e.,
:mod:`beartype`-specific parameter whose default value is the decorated
callable passed to all wrapper functions generated by the
:func:`beartype.beartype` decorator).
'''


ARG_NAME_GETRANDBITS = '__beartype_getrandbits'
'''
Name of the **private getrandbits parameter** (i.e., :mod:`beartype`-specific
parameter whose default value is the highly performant C-based
:func:`random.getrandbits` function conditionally passed to every wrapper
functions generated by the :func:`beartype.beartype` decorator internally
requiring one or more random integers).
'''


ARG_NAME_RAISE_EXCEPTION = '__beartype_raise_exception'
'''
Name of the **private exception raising parameter** (i.e.,
:mod:`beartype`-specific parameter whose default value is the
:func:`beartype._decor._error.errormain.raise_pep_call_exception`
function raising human-readable exceptions on call-time type-checking failures
passed to all wrapper functions generated by the :func:`beartype.beartype`
decorator).
'''


ARG_NAME_TYPISTRY = '__beartypistry'
'''
Name of the **private beartypistry parameter** (i.e., :mod:`beartype`-specific
parameter whose default value is the beartypistry singleton conditionally
passed to every wrapper function generated by the :func:`beartype.beartype`
decorator requiring one or more types or tuples of types cached by this
singleton).
'''

# ....................{ CODE ~ var                        }....................
VAR_NAME_ARGS_LEN = '__beartype_args_len'
'''
Name of the local variable providing the **positional argument count** (i.e.,
number of positional arguments passed to the current call).
'''


VAR_NAME_RANDOM_INT = '__beartype_random_int'
'''
Name of the local variable providing a **pseudo-random integer** (i.e.,
unsigned 32-bit integer pseudo-randomly generated for subsequent use in
type-checking randomly indexed container items by the current call).
'''

# ....................{ CODE ~ init                       }....................
CODE_INIT_ARGS_LEN = f'''
    # Localize the number of passed positional arguments for efficiency.
    {VAR_NAME_ARGS_LEN} = len(args)'''
'''
PEP-agnostic code snippet localizing the number of passed positional arguments
for callables accepting one or more such arguments.
'''


#FIXME: Note that NumPy provides an efficient means of generating a large
#number of pseudo-random integers all-at-once. The core issue there, of
#course, is that we then need to optionally depend upon and detect NumPy,
#which then requires us to split our random integer generation logic into two
#parallel code paths that we'll then have to maintain -- and the two will be
#rather different. In any case, here's how one generates a NumPy array
#containing 100 pseudo-random integers in the range [0, 127]:
#    random_ints = numpy.random.randint(128, size=100)
#To leverage that sanely, we'd need to:
#* Globally cache that array somewhere.
#* Globally cache the current index into that array.
#* When NumPy is unimportable, fallback to generating a Python list containing
#  the same number of pseudo-random integers in the same range.
#* In either case, we'd probably want to wrap that logic in a globally
#  accessible infinite generator singleton that returns another pseudo-random
#  integer every time you iterate it. This assumes, of course, that iterating
#  generators is reasonably fast in Python. (If not, just make that a getter
#  method of a standard singleton object.)
#* Replace the code snippet below with something resembling:
#      '''
#      __beartype_random_int = next(__beartype_random_int_generator)
#      '''
#Note that thread concurrency issues are probable ignorable here, but that
#there's still a great deal of maintenance and refactoring that would need to
#happen to sanely support this. In other words, ain't happenin' anytime soon.

CODE_INIT_RANDOM_INT = f'''
    # Generate and localize a sufficiently large pseudo-random integer for
    # subsequent indexation in type-checking randomly selected container items.
    {VAR_NAME_RANDOM_INT} = {ARG_NAME_GETRANDBITS}(32)'''
'''
PEP-specific code snippet generating and localizing a pseudo-random unsigned
32-bit integer for subsequent use in type-checking randomly indexed container
items.

This bit length was intentionally chosen to correspond to the number of bits
generated by each call to Python's C-based Mersenne Twister underlying the
:func:`random.getrandbits` function called here. Exceeding this number of bits
would cause that function to inefficiently call the Twister multiple times.

This bit length produces unsigned 32-bit integers efficiently representable as
C-based atomic integers rather than **big numbers** (i.e., aggregations of
C-based atomic integers) ranging 0–``2**32 - 1`` regardless of the word size of
the active Python interpreter.

Since the cost of generating integers to this maximum bit length is
approximately the same as generating integers of much smaller bit lengths, this
maximum is preferred. Although big numbers transparently support the same
operations as non-big integers, the latter are dramatically more efficient with
respect to both space and time consumption and thus preferred.

Usage
-----
Since *most* containers are likely to contain substantially fewer items than
the maximum integer in this range, pseudo-random container indices are
efficiently selectable by simply taking the modulo of this local variable with
the lengths of those containers.

Any container containing more than this maximum number of items is typically
defined as a disk-backed data structure (e.g., Pandas dataframe) rather than an
in-memory standard object (e.g., :class:`list`). Since :mod:`beartype`
currently ignores the former with respect to deep type-checking, this local
typically suffices for real-world in-memory containers. For edge-case
containers containing more than this maximum number of items, :mod:`beartype`
will only deeply type-check items with indices in this range; all trailing
items will *not* be deeply type-checked, which we consider an acceptable
tradeoff, given the infeasibility of even storing such objects in memory.

Caveats
-------
**The only safely callable function declared by the stdlib** :mod:`random`
**module is** :func:`random.getrandbits`. While that function is efficiently
implemented in C, all other functions declared by that module are inefficiently
implemented in Python. In fact, their implementations are sufficiently
inefficient that there exist numerous online articles lamenting the fact.

See Also
--------
https://stackoverflow.com/a/11704178/2809027
    StackOverflow answer demonstrating Python's C-based Mersenne Twister
    underlying the :func:`random.getrandbits` function to generate 32 bits of
    pseudo-randomness at a time.
https://gist.github.com/terrdavis/1b23b7ff8023f55f627199b09cfa6b24#gistcomment-3237209
    Self GitHub comment introducing the core concepts embodied by this snippet.
https://eli.thegreenplace.net/2018/slow-and-fast-methods-for-generating-random-integers-in-python
    Authoritative article profiling various :mod:`random` callables.
'''

# ....................{ CODE ~ return                     }....................
CODE_RETURN_UNCHECKED = f'''
    # Call this function with all passed parameters and return the value
    # returned from this call.
    return {ARG_NAME_FUNC}(*args, **kwargs)'''
'''
PEP-agnostic code snippet calling the decorated callable *without*
type-checking the value returned by that call (if any).
'''
