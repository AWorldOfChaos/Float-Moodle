# Generated by Django 3.2.7 on 2021-10-18 08:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20211018_1352'),
    ]

    operations = [
        migrations.AlterField(
            model_name='evaluation',
            name='assignment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.assignment'),
        ),
    ]