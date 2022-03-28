import json
from prodigy.components.db import connect
from prodigy.components.loaders import JSONL


def get_db(dataset_location: str,db_name: str) -> None:
    db = connect()
    assert db_name in db
    dataset = db.get_dataset(db_name)
    jsonl = JSONL(dataset)
    with open(dataset_location + "_annotations.jsonl") as data:
        json.dump(jsonl, data, indent=4)

get_db("./dataset/", "antebadger")