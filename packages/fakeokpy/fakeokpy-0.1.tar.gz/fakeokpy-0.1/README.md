# fakeok client

A package that provides a fake interface similar to
[okpy](https://pypi.python.org/pypi/okpy) but fake

## Why?

okpy's notebook integration writes to stdout for each `grade`
call. This makes it hard to autograde it, since you get a
lot of spurious issues when you are autograding. This is
particularly bad when you want to autograde without requiring
the full complexity of okpy.

## What?

You can install this package (`fakeokpy`) instead of `okpy`.
All imports will work, and so will function calls. They'll
just do nothing, and hopefully not cause exceptions.
