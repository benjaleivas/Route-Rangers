# ask JP why we're importing like this instead of:
# from django import forms
from django.contrib.gis import forms
from route_rangers_api.models import SurveyResponse, SurveyUser
from django.forms import ModelForm, RadioSelect, Textarea, NumberInput
from django.utils.translation import gettext_lazy as _

MODES_OF_TRANIST = {
    "bus": "Bus",
    "train": "Train",
    "car": "Car",
    "bike": "Bike",
    "walking": "Walking",
    "rideshare": "Rideshare",
}

TRIP_FREQ = {
    "daily": "Everyday",
    "weekdays": "Weekdays",
    "weekends": "Weekends",
    "few_week": "A few times per week",
    "few_month": "A few times per month",
    "few_year": "A few times per year",
}

TIME_OF_DAY = {"peak": "Peak commute hours", "day": "Daytime", "night": "Nighttime"}

SATISFIED = {"1": 1, "2": 2, "3": 3, "4": 4, "5": 5}

TRANSIT_IMPROVEMENT = {
    "frequent_service": "More frequent service",
    "accurate_schedule": "More accurate schedule times",
    "fewer_transfers": "Fewer transfers or a more direct route",
    "safety": "It feels safe at the station and onboard",
}

SWITCH_TO_TRANSIT = {
    "stops": "There are stops near you",
    "schedule": "There are many scheduled departures",
    "length": "It doesn't take significantly longer than driving",
    "seats": "There are enough seats for all riders",
    "safe": "It feels safe at the station and onboard",
    "cost": "It will save me money",
}

QUESTIONS = {
    "p1": {
        "frequent_transit": "Do you use public transit regularly?",
        "car_owner": "Do you own a car or other motorized vehicle?",
    },
    "p2": {
        "trip_freq": "When do you usually make this trip?",
        "trip_tod": "What time of day you usually make this trip?",
        "trip_time": "How long does this trip currently take in minutes?",
        "modes_of_transit": "What mode of transit do you usually use to make \
            this trip?",
    },
    "p3": {
        "satisfied": "How satisfied are you with the public transit options \
            for this route? Consider 1 to be 'Very Unstisfied' \
                  and 5 'Very Satisfied",
        "transit_improvement": "How could this public transit route be \
              improved?",
        "transit_improvement_open": "Other suggestions on how this transit \
            route could be improved:",
        "another_trip": "Do you have another trip you would like to report?",
    },
    "p4": {
        "switch": "Assuming that a new transit route is built connecting these \
            stops, what factor would most motivate you to choose to take \
                public transit?",
        "another_trip": "Do you have another trip you would like to report?",
    },
    "p5": {
        "another_trip": "Do you have another trip you would like to report?",
    },
}

BOOL_CHOICES = ((True, "Yes"), (False, "No"))


class RiderSurvey1(ModelForm):
    """
    Survey intro page
    """

    class Meta:
        model = SurveyUser
        fields = ["frequent_transit", "car_owner"]
        labels = {
            "frequent_transit": _(QUESTIONS["p1"]["frequent_transit"]),
            "car_owner": _(QUESTIONS["p1"]["car_owner"]),
        }
        widgets = {
            "frequent_transit": forms.RadioSelect(attrs={"class": "form-radio"}),
            "car_owner": forms.RadioSelect(attrs={"class": "form-radio"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove the placeholder choice
        self.fields["frequent_transit"].widget.choices = [
            choice
            for choice in self.fields["frequent_transit"].choices
            if choice[0] != ""
        ]
        self.fields["car_owner"].widget.choices = [
            choice for choice in self.fields["car_owner"].choices if choice[0] != ""
        ]


class RiderSurvey2(ModelForm):
    """
    Question about trip
    """

    class Meta:
        model = SurveyResponse
        fields = [
            "trip_frequency",
            "trip_tod",
            "trip_time",
            "modes_of_transit",
        ]
        labels = {
            "trip_frequency": _(QUESTIONS["p2"]["trip_freq"]),
            "trip_tod": _(QUESTIONS["p2"]["trip_tod"]),
            "trip_time": _(QUESTIONS["p2"]["trip_time"]),
            "modes_of_transit": _(QUESTIONS["p2"]["modes_of_transit"]),
        }
        widgets = {
            "trip_frequency": RadioSelect(attrs={"class": "form-radio"}),
            "trip_tod": RadioSelect(attrs={"class": "form-radio"}),
            "trip_time": NumberInput(attrs={"class": "NumberInput", "min": 0}),
            "modes_of_transit": RadioSelect(attrs={"class": "form-radio"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove the placeholder choice
        self.fields["trip_frequency"].widget.choices = [
            choice
            for choice in self.fields["trip_frequency"].choices
            if choice[0] != ""
        ]
        self.fields["trip_tod"].widget.choices = [
            choice for choice in self.fields["trip_tod"].choices if choice[0] != ""
        ]
        self.fields["modes_of_transit"].widget.choices = [
            choice
            for choice in self.fields["modes_of_transit"].choices
            if choice[0] != ""
        ]


class RiderSurvey3(ModelForm):
    """
    Questions for transit riders
    """

    another_trip = forms.ChoiceField(
        label=QUESTIONS["p3"]["another_trip"],
        choices=BOOL_CHOICES,
        widget=RadioSelect(attrs={"class": "form-radio"}),
    )

    class Meta:
        model = SurveyResponse
        fields = ["satisfied", "transit_improvement"]
        labels = {
            "satisfied": _(QUESTIONS["p3"]["satisfied"]),
            "transit_improvement": _(QUESTIONS["p3"]["transit_improvement"]),
        }

        widgets = {
            "satisfied": RadioSelect(attrs={"class": "form-radio"}),
            "transit_improvement": RadioSelect(attrs={"class": "form-radio"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove the placeholder choice
        self.fields["satisfied"].widget.choices = [
            choice for choice in self.fields["satisfied"].choices if choice[0] != ""
        ]
        self.fields["transit_improvement"].widget.choices = [
            choice
            for choice in self.fields["transit_improvement"].choices
            if choice[0] != ""
        ]


class RiderSurvey4(ModelForm):
    """
    Questions for drivers and rider share
    """

    another_trip = forms.ChoiceField(
        label=QUESTIONS["p4"]["another_trip"],
        choices=BOOL_CHOICES,
        widget=RadioSelect(attrs={"class": "form-radio"}),
    )

    class Meta:
        model = SurveyResponse
        fields = ["switch_to_transit"]
        labels = {
            "switch_to_transit": _(QUESTIONS["p4"]["switch"]),
        }

        widgets = {"switch_to_transit": RadioSelect(attrs={"class": "form-radio"})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove the placeholder choice
        self.fields["switch_to_transit"].widget.choices = [
            choice
            for choice in self.fields["switch_to_transit"].choices
            if choice[0] != ""
        ]


# use forms.Forms not ModelForm because not writing to database
class RiderSurvey5(forms.Form):
    """
    Check if bikers and walkers have another trip to report.
    """

    another_trip = forms.ChoiceField(
        label=QUESTIONS["p5"]["another_trip"],
        choices=BOOL_CHOICES,
        widget=RadioSelect(attrs={"class": "form-radio"}),
    )
