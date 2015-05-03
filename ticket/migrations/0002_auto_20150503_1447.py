# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ticket', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tickets',
            name='types',
            field=models.CharField(verbose_name='Types', choices=[('INCIDENT', 'Incident'), ('ASK', 'Demande')], max_length=15),
        ),
    ]