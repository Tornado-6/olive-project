# Generated by Django 5.1.3 on 2024-11-24 11:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0002_review"),
    ]

    operations = [
        migrations.AddField(
            model_name="category",
            name="parent",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="children",
                to="products.category",
            ),
        ),
        migrations.AlterField(
            model_name="category",
            name="slug",
            field=models.SlugField(max_length=200, unique=True),
        ),
    ]