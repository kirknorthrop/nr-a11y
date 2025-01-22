import os
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict
from mako.template import Template
from main import get_stations, get_station_accessibility_surveys


@dataclass
class Question:
    question: str
    answer: str
    statement: str
    last_updated: datetime


@dataclass
class Survey:
    id: str
    name: str
    alternative_name: str
    friendly_name: str
    type: str
    questions: List[Question] = None


@dataclass
class Station:
    name: str
    id: str
    crs: str
    surveys: List[Survey] = None
    types: List[str] = None
    surveys_by_type: Dict = None


def make_survey_page(survey, station):
    template = Template(filename="survey.html")
    output = template.render(survey=survey, station=station)

    with open(f"../nr-a11y-site/{station.crs}/{survey.id}.html", "w") as f:
        f.write(output)


def make_station_page(station):
    template = Template(filename="station.html")
    output = template.render(station=station)

    with open(f"../nr-a11y-site/{station.crs}/{station.id}.html", "w") as f:
        f.write(output)


def make_station_list_page(stations):
    template = Template(filename="station_list.html")
    output = template.render(stations=stations)

    with open(f"../nr-a11y-site/index.html", "w") as f:
        f.write(output)


if __name__ == "__main__":
    stations, _ = get_stations()

    data = {}
    bad_stations = []

    for station_dict in stations["data"]["resultSet"]:
        station = Station(
            name=station_dict["name"].replace("Stn", "").strip(),
            id=station_dict["id"],
            crs=station_dict["crsCode"],
            surveys=[],
            types=[],
            surveys_by_type={}
        )
        try:
            os.mkdir(f"../nr-a11y-site/{station.crs}")
        except FileExistsError:
            pass

        surveys, _ = get_station_accessibility_surveys(station.id)

        try:
            for survey_dict in surveys["data"]["surveyBlocks"]:
                survey = Survey(
                    id=survey_dict["id"],
                    name=survey_dict["name"],
                    alternative_name=survey_dict.get("alternativeName"),
                    friendly_name=survey_dict.get("friendlyName"),
                    type=survey_dict["type"],
                    questions=[],
                )

                for question in survey_dict["survey"]["questionsAndAnswers"]:
                    question_data = Question(
                        question=question["name"],
                        answer=question["answer"],
                        statement=question.get('statement'),
                        last_updated=question.get("lastUpdatedDate"),
                    )
                    survey.questions.append(question_data)

                station.surveys.append(survey)

                make_survey_page(survey, station)

            surveys_by_type = {}
            for survey in station.surveys:
                if surveys_by_type.get(survey.type) is None:
                    surveys_by_type[survey.type] = []
                surveys_by_type[survey.type].append(survey)

            station.surveys_by_type = surveys_by_type
            station.types = surveys_by_type.keys()

        except KeyError:
            print(station)
            bad_stations.append(station)

        make_station_page(station)

        data[station.id] = station

    sorted_stations = sorted(data.values(), key=lambda s: s.name)
    make_station_list_page(sorted_stations)

    print(len(data))
    print(len(bad_stations))
