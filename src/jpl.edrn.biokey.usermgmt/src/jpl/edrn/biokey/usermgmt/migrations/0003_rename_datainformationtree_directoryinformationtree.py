# Generated by Django 4.2.11 on 2024-05-05 21:57

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("wagtailcore", "0089_log_entry_data_json_null_to_object"),
        ("jpledrnbiokeyusermgmt", "0002_datainformationtree_manager_dn_and_more"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="DataInformationTree",
            new_name="DirectoryInformationTree",
        ),
    ]
