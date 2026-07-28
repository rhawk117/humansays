"""humansays.

Nothing is imported from ``humansays.*`` here: an ancestor importing a
descendant would execute on every ``import humansays.anything``.
"""

import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())
