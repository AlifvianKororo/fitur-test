import prodigy
import socket
import os

import signal
import subprocess
from prodigy.components.loaders import Images
from typing import Optional, List
from pyngrok import ngrok
from prodigy.util import split_string
from prodigy.components.db import connect
from prodigy.components.loaders import JSONL


def search_port() -> str:
    sock = socket.socket()
    sock.bind(("", 0))
    port = str(sock.getsockname()[1])
    print("Free Port : {}".format(port))
    os.environ["PRODIGY_PORT"] = port
    return port


def get_len_dataset(images_path: str) -> int:
    dir = images_path
    format = ["png", "jpg", "jpeg"]
    count = 0
    for i in os.listdir(dir):
        if os.path.isfile(os.path.join(dir, i)):
            splits = i.split(".")
            if splits[-1] in format:
                count += 1
    return count


@prodigy.recipe(
    "custom_recipe_image_manual",
    dataset=("Dataset to save answers to", "positional", None, str),
    label=("One or more comma-separated labels", "option", "l", split_string),
    view_id=("Annotation interface", "option", "v", str),
)
def custom_recipe_image_manual(
    dataset, images_path, view_id="image_manual", label: Optional[List] = None
):
    len_dataset = get_len_dataset(images_path)
    print(f"The dataset has a {len_dataset} images")
    stream = Images(images_path)
    port = search_port()
    # connection = ngrok.connect(port, bind_tls=True)
    # print(connection)

    def update(examples):
        # This function is triggered when Prodigy receives annotations

        print(f"Received {len(examples)} annotations")

    def progress(ctrl, update_return_value):
        if ctrl.session_annotated >= len_dataset:
            process = subprocess.Popen(
                ["lsof", "-i", ":{0}".format(port)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            stdout, stderr = process.communicate()
            for process in str(stdout.decode("utf-8")).split("\n")[1:]:
                data = [x for x in process.split(" ") if x != ""]
                if len(data) <= 1:
                    continue
                os.kill(int(data[1]), signal.SIGTERM)
            # ngrok.kill()
        else:
            pass
        return ctrl.session_annotated / len_dataset

    def on_exit(controller):
        examples = controller.db.get_dataset(controller.dataset)
        examples = [eg for eg in examples if eg["answer"] == "accept"]
        print(f"Received {len(examples)} annotations after saving!")

    return {
        "stream": stream,
        "view_id": view_id,
        "dataset": dataset,  # save annotations in this dataset
        "update": update,
        "progress": progress,
        "on_exit": on_exit,
        "config": {  # Additional config settings, mostly for app UI
            "label": ", ".join(label) if label is not None else "all",
            "labels": label,  # Selectable label options,
            # "darken_image": 0.3 if darken else 0,
        },
    }


@prodigy.recipe(
    "custom_reannotate_image",
    dataset=("Dataset to save answers to", "positional", None, str),
    # file_path=("Path to texts", "positional", None, str),
    label=("One or more comma-separated labels", "option", "l", split_string),
    view_id=("Annotation interface", "option", "v", str),
)
def custom_reannotate_image(
    dataset,
    file_path,
    images_path,
    view_id="image_manual",
    label: Optional[List] = None,
):
    # db = connect()
    len_dataset = get_len_dataset(images_path)
    print(f"The dataset has a {len_dataset} images")
    # assert dataset in db
    # data = db.get_dataset(dataset)
    stream = JSONL(file_path)
    port = search_port()
    # connection = ngrok.connect(port, bind_tls=True)
    # print(connection)

    def update(examples):
        # This function is triggered when Prodigy receives annotations

        print(f"Received {len(examples)} annotations")

    def progress(ctrl, update_return_value):
        if ctrl.session_annotated >= len_dataset:
            process = subprocess.Popen(
                ["lsof", "-i", ":{0}".format(port)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            stdout, stderr = process.communicate()
            for process in str(stdout.decode("utf-8")).split("\n")[1:]:
                data = [x for x in process.split(" ") if x != ""]
                if len(data) <= 1:
                    continue
                os.kill(int(data[1]), signal.SIGTERM)
            # ngrok.kill()
        else:
            pass
        return ctrl.session_annotated / len_dataset

    def on_exit(controller):
        examples = controller.db.get_dataset(controller.dataset)
        examples = [eg for eg in examples if eg["answer"] == "accept"]
        print(f"Received {len(examples)} annotations after saving!")

    return {
        "stream": stream,
        "view_id": view_id,
        "dataset": dataset,  # save annotations in this dataset
        "update": update,
        "progress": progress,
        "on_exit": on_exit,
        "config": {  # Additional config settings, mostly for app UI
            "label": ", ".join(label) if label is not None else "all",
            "labels": label,  # Selectable label options,
            # "darken_image": 0.3 if darken else 0,
        },
    }
