###############################################################################
#
# Copyright (c) 2017 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""Interfaces

$Id: interfaces.py 4669 2017-12-21 01:22:32Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import j01.form.interfaces

# editor text
class IEditorWidget(j01.form.interfaces.ITextAreaWidget):
    """Editor widget"""
