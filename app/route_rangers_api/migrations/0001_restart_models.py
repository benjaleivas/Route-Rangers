# Generated by Django 5.0.4 on 2024-05-03 15:22

import django.contrib.gis.db.models.fields
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="BikeStation",
            fields=[
                (
                    "station_id",
                    models.CharField(max_length=30, primary_key=True, serialize=False),
                ),
                ("location", django.contrib.gis.db.models.fields.PointField(srid=4326)),
            ],
        ),
        migrations.CreateModel(
            name="Demographics",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("census_block", models.CharField(max_length=15)),
                ("state", models.CharField(max_length=15)),
                ("county", models.CharField(max_length=15)),
                ("median_income", models.IntegerField()),
                (
                    "transportation_to_work",
                    models.IntegerField(
                        verbose_name="Means of Transportation to Work Total"
                    ),
                ),
                (
                    "transportation_to_work_car",
                    models.IntegerField(
                        null=True, verbose_name="Means of Transportation to Work: Car"
                    ),
                ),
                (
                    "transportation_to_work_public",
                    models.IntegerField(
                        null=True,
                        verbose_name="Means of Transportation to Work: Public Transportation",
                    ),
                ),
                (
                    "transportation_to_work_bus",
                    models.IntegerField(
                        null=True, verbose_name="Means of Transportation to Work: Bus"
                    ),
                ),
                (
                    "transportation_to_work_subway",
                    models.IntegerField(
                        null=True,
                        verbose_name="Means of Transportation to Work: subway",
                    ),
                ),
                (
                    "work_commute_time",
                    models.FloatField(verbose_name="Time of commute to work"),
                ),
                ("vehicles_available", models.IntegerField()),
                (
                    "disability_status",
                    models.IntegerField(
                        verbose_name="Number of people with disability"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="PlannedRoute",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("user_id", models.CharField(max_length=30)),
                (
                    "response_date",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Survey response date"
                    ),
                ),
                (
                    "route",
                    django.contrib.gis.db.models.fields.LineStringField(srid=4326),
                ),
            ],
        ),
        migrations.CreateModel(
            name="RidershipRoute",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("date", models.DateField()),
                ("ridership", models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name="RidershipStation",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("date", models.DateField()),
                ("ridership", models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name="StationRouteRelation",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Survey",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=30)),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="Created at"),
                ),
                ("questionnaire", models.JSONField()),
            ],
        ),
        migrations.CreateModel(
            name="TransitRoute",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "city",
                    models.CharField(
                        choices=[
                            ("CHI", "Chicago"),
                            ("NYC", "New York"),
                            ("PDX", "Portland"),
                        ],
                        max_length=30,
                    ),
                ),
                ("route_id", models.CharField(max_length=30)),
                ("route_name", models.CharField(max_length=30)),
                ("color", models.CharField(max_length=30, null=True)),
                (
                    "geo_representation",
                    django.contrib.gis.db.models.fields.LineStringField(srid=4326),
                ),
                (
                    "mode",
                    models.IntegerField(
                        choices=[
                            (0, "Tram, Streetcar, Light rail."),
                            (1, "Subway, Metro"),
                            (2, "Rail"),
                            (3, "Bus"),
                            (4, "Ferry"),
                            (5, "Cable car"),
                            (6, " Aerial lift, suspended cable car"),
                            (7, "Funicular"),
                            (11, "Trolleybus"),
                            (12, "Monorail"),
                        ],
                        verbose_name="Mode of transportation",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="TransitStation",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "city",
                    models.CharField(
                        choices=[
                            ("CHI", "Chicago"),
                            ("NYC", "New York"),
                            ("PDX", "Portland"),
                        ],
                        max_length=30,
                    ),
                ),
                ("station_id", models.CharField(max_length=30)),
                ("station_name", models.CharField(max_length=30)),
                (
                    "location",
                    django.contrib.gis.db.models.fields.PointField(
                        null=True, srid=4326
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="BikeRidership",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("date", models.DateField()),
                ("n_started", models.IntegerField()),
                ("n_ended", models.IntegerField()),
                (
                    "station",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="route_rangers_api.bikestation",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="SurveyAnswer",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("user_id", models.CharField(max_length=30)),
                (
                    "response_date",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Survey response date"
                    ),
                ),
                ("city", models.CharField(max_length=30)),
                ("answers", models.JSONField()),
                (
                    "survey",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="route_rangers_api.survey",
                    ),
                ),
            ],
        ),
        migrations.AddConstraint(
            model_name="transitroute",
            constraint=models.UniqueConstraint(
                fields=("city", "route_id"), name="city route id"
            ),
        ),
        migrations.AddField(
            model_name="stationrouterelation",
            name="route",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                to="route_rangers_api.transitroute",
            ),
        ),
        migrations.AddField(
            model_name="ridershiproute",
            name="route",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                to="route_rangers_api.transitroute",
            ),
        ),
        migrations.AddConstraint(
            model_name="transitstation",
            constraint=models.UniqueConstraint(
                fields=("city", "station_id"), name="city station"
            ),
        ),
        migrations.AddField(
            model_name="stationrouterelation",
            name="station",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                to="route_rangers_api.transitstation",
            ),
        ),
        migrations.AddField(
            model_name="ridershipstation",
            name="station",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                to="route_rangers_api.transitstation",
            ),
        ),
    ]
