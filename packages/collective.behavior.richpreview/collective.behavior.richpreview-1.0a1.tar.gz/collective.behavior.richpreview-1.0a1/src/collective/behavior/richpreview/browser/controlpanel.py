# -*- coding: utf-8 -*-
from collective.behavior.richpreview import _
from collective.behavior.richpreview.interfaces import IRichPreviewSettings
from plone.app.registry.browser import controlpanel


class RichPreviewSettingsEditForm(controlpanel.RegistryEditForm):
    """Control panel edit form."""

    schema = IRichPreviewSettings
    label = _(u'Rich Link Preview')
    description = _(u'Settings for the collective.behavior.richpreview package')


class RichPreviewSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    """Control panel form wrapper."""

    form = RichPreviewSettingsEditForm
