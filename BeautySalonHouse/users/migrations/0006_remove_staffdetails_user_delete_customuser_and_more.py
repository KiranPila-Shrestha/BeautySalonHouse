# Generated by Django 5.0.1 on 2024-02-23 04:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_customuser_staffdetails'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='staffdetails',
            name='user',
        ),
        migrations.DeleteModel(
            name='CustomUser',
        ),
        migrations.DeleteModel(
            name='StaffDetails',
        ),
    ]
