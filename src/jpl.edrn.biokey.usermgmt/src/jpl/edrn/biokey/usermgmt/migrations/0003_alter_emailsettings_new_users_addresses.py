# Generated by Django 4.2.13 on 2024-06-18 18:09

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "jpledrnbiokeyusermgmt",
            "0002_alter_edrndirectoryinformationtree_dmcc_managed_email_template",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="emailsettings",
            name="new_users_addresses",
            field=models.CharField(
                default="ic-accounts@jpl.nasa.gov",
                help_text="Addresses (comma-separated) to notify when new users are created",
                max_length=512,
            ),
        ),
    ]
