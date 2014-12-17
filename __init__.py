"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
 - **Module inasafe.**

This script initializes the plugin, making it known to QGIS.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'tim@linfiniti.com'
__date__ = '10/01/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import os
import sys
THIRD_PARTY_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'safe_extras', 'parameters'))
if THIRD_PARTY_DIR not in sys.path:
    sys.path.append(THIRD_PARTY_DIR)


# noinspection PyDocstring
def classFactory(iface):
    """Load Plugin class from file Plugin."""
    from safe.plugin import Plugin
    return Plugin(iface)
