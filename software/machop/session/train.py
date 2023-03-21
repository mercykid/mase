import pytorch_lightning as pl
from pytorch_lightning.callbacks import ModelCheckpoint
from pytorch_lightning.loggers import TensorBoardLogger

from ..utils import load_model
from .plt_wrapper import get_model_wrapper


def train(
    model_name,
    info,
    model,
    task,
    data_loader,
    optimizer,
    learning_rate,
    plt_trainer_args,
    save_path,
    load_path,
):
    # if save_path is None, the model will not be saved
    if save_path is not None:
        checkpoint_callback = ModelCheckpoint(
            save_top_k=1,
            monitor="val_loss",
            mode="min",
            filename="best",
            dirpath=save_path,
            save_last=True,
        )
        logger = TensorBoardLogger(save_dir=save_path, name="logs")
        plt_trainer_args["callbacks"] = [checkpoint_callback]
        plt_trainer_args["logger"] = logger
    wrapper_cls = get_model_wrapper(model_name, task)
    plt_model = wrapper_cls(
        model,
        info=info,
        learning_rate=learning_rate,
        epochs=plt_trainer_args["max_epochs"],
        optimizer=optimizer,
    )
    # Here load_model may load a modified mdoel from a pickle file
    plt_model = load_model(plt_model=plt_model, load_path=load_path)
    # A hack for modified model...
    if not isinstance(plt_model, pl.LightningModule):
        # rewrap
        plt_model = wrapper_cls(
            model,
            info=info,
            learning_rate=learning_rate,
            epochs=plt_trainer_args["max_epochs"],
            optimizer=optimizer,
        )

    trainer = pl.Trainer(**plt_trainer_args)
    trainer.fit(
        plt_model,
        train_dataloaders=data_loader.train_dataloader,
        val_dataloaders=data_loader.val_dataloader,
    )