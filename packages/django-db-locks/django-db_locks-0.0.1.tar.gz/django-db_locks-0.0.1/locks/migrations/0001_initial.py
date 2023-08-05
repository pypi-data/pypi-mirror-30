# Generated by Django 2.0 on 2018-03-15 20:23

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Lock',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=100, unique=True)),
                ('locked', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now=True)),
                ('expire', models.BooleanField()),
                ('expiration', models.DateTimeField()),
            ],
        ),
    ]
