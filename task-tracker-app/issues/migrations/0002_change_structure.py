# Generated by Django 4.2.7 on 2024-06-12 03:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("issues", "0001_change_constraints"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="issuerec",
            name="o_uid",
        ),
        migrations.AddField(
            model_name="issue",
            name="o_uid",
            field=models.ForeignKey(
                default=2,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="owner_uid",
                to="issues.issueowner",
            ),
        ),
    ]
