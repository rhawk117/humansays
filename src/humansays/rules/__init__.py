"""Rule definitions, grouped by the design concern a rule speaks to.

Each subpackage owns one group: a ``rules.toml`` carrying the group's rule
metadata, and the detection code that emits those rules. Definitions are
package data, not a user extension point -- users tune thresholds through
``humansays.toml`` and never author rule files.
"""
