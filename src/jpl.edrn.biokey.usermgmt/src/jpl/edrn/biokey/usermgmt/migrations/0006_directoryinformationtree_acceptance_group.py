# Generated by Django 4.2.13 on 2024-06-21 20:51

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "jpledrnbiokeyusermgmt",
            "0005_directoryinformationtree_approval_template_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="directoryinformationtree",
            name="acceptance_group",
            field=models.CharField(
                default="cn=All Users,ou=groups,o=organization",
                help_text="Group to which to move approved users",
                max_length=600,
            ),
        ),
    ]
