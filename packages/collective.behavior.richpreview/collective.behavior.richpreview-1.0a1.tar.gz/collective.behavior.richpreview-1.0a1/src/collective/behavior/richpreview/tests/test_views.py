# -*- coding: utf-8 -*-
from collective.behavior.richpreview.testing import INTEGRATION_TESTING
from plone import api

import json
import unittest


class RichPreviewJsonViewTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.view = api.content.get_view(
            u'richpreview-json-view', self.portal, self.request)

    def test_view_no_url(self):
        self.view.setup()
        response = self.view()
        self.assertEqual(response, '')
        self.assertEqual(self.request.RESPONSE.getStatus(), 400)

    def test_view(self):
        self.request.form['url'] = 'http://www.plone.org'
        self.view.setup()
        expected = {
            'image': 'https://plone.org/logo.png',
            'description': '',
            'title': 'Plone CMS: Open Source Content Management',
        }

        response = self.view()
        content_type = response.getHeader('Content-Type')
        body = response.getBody()
        self.assertEqual(content_type, 'application/json')
        self.assertEqual(body, json.dumps(expected))
