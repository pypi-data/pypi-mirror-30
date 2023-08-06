from django.db import models

from cms.models import CMSPlugin
from cms.utils.compat.dj import python_2_unicode_compatible
from simplemde.fields import SimpleMDEField


@python_2_unicode_compatible
class CMSMarkdownPlugin(CMSPlugin):
    markdown_text = SimpleMDEField(verbose_name=u'mardown content')

    def __str__(self):
        text = self.markdown_text
        return (text[:50] + '...') if len(text) > 53 else text