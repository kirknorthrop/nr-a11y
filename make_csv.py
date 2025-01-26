import csv

from main import get_stations, get_station_accessibility_surveys
from make_html import Station, Survey, Question

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
            surveys_by_type={},
        )

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
                        statement=question.get("statement"),
                        last_updated=question.get("lastUpdatedDate"),
                    )
                    survey.questions.append(question_data)

                station.surveys.append(survey)

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

        data[station.id] = station

    sorted_stations = sorted(data.values(), key=lambda s: s.name)

    csv_data = []
    fields = []
    for station in sorted_stations:
        this_data = {
            "name": station.name,
            "crs": station.crs,
        }

        for survey in station.surveys:
            if survey.type in ["Station", "QA Questions"]:
                for question in survey.questions:
                    fields.append(question.question)
                    this_data[question.question] = question.answer

        # print(this_data)
        csv_data.append(this_data)

    with open("data.csv", "w", newline="") as csvfile:
        fieldnames = ["name", "crs"] + list(set(fields))
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for item in csv_data:
            writer.writerow(item)

    #     this_data["id"] = station.id
    #     this_data["name"] = station.name
    #
    #
    # print(len(data))
    # print(len(bad_stations))
