import json
import pytz

from collections import OrderedDict
from datetime import datetime
from flask import Flask, request


def time2human(sec):
    result = ""
    if sec // 3600 > 0:
        result += str(sec // 3600) + "h"
        sec %= 3600
    if sec // 60 > 0:
        result += str(sec // 60) + "m"
        sec %= 60
    result += str(sec) + "s"
    return result


FILENAME = "data.jsonl"
TIMEZONE = "Asia/Shanghai"
PING_PANG_THRESHOLD = 120

app = Flask(__name__)


@app.route("/")
def hello():
    return "hello"


@app.route("/pub", methods=["POST"])
def pub():
    # print raw request data
    with open(FILENAME, "ab") as f:
        f.write(request.data)
        f.write(b"\n")
    return "done"


@app.route("/report")
def report():
    data = []
    with open(FILENAME, "r", encoding="utf-8") as f:
        data = f.readlines()
    data = [json.loads(item) for item in data]
    data = [item for item in data if item.get("event") in ["leave", "enter"]]
    chinaTz = pytz.timezone(TIMEZONE)

    # remove item with very close time and same event
    masks = [False] * len(data)
    for i in range(1, len(data)):
        if abs(data[i]["tst"] - data[i - 1]["tst"]) < PING_PANG_THRESHOLD and \
           data[i]["desc"] == data[i - 1]["desc"] and \
           data[i]["event"] == data[i - 1]["event"]:
            masks[i - 1] = True
            masks[i] = False
    data = [item for i, item in enumerate(data) if not masks[i]]

    # remove item with very close time and different event
    masks = [False] * len(data)
    for i in range(1, len(data)):
        if abs(data[i]["tst"] - data[i - 1]["tst"]) < PING_PANG_THRESHOLD and \
           data[i]["desc"] == data[i - 1]["desc"] and \
           data[i]["event"] != data[i - 1]["event"]:
            masks[i - 1] = True
            masks[i] = True
    data = [item for i, item in enumerate(data) if not masks[i]]

    # fix the error
    for item in data:
        # remove 3 minutes if leave
        if item["event"] == "leave":
            item["tst"] -= 180
        # add 3 minutes if enter
        if item["event"] == "enter":
            item["tst"] += 180

    # add date time datetime
    data = [
        {
            "desc": item["desc"],
            "event": item["event"],
            "date": datetime.fromtimestamp(item["tst"], chinaTz).strftime(
                "%m/%d"
            ),
            "time": datetime.fromtimestamp(item["tst"], chinaTz).strftime(
                "%H:%M"
            ),
            "datetime": datetime.fromtimestamp(item["tst"], chinaTz).strftime(
                "%m/%d %H:%M"
            ),
            "tst": item["tst"]
        }
        for item in data
    ]

    # group by time
    grouped = OrderedDict()
    for item in data:
        if item["date"] not in grouped:
            grouped[item["date"]] = []
        grouped[item["date"]].append(item)

    # add time diff
    for date in grouped:
        grouped[date][0]["time_diff"] = 0
        if len(grouped[date]) > 1:
            for i in range(1, len(grouped[date])):
                grouped[date][i]["time_diff"] = grouped[date][i]["tst"] - \
                    grouped[date][i - 1]["tst"]

    result = [
        [
            date,
            "\n".join(
                [
                    f"\t{item['time']}\t{item['event']}\t{item['desc']}\t{time2human(item['time_diff'])}"
                    for item in items
                ]
            ),
        ]
        for date, items in reversed(grouped.items())
    ]

    return (
        "\n".join([y for x in result for y in x]),
        200,
        {"Content-Type": "text/plain; charset=utf-8"},
    )


if __name__ == "__main__":
    print("Starting server...")
    app.run(host="0.0.0.0")
