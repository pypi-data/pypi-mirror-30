# -*- coding: utf-8 -*-
from collective.behavior.richpreview import _
from zope import schema
from zope.interface import Interface


class IBrowserLayer(Interface):
    """A layer specific for this add-on product."""


class IRichPreviewSettings(Interface):
    """Schema for the control panel form."""

    enable = schema.Bool(
        title=_(u'Enable Rich Link Previews?'),
        description=_(
            u''),
        default=True,
    )
