import functools
import os
import pickle
import types

import torch

use_cuda = torch.cuda.is_available()
print("Using cuda:{}".format(use_cuda))
torch_cuda = torch.cuda if use_cuda else torch
device = torch.device("cuda" if use_cuda else "cpu")


def get_checkpoint_file(checkpoint_dir):
    for file in os.listdir(checkpoint_dir):
        if file.endswith(".ckpt"):
            return file


def plt_model_load(model, checkpoint):
    if checkpoint.endswith(".pkl"):
        with open(checkpoint, "rb") as f:
            model = pickle.load(f)
    else:
        state_dict = torch.load(checkpoint)["state_dict"]
        model.load_state_dict(state_dict)
    return model


def load_model(load_path, plt_model):
    if load_path is not None:
        if load_path.endswith(".ckpt") or load_path.endswith(".pkl"):
            checkpoint = load_path
        else:
            if load_path.endswith("/"):
                checkpoint = load_path + "best.ckpt"
            else:
                raise ValueError(
                    "if it is a directory, if must end with /; if it is a file, it must end with .ckpt or .pkl"
                )
        plt_model = plt_model_load(plt_model, checkpoint)
        print(f"Loaded model from {checkpoint}")
    return plt_model


def check_conda_env(is_sw_env: bool, requires_sw_env: bool, current_action_name: str):
    if requires_sw_env:
        if not is_sw_env:
            raise RuntimeError(
                f"The torch-mlir env is activated. Please switch to cuda pytorch env for {current_action_name}"
            )
    else:
        # requires hw env
        if is_sw_env:
            raise RuntimeError(
                f"The cuda pytorch env is activated. Please switch to torch-mlir env for {current_action_name}"
            )