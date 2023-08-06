# -*- coding: utf-8 -*-
from django.test import TestCase

from djcms_markdown.models import CMSMarkdownPlugin


class CMSMarkdownPluginTestCase(TestCase):

    def setUp(self):
        pass

    def test_models(self):
        markdown = CMSMarkdownPlugin.objects.create(
            markdown_text='# Test'
        )
        assert markdown.markdown_text == '# Test'
        
