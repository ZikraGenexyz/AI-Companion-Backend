# Generated by Django 5.1.6 on 2025-03-06 02:54

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Personnel_Entries',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('timestamp', models.CharField(max_length=200)),
            ],
        ),
    ]
