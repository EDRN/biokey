# Generated by Django 4.2.11 on 2024-05-29 16:20

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("jpledrnbiokeyusermgmt", "0004_directoryinformationtree_user_base"),
    ]

    operations = [
        migrations.AddField(
            model_name="directoryinformationtree",
            name="user_scope",
            field=models.CharField(
                choices=[(0, "base"), (1, "one-level"), (2, "subtree")],
                default=1,
                help_text="Search scope for users",
                max_length=3,
            ),
        ),
    ]