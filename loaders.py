import json
import jsonlines
from prodigy.components.db import connect


class Loaders:
    all_data = []
    categories = [{"id": 0, "name": "animals", "supercategory": "none"}]
    category_id = 1
    labels = set()

    all_images = []
    images = {}
    image_id = 0

    annotation_id = 0
    all_annotations = []
    annotations = {}

    data_info = {
        "info": {
            "year": "2022",
            "version": "1",
            "description": "converted from JSONL prodi.gy",
            "contributor": "VGG",
        },
        "licenses": [
            {
                "id": 1,
                "url": "https://creativecommons.org/licenses/by/4.0/",
                "name": "CC BY 4.0",
            }
        ],
    }

    def __init__(self, db_jsonl, dataset_location):
        self.db_jsonl = db_jsonl
        self.dataset_location = dataset_location
        self.transform(self.db_jsonl)
        self.json_dumps(self.dataset_location)

    def area(self, corners) -> float:
        n = len(corners)  # of corners
        area = 0.0
        for i in range(n):
            j = (i + 1) % n
            area += corners[i][0] * corners[j][1]
            area -= corners[j][0] * corners[i][1]
        area = abs(area) / 2.0
        return area

    def transform(self, db_jsonl):
        db = connect()
        examples = db.get_dataset(db_jsonl)
        for data in examples:
            self.all_data.append(data)
            for cat in data.get("spans"):
                self.labels.add(cat.get("label"))

        for label in self.labels:
            category = {}
            category["id"] = self.category_id
            category["name"] = label
            category["supercategory"] = "animals"
            self.categories.append(category)
            self.category_id += 1

        for obj in self.all_data:
            self.images["id"] = self.image_id
            self.images["licenses"] = 1
            self.images["file_name"] = obj.get("meta").get("file")
            self.images["coco_url"] = ""
            # images["file_name"] = obj.get("image")
            self.images["height"] = obj.get("height")
            self.images["width"] = obj.get("width")

            images_copy = self.images.copy()
            self.all_images.append(images_copy)

            for i in obj.get("spans"):
                if len(i.get("points")) == 1:
                    iscrowd = 1
                else:
                    iscrowd = 0
                self.annotations["id"] = self.annotation_id
                self.annotations["image_id"] = self.image_id
                self.annotations["category_id"] = [
                    cat.get("id")
                    for cat in self.categories
                    if i.get("label") == cat.get("name")
                ][0]
                self.annotations["iscrowd"] = iscrowd
                self.annotations["area"] = int(self.area(i.get("points")) // 1)
                self.annotations["bbox"] = [
                    int(i.get("x")),
                    int(i.get("y")),
                    int(i.get("width")),
                    int(i.get("height")),
                ]
                self.annotation_id += 1

                annotations_copy = self.annotations.copy()
                self.all_annotations.append(annotations_copy)

            self.image_id += 1

    def json_dumps(self, dataset_location):
        self.data_info["categories"] = self.categories
        self.data_info["images"] = self.all_images
        self.data_info["annotations"] = self.all_annotations

        data_info_dumps = json.dumps(self.data_info)
        data_object = json.loads(data_info_dumps)

        with open(dataset_location + "_annotations.coco.json", "w") as outfile:
            json.dump(data_object, outfile, indent=4)
