# Generated by Django 4.1.5 on 2023-01-15 19:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_user_is_staff_alter_user_is_superuser'),
    ]

    operations = [
        migrations.AddField(
            model_name='userframe',
            name='active',
            field=models.BooleanField(default=False),
        ),
    ]