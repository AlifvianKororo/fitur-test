import os
import flash
import wandb
from flash.image import ObjectDetectionData, ObjectDetector
from pytorch_lightning.loggers import WandbLogger


class TrainModel:
    def __init__(self, dataset_location, db_name):
        self.db_name = db_name
        os.environ["WANDB_API_KEY"] = "cbb9e471722cfa8126ca14789c172a6115c6cc21"
        # wandb.login()
        wandb.init(project=self.db_name)
        self.dataset_location = dataset_location
        self.data_module = self.datamodule(self.dataset_location)
        self.train()

    def datamodule(self, dataset_location):
        datamodule = ObjectDetectionData.from_coco(
            train_folder=dataset_location,
            train_ann_file=dataset_location + "_annotations.coco.json",
            val_split=0.1,
            transform_kwargs={"image_size": 128},
            batch_size=4,
        )
        return datamodule

    def train(self):
        wandb_logger = WandbLogger(project=self.db_name, job_type="train")
        model = ObjectDetector(
            head="efficientdet",
            backbone="d0",
            num_classes=self.data_module.num_classes,
            image_size=128,
        )
        trainer = flash.Trainer(max_epochs=15, logger=wandb_logger)
        trainer.finetune(model, datamodule=self.data_module, strategy="freeze")
        trainer.save_checkpoint("object_detection_model.pt")
        wandb.finish()


class PredictModel:
    def __init__(self, dataset_location, model_location):
        self.dataset_location = dataset_location
        self.model_location = model_location
        self.all_data = self.get_all_data(self.dataset_location)

    def get_all_data(self):
        data =[os.path.join(self.dataset_location, i) for i in os.listdir(self.dataset_location)]
        return data




TrainModel(dataset_location="./dataset/", db_name="antebadger")