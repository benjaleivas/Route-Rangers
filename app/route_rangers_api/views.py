from django.db.models import F
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.http import Http404, JsonResponse
from django.urls import reverse
from django.core.serializers import serialize
from django.templatetags.static import static
from django.contrib.gis.geos import GEOSGeometry, MultiLineString, LineString, Point
from django.views.decorators.cache import cache_page
import uuid
import json

from app.route_rangers_api.utils.metric_processing import (
    dashboard_metrics,
    get_daily_ridership,
    extract_top_ten,
)
from app.route_rangers_api.utils.city_mapping import (
    CITY_CONTEXT,
    CITIES_CHOICES_SURVEY,
    MODES_OF_TRANSIT,
    CITY_RIDERSHIP_LEVEL,
)
from app.route_rangers_api.utils.survey_results_processing import (
    get_number_of_responses,
    get_transit_use_pct,
    get_rider_satisfaction,
    get_transit_mode,
    get_trip_top,
    get_transit_improv_drivers_dict,
    get_transit_improv_riders_dict,
)
from route_rangers_api.models import (
    TransitRoute,
    TransitStation,
    SurveyResponse,
    SurveyUser,
)
from route_rangers_api.forms import (
    RiderSurvey1,
    RiderSurvey2,
    RiderSurvey3,
    RiderSurvey4,
    RiderSurvey5,
)

from django.contrib.gis.geos import GEOSGeometry, MultiLineString, LineString


def test(request):
    return HttpResponse("""This is a test route without any html/JS/static stuff""")


def home(request):
    context = {"cities_class": "cs-li-link cs-active", "about_class": "cs-li-link"}
    return render(request, "cities.html", context)


def about(request):
    context = {"cities_class": "cs-li-link", "about_class": "cs-li-link cs-active"}
    return render(request, "about.html", context)


def about_internal(request, city: str):
    context = {
        "City": CITY_CONTEXT[city]["CityName"],
        "City_NoSpace": city,
        "about_class": "cs-li-link cs-active",
        "cities_class": "cs-li-link",
        "policy_class": "cs-li-link",
        "survey_class": "cs-li-link",
        "feedback_class": "cs-li-link",
    }
    return render(request, "about_internal.html", context)


# caching for 6 hours since the data doesn't change often
@cache_page(60 * 60 * 6)
def dashboard(request, city: str):
    # Get existing routes and stations
    routes = TransitRoute.objects.filter(city=CITY_CONTEXT[city]["DB_Name"])
    # reduce load time and data transfer size by overwriting model attribute
    TOLERANCE = 0.00005
    for route in routes:
        simple_geo_representation = route.geo_representation.simplify(
            tolerance=TOLERANCE, preserve_topology=True
        )
        # simplify() might alter the GEOS type; can't allow that
        if isinstance(simple_geo_representation, LineString):
            simple_geo_representation = MultiLineString(simple_geo_representation)
        route.geo_representation = simple_geo_representation

    routes_json = serialize(
        "geojson",
        routes,
        geometry_field="geo_representation",
        fields=("route_name", "color", "mode"),
    )

    # Get Stations:
    stations = TransitStation.objects.filter(city=CITY_CONTEXT[city]["DB_Name"])
    stations_json = serialize(
        "geojson", stations, geometry_field="location", fields=("station_name", "mode")
    )

    # Get user-drawn routes and endpoints
    user_routes = SurveyResponse.objects.filter(
        city=CITY_CONTEXT[city]["DB_Name"],
        route__isnull=False,
        starting_point__isnull=False,
        end_point__isnull=False,
    )
    # reduce load time and data transfer size by overwriting model attribute
    user_features = []
    for user_drawn in user_routes:
        simple_route = user_drawn.route.simplify(
            tolerance=TOLERANCE, preserve_topology=True
        )
        user_drawn.route = simple_route
        user_features.append(
            {
                "type": "Feature",
                "geometry": {
                    "type": "GeometryCollection",
                    "geometries": [
                        {
                            "type": "LineString",
                            "coordinates": [
                                # TODO: figure out why these are reversed y,x
                                # instead of x,y
                                [coord[1], coord[0]]
                                for coord in user_drawn.route.coords
                            ],
                        },
                        {
                            "type": "Point",
                            "coordinates": [
                                user_drawn.starting_point.x,
                                user_drawn.starting_point.y,
                            ],
                        },
                        {
                            "type": "Point",
                            "coordinates": [
                                user_drawn.end_point.x,
                                user_drawn.end_point.y,
                            ],
                        },
                    ],
                },
                "properties": {"id": user_drawn.id},
            }
        )

    # When you make a geoJSON yourself, you don't need to serialize it
    user_drawn_json = {"type": "FeatureCollection", "features": user_features}

    city_name = CITY_CONTEXT[city]["CityName"]

    # Get dashboard metrics:
    dashboard_dict = dashboard_metrics(city)

    # Get daily ridership:
    daily_ridership_json = get_daily_ridership(city)

    # Get top transit stations:
    top_bus_weekend = extract_top_ten(
        city=city, mode=3, transit_unit=CITY_RIDERSHIP_LEVEL[city]["bus"], weekday=False
    )
    top_subway_weekend = extract_top_ten(
        city=city,
        mode=CITY_CONTEXT[city]["subway_mode"],
        transit_unit=CITY_RIDERSHIP_LEVEL[city]["subway"],
        weekday=False,
    )
    top_bus_weekday = extract_top_ten(
        city=city, mode=3, transit_unit=CITY_RIDERSHIP_LEVEL[city]["bus"], weekday=True
    )
    top_subway_weekday = extract_top_ten(
        city=city,
        mode=CITY_CONTEXT[city]["subway_mode"],
        transit_unit=CITY_CONTEXT[city]["subway_level"],
        weekday=True,
    )

    context = {
        "City": CITY_CONTEXT[city]["CityName"],
        "City_NoSpace": city,
        "citydata": dashboard_dict,
        "heatmaplabel": f"{city_name} By Census Tract",
        "about_class": "cs-li-link",
        "cities_class": "cs-li-link",
        "policy_class": "cs-li-link cs-active",
        "survey_class": "cs-li-link",
        "feedback_class": "cs-li-link",
        "coordinates": CITY_CONTEXT[city]["Coordinates"],
        "stations": stations_json,
        "daily_ridership": daily_ridership_json,
        "top_bus_weekend": top_bus_weekend,
        "top_bus_weekday": top_bus_weekday,
        "top_subway_weekend": top_subway_weekend,
        "top_subway_weekday": top_subway_weekday,
        "lineplot": CITY_CONTEXT[city]["lineplot"],
        "geojsonfilepath": static(CITY_CONTEXT[city]["geojsonfilepath"]),
        "routes": routes_json,
        "heatmap_categories": [
            "median_income",
            "total_weighted_commute_time",
            "percentage_subway_to_work",
            "percentage_bus_to_work",
            "percentage_public_to_work",
            "population",
        ],
        "heatmap_units": {
            "median_income": "dollars",
            "total_weighted_commute_time": "minutes",
            "percentage_subway_to_work": "%",
            "percentage_bus_to_work": "%",
            "percentage_public_to_work": "%",
            "population": "people",
        },
        "heatmap_titles": {
            "median_income": "Median Income",
            "total_weighted_commute_time": "Total Average Commute Time",
            "percentage_subway_to_work": "Percent of People who Subway to Work",
            "percentage_bus_to_work": "Percent of People who Bus to Work",
            "percentage_public_to_work": "Percent of people who commute via subway",
            "population": "Population",
        },
        "heatmap_titles_reversed": {
            "Median Income": "median_income",
            "Total Average Commute Time": "total_weighted_commute_time",
            "Percent of People who Subway to Work": "percentage_subway_to_work",
            "Percent of People who Bus to Work": "percentage_bus_to_work",
            "Percent of people who commute via subway": "percentage_public_to_work",
            "Population": "population",
        },
        "user_drawn": user_drawn_json,
    }

    return render(request, "dashboard.html", context)


def survey_p1(request, city: str):
    """
    Survey intro page
    """
    # Gen unique user id with uuid
    request.session["uuid"] = str(uuid.uuid4())
    request.session["route_id"] = 1

    if request.method == "POST":
        # create new SurveyUser object
        city_survey = CITIES_CHOICES_SURVEY[city]
        survey_answer = SurveyUser(user_id=request.session["uuid"], city=city_survey)

        update_survey = RiderSurvey1(request.POST, instance=survey_answer)
        # update and save
        update_survey.save()

        return redirect(reverse("app:survey_p2", kwargs={"city": city}))

    else:  # GET
        form = RiderSurvey1()

    context = get_survey_context(city, form)

    return render(request, "survey.html", context)


def survey_p2(request, city: str, user_id: str = None):
    """
    Question about trip
    """
    print(request.method)
    user_id = request.session.get("uuid")
    route_id = request.session.get("route_id")

    if request.method == "POST":
        # post form data to database
        city_survey = CITIES_CHOICES_SURVEY[city]
        try:
            survey_answer = SurveyResponse.objects.get(
                user_id_id=user_id, city=city_survey, route_id=route_id
            )
            survey_answer = RiderSurvey2(request.POST, instance=survey_answer)
        except Exception as e:
            print(e)
            survey_answer = SurveyResponse(
                user_id_id=user_id, city=city_survey, route_id=route_id
            )
            print(f"survey answer pg 2: {survey_answer}")
            survey_answer = RiderSurvey2(request.POST, instance=survey_answer)

        # Get the line string data and update database
        post_line_string = request.POST.get("lineString")
        # Convert the string to a list of tuples
        line_string_coords = json.loads(post_line_string)
        # Create a LineString object
        route = LineString(line_string_coords)
        # Access the first and last points
        starting_point = route.coords[0]
        end_point = route.coords[-1]

        # Update row in database

        survey_answer.route = route
        survey_answer.starting_point = Point(starting_point)
        survey_answer.end_point = Point(end_point)
        survey_answer.save()

        # return selected mode of transit from form
        selected_mode_index = survey_answer.cleaned_data["modes_of_transit"]
        selected_mode = MODES_OF_TRANSIT[selected_mode_index]

        if selected_mode == "Train" or selected_mode == "Bus":
            return redirect(reverse("app:survey_p3", kwargs={"city": city}))
        elif selected_mode == "Car" or selected_mode == "Rideshare":
            return redirect(reverse("app:survey_p4", kwargs={"city": city}))
        else:
            return redirect(reverse("app:survey_p5", kwargs={"city": city}))

    else:  # GET
        form = RiderSurvey2()

    context = get_survey_context(city, form)

    return render(request, "survey_map.html", context)


def survey_p3(request, city: str):
    """
    Questions for transit riders
    """
    user_id = request.session.get("uuid")
    route_id = request.session.get("route_id")
    print(request.method)

    if request.method == "POST":
        survey_answer = SurveyResponse.objects.get(
            user_id_id=user_id, route_id=route_id
        )
        update_survey = RiderSurvey3(request.POST, instance=survey_answer)
        update_survey.save()

        # check if user has another trip to report
        another_trip = update_survey.cleaned_data["another_trip"]

        # Not recognizing T/F as booleans so using string
        if another_trip == "True" and int(route_id) < 3:
            route_id += 1
            print(route_id)
            request.session["route_id"] = route_id
            return redirect(reverse("app:survey_p2", kwargs={"city": city}))
        else:
            return redirect(reverse("app:thanks", kwargs={"city": city}))

    else:  # GET
        form = RiderSurvey3()

    context = get_survey_context(city, form)

    return render(request, "survey_internal.html", context)


def survey_p4(request, city: str):
    """
    Questions for drivers and rider share
    """
    user_id = request.session.get("uuid")
    route_id = request.session.get("route_id")
    print(request.method)
    if request.method == "POST":
        survey_answer = SurveyResponse.objects.get(
            user_id_id=user_id, route_id=route_id
        )
        update_survey = RiderSurvey4(request.POST, instance=survey_answer)
        update_survey.save()

        # check if user has another trip to report
        another_trip = update_survey.cleaned_data["another_trip"]

        if another_trip == "True" and int(route_id) < 3:
            route_id += 1
            print(route_id)
            request.session["route_id"] = route_id
            return redirect(reverse("app:survey_p2", kwargs={"city": city}))
        else:
            return redirect(reverse("app:thanks", kwargs={"city": city}))

    else:  # GET
        form = RiderSurvey4()

    context = get_survey_context(city, form)

    return render(request, "survey_internal.html", context)


def survey_p5(request, city: str):
    """
    Check if bikers and walkers have another trip to report.
    """
    route_id = request.session.get("route_id")
    print(request.method)
    if request.method == "POST":
        form = RiderSurvey5(request.POST)
        form.is_valid()

        # check if user has another trip to report
        another_trip = form.cleaned_data["another_trip"]

        if another_trip == "True" and int(route_id) < 3:
            route_id += 1
            print(route_id)
            request.session["route_id"] = route_id
            return redirect(reverse("app:survey_p2", kwargs={"city": city}))
        else:
            return redirect(reverse("app:thanks", kwargs={"city": city}))

    else:  # GET
        form = RiderSurvey5()

    context = get_survey_context(city, form)

    return render(request, "survey_internal.html", context)


def thanks(request, city: str):
    url = "thanks"

    context = {
        "City": CITY_CONTEXT[city]["CityName"],
        "City_NoSpace": city,
        "about_class": "cs-li-link",
        "cities_class": "cs-li-link",
        "policy_class": "cs-li-link ",
        "survey_class": "cs-li-link cs-active",
        "feedback_class": "cs-li-link",
        "Coordinates": CITY_CONTEXT[city]["Coordinates"],
        "url": url,
    }
    return render(request, "thanks.html", context)


def responses(request, city: str):
    context = {
        "City": CITY_CONTEXT[city]["CityName"],
        "Response": get_number_of_responses(city),
        "City_NoSpace": city,
        "Riders": get_transit_use_pct(city),
        "about_class": "cs-li-link",
        "cities_class": "cs-li-link",
        "policy_class": "cs-li-link ",
        "survey_class": "cs-li-link",
        "feedback_class": "cs-li-link cs-active",
        "coordinates": CITY_CONTEXT[city]["Coordinates"],
        "ridersatisfaction": get_rider_satisfaction(city),
        "transit_mode_graph": get_transit_mode(city),
        "toptengraph": get_trip_top(city),
        "tranrideimprov_rider": get_transit_improv_riders_dict(city),
        "tranrideimprov_drivers": get_transit_improv_drivers_dict(city),
    }
    return render(request, "responses.html", context)


def get_survey_context(city, form):
    context = {
        "City": CITY_CONTEXT[city]["CityName"],
        "City_NoSpace": city,
        "about_class": "cs-li-link",
        "cities_class": "cs-li-link",
        "policy_class": "cs-li-link ",
        "survey_class": "cs-li-link cs-active",
        "feedback_class": "cs-li-link",
        "coordinates": CITY_CONTEXT[city]["Coordinates"],
        "form": form,
    }
    return context
