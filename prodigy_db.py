import jsonlines
from prodigy.components.db import connect

db = connect()
all_dataset_names = db.datasets
examples = db.get_dataset("antebadger")
labels = set()
for data in examples:
    for cat in data.get("spans"):
        labels.add(cat.get("label"))
print(labels)
