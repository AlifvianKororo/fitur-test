import subprocess
import socket
import os
from loaders import Loaders
from train import TrainModel


def search_port() -> str:
    sock = socket.socket()
    sock.bind(("", 0))
    port = str(sock.getsockname()[1])
    print("Free Port : {}".format(port))
    os.environ["PRODIGY_PORT"] = port
    return port


def stats_prodigy():
    process = subprocess.Popen(
        ["prodigy", "stats", "-ls"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout, stderr = process.communicate()
    print(stdout.decode(), stderr)


def run_annotate(db_name: str, images_location: str, label: str):
    with subprocess.Popen(
        [
            "prodigy",
            "custom_recipe_image_manual",
            db_name,
            images_location,
            "--label",
            label,
            "-F",
            "recipes.py",
        ]
    ) as p:
        ret = p.poll()
        print("RESPONSE : ", ret)


def db_out(db_name, dataset_location):
    print("Transforming JSONL to COCO")
    Loaders(db_name, dataset_location)
    print("Done transforming")


if __name__ == "__main__":
    port = search_port()
    try:
        input_command = input(
            """
            what operation you want to choose ?
            [1] prodigy stats
            [2] run prodigy image annotation
            [3] reannotate images
        """
        )
        if input_command == "0":
            db_name = "antebadger"
            images_location = "./dataset/"
            label = "antelope,badger"
            run_annotate(
                db_name=db_name,
                images_location=images_location,
                label=label,
            )
            db_out(db_name, images_location)
            TrainModel(dataset_location=images_location, db_name=db_name)
        elif input_command == "1":
            stats_prodigy()
        elif input_command == "2":
            db_name = input("db name : ")
            images_location = input("images location : ")
            label = input("label : ")
            run_annotate(db_name=db_name, images_location=images_location, label=label)
            TrainModel(dataset_location=images_location, db_name=db_name)
        elif input_command == "3":
            db_name = input("db name : ")
            images_location = input("images location : ")
            label = input("label : ")
    except KeyboardInterrupt:
        print("This operation was shutdown")
