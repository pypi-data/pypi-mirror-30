# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-10-24 22:31
from __future__ import unicode_literals

from django.core.exceptions import ValidationError
from django.db import migrations, models
from django.utils.text import slugify


def set_slugs(apps, schema_editor):
    BaseForm = apps.get_model("wagtailstreamforms", "BaseForm")
    db_alias = schema_editor.connection.alias

    forms = BaseForm.objects.using(db_alias).all()

    for form in forms:
        # try to slugify the title if it fails set it to something that will be unique
        form.slug = slugify(form.name, allow_unicode=True)
        try:
            form.full_clean()
        except ValidationError as e:
            form.slug = 'form-{}'.format(form.pk)

        # finally save
        form.save()


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailstreamforms', '0002_baseform_post_redirect_page'),
    ]

    operations = [
        migrations.AddField(
            model_name='baseform',
            name='slug',
            field=models.SlugField(allow_unicode=True, unique=True, blank=True, help_text='Used to identify the form in template tags', max_length=255, null=True),
        ),
        migrations.RunPython(set_slugs),
    ]
