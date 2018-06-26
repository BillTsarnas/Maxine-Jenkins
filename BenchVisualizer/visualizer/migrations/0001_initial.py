# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-06-26 18:55
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Dacapo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('build_no', models.IntegerField(default=0)),
                ('revision', models.CharField(default='0', max_length=50)),
                ('details', models.CharField(default='default', max_length=50)),
                ('avrora', models.CharField(default='0', max_length=50)),
                ('batik', models.CharField(default='0', max_length=50)),
                ('eclipse', models.CharField(default='0', max_length=50)),
                ('fop', models.CharField(default='0', max_length=50)),
                ('h2', models.CharField(default='0', max_length=50)),
                ('jython', models.CharField(default='0', max_length=50)),
                ('luindex', models.CharField(default='0', max_length=50)),
                ('lusearch', models.CharField(default='0', max_length=50)),
                ('pmd', models.CharField(default='0', max_length=50)),
                ('sunflow', models.CharField(default='0', max_length=50)),
                ('tomcat', models.CharField(default='0', max_length=50)),
                ('tradebeans', models.CharField(default='0', max_length=50)),
                ('tradesoap', models.CharField(default='0', max_length=50)),
                ('xalan', models.CharField(default='0', max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='n/a', max_length=50)),
                ('description', models.CharField(default='n/a', max_length=50)),
                ('is_running', models.CharField(default='n/a', max_length=5)),
                ('is_enabled', models.CharField(default='n/a', max_length=5)),
            ],
        ),
        migrations.CreateModel(
            name='Specjvm',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('build_no', models.IntegerField(default=0)),
                ('revision', models.CharField(default='0', max_length=50)),
                ('details', models.CharField(default='default', max_length=50)),
                ('startup', models.CharField(default='0', max_length=50)),
                ('compiler', models.CharField(default='0', max_length=50)),
                ('compress', models.CharField(default='0', max_length=50)),
                ('crypto', models.CharField(default='0', max_length=50)),
                ('derby', models.CharField(default='0', max_length=50)),
                ('mpegaudio', models.CharField(default='0', max_length=50)),
                ('scimark', models.CharField(default='0', max_length=50)),
                ('serial', models.CharField(default='0', max_length=50)),
                ('sunflow', models.CharField(default='0', max_length=50)),
                ('xml', models.CharField(default='0', max_length=50)),
                ('job', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='visualizer.Job')),
            ],
        ),
        migrations.AddField(
            model_name='dacapo',
            name='job',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='visualizer.Job'),
        ),
    ]
