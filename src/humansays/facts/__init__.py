"""Pure fact types.

What extraction produces and evaluation consumes. Nothing here imports
``ast``: these are the values that cross the boundary between the two, so
they carry only ``str``, ``int``, ``bool``, ``tuple`` and ``frozenset``.
"""
