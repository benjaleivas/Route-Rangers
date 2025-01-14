"""
OBJECTIVE: Ingest Portland Ridership Data into our Database
AUTHOR: Jimena Salinas
DATE: 05/06/2024

SOURCES: the data sets were obtained by a direct request to the 
TriMet Public Records department. This is the link to the form
to request data sets for Tri Met: 
https://trimet.org/publicrecords/recordsrequest.htm
The  Receipt ID for this Public Records Request is PRR 2024-254.

VARIABLES:
    - ID (int): this ID is the foreign key from the TransitStations table,
    it can be obtained using city = 'PDX' and station_id
    - station_id (from JSON raw file): (str) a stop_id (GTFS), only needed to 
    get the foreign key, it does not go into the ridership db table
    - date: (datetime) represents a day in the format yyyy-mm-dd, only includes
    values for 2023
    - ridership: (int) represents the average number of bus and light rail Tri Met
    riders. The riders value was originally provided as an average by season 
    and day type (Saturday, Sunday, and Weekday). In order to fit the data model
    for the project which is at the datetime level, the data has been mapped to dates in 2023.
"""

import json
import sys
import os
from requests.models import Response
import django
import datetime
from datetime import datetime
import pytz
from typing import List, Dict, Any
from django.db.utils import IntegrityError
from dotenv import load_dotenv

load_dotenv()

json_file_path = os.getenv("JSON_FILE_PATH")

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(parent_dir)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "geodjango.settings")

django.setup()

from route_rangers_api.models import TransitStation, RidershipStation


def format_input_ridership_data(
    json_file_path: str, start_date: datetime.date, end_date: datetime.date
) -> List[Dict[str, Any]]:
    """
    Format the dates in the input JSON ridership data
    and filter the data set to only include the dates that we need to
    work with
    """
    formatted_data = []
    with open(json_file_path, "r") as file:
        data = json.load(file)
    for record in data:
        timestamp_seconds = int(record["date"]) / 1000
        date_obj = datetime.fromtimestamp(timestamp_seconds)
        formatted_date = date_obj.strftime("%Y-%m-%d %H:%M:%S")
        record["date"] = formatted_date
        if start_date <= date_obj <= end_date:
            formatted_data.append(record)
    print("JSON ready..")
    return formatted_data


def ingest_pdx_ridership_data(
    json_file_path: str, start_date: datetime.date, end_date: datetime.date
) -> None:
    """
    Ingest portland ridership data from extracted JSON file
    into Django database for a given subset of date ranges
    """
    stations_not_matched = []

    formatted_data = format_input_ridership_data(json_file_path, start_date, end_date)

    for record in formatted_data:
        try:
            # Get the id from TransitStation using station_id + city = 'PDX'
            transit_station = TransitStation.objects.filter(
                station_id=str(record["station_id"]), city="PDX"
            ).first()

            if transit_station:
                foreign_key = transit_station.id
                date_str = record["date"]
                date_obj = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                # date formatting to match model

                if start_date <= date_obj <= end_date:

                    ridership_obj = RidershipStation.objects.create(
                        date=date_obj,
                        ridership=record["ridership"],
                        station_id=foreign_key,
                    )

                    if foreign_key % 10 == 0:
                        print(f"Ingesting ridership data for key {foreign_key}...")
                        # print info every 10 records

                    ridership_obj.save()
                else:
                    print(
                        f"Skipping ingestion for key {foreign_key}, foreign key not found in TransitStation"
                    )

        except TransitStation.DoesNotExist:
            stations_not_matched.append(record["station_id"])
            print(
                f"Skipping ingestion for station {record['station_id']}, no matching TransitStation"
            )
            continue

        except IntegrityError as e:
            # foreign key db rule violation, skips records if they are already in the db
            print(
                f"Skipping ingestion for station {record['station_id']} due to foreign key constraint violation"
            )
            continue

    print("Ingestion complete")


def run():
    """
    Ingest PDX ridership data into Django db
    """
    start_date = datetime(2023, 7, 2)
    end_date = datetime(2023, 7, 31)
    ingest_pdx_ridership_data(json_file_path, start_date, end_date)


if __name__ == "__main__":
    run()
