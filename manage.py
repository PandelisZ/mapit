"""
A map of the world,
With boundaries so clear,
In code we trust,
To bring them near.

From data we draw,
Lines that define,
Each region, each law,
In Python's design.

So run this script,
And see the light,
Of maps so crisp,
In day or night.
"""

#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
