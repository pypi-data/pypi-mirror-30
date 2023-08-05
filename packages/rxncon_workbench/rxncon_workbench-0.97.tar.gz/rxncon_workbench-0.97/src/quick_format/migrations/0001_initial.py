# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-06-22 13:31
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('boolean_model', '0001_initial'),
        ('rule_based', '0001_initial'),
        ('rxncon_system', '0001_initial'),
        ('graphs', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Quick',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120)),
                ('slug', models.SlugField(blank=True)),
                ('loaded', models.BooleanField(default=False)),
                ('quick_input', models.TextField()),
                ('comment', models.TextField(blank=True, null=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('boolean_model', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='bool_quick', to='boolean_model.Bool_from_rxnconsys')),
                ('rea_graph', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reaction_graph_quick', to='graphs.Graph_from_File')),
                ('reg_graph', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='regulatory_graph_quick', to='graphs.Graph_from_File')),
                ('rule_based_model', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='rule_based_quick', to='rule_based.Rule_based_from_rxnconsys')),
                ('rxncon_system', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='rxncon_system_quick', to='rxncon_system.Rxncon_system')),
                ('sRea_graph', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='species reaction_graph_quick+', to='graphs.Graph_from_File')),
            ],
        ),
    ]
