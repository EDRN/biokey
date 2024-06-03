# Generated by Django 4.2.11 on 2024-06-03 22:37

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("jpledrnbiokeyusermgmt", "0011_forgottendetailsformpage"),
    ]

    operations = [
        migrations.AddField(
            model_name="emailsettings",
            name="new_users_addresses",
            field=models.CharField(
                default="edrn-ic@jpl.nasa.gov",
                help_text="Addresses (comma-separated) to notify when new users are created",
                max_length=512,
            ),
        ),
    ]