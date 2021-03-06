# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import social.apps.django_app.default.fields
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('replays', '0035_auto_20160326_1121'),
    ]

    operations = [
        migrations.CreateModel(
            name='BoostData',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('frame', models.PositiveIntegerField()),
                ('value', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(255)])),
            ],
            options={
                'ordering': ['player', 'frame'],
            },
        ),
        migrations.AddField(
            model_name='player',
            name='boost_data',
            field=social.apps.django_app.default.fields.JSONField(blank=True, null=True, default='{}'),
        ),
        migrations.AddField(
            model_name='boostdata',
            name='player',
            field=models.ForeignKey(to='replays.Player'),
        ),
        migrations.AddField(
            model_name='boostdata',
            name='replay',
            field=models.ForeignKey(to='replays.Replay'),
        ),
    ]
