# Generated by Django 2.1.7 on 2019-04-17 07:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0004_profile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='birthdate',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='facebook',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='line_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
