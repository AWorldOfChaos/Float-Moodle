# Generated by Django 3.2.7 on 2021-10-08 15:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_alter_assignment_problem_statement'),
    ]

    operations = [
        migrations.AddField(
            model_name='assignment',
            name='name',
            field=models.CharField(default='No name', max_length=50, unique=True),
        ),
    ]