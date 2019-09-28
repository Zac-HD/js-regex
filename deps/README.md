# Pinning dependencies

We pin *all* our dependencies for testing, and disable installation
of any unlisted dependencies to make sure the set of pins is complete.

How does this work?

1. `setup.py` lists all our top-level dependencies for the library,
   and the `*.in` files list the development and test-time dependencies.
2. `pip-compile` calculates all the transitive dependencies we need,
   with exact version pins (run with `tox -e deps` for convenience).
3. `tox` then installs from the files full of pinned versions here!

That's it - a simple implementation but it stabilises the whole dependency
chain and really improves visibility :-)
