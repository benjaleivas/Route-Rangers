# Generated by Django 5.0.4 on 2024-05-06 23:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("route_rangers_api", "0002_bikestation_n_docks_alter_bikestation_station_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="bikestation",
            name="station_name",
            field=models.CharField(max_length=50),
        ),
    ]
