# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import simplemde.fields


class Migration(migrations.Migration):

    dependencies = [
        ('djcms_markdown', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cmsmarkdownplugin',
            name='markdown_text',
            field=simplemde.fields.SimpleMDEField(verbose_name='mardown content'),
        ),
    ]
