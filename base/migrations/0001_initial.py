# Generated by Django 3.2.9 on 2021-11-07 01:32

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Problem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contest_id', models.IntegerField(default=1)),
                ('name', models.CharField(max_length=200)),
                ('rating', models.IntegerField(default=1500)),
                ('index', models.CharField(max_length=4)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('handle', models.CharField(max_length=40)),
                ('registration_date', models.DateField(auto_now_add=True)),
                ('rating_progress', models.CharField(max_length=200)),
                ('virtual_rating', models.IntegerField(default=1400)),
                ('in_progress', models.BooleanField(default=False)),
                ('current_problem', models.CharField(default='Unselected', max_length=20)),
                ('deadline', models.DateTimeField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
