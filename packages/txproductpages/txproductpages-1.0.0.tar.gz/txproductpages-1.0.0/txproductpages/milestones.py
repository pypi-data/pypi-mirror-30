import re

"""
Schedule Milestones
"""

DEV_FREEZE = re.compile('Development Freeze', flags=re.IGNORECASE)
GA = re.compile('^GA$')
