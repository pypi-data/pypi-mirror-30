# -*- coding: utf-8 -*-
from plone.dexterity.interfaces import IDexterityFTI
from zope.component import queryUtility


def enable_rich_preview_behavior(portal_type):
    """Enable the behavior on the specified portal type."""
    fti = queryUtility(IDexterityFTI, name=portal_type)
    behavior = 'collective.behavior.richpreview.behaviors.IRichPreview'
    if behavior in fti.behaviors:
        return
    fti.behaviors += ('collective.behavior.richpreview.behaviors.IRichPreview',)
