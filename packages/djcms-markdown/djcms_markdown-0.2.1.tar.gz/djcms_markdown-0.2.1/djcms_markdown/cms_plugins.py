"""Implementation of CMSPluginBase class for ``djcms_markdown``."""
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.utils.translation import ugettext_lazy as _

from djcms_markdown.models import CMSMarkdownPlugin


class DJMarkdownCMSPlugin(CMSPluginBase):
    model = CMSMarkdownPlugin
    name = _('DJCMSMarkdown')
    render_template = 'djcms_markdown/markdown.html'
    change_form_template = 'djcms_markdown/change_form.html'

    def render(self, context, instance, placeholder):
        context['text'] = instance.markdown_text
        return context


plugin_pool.register_plugin(DJMarkdownCMSPlugin)