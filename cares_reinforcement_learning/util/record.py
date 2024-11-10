import json
import logging
import os

import cv2
import numpy as np
import pandas as pd
from torch import nn

import cares_reinforcement_learning.util.plotter as plt


class Record:
    """
    A class that represents a record for logging and saving data during training and evaluation.

    Args:
        glob_log_dir (str): DEPRECATED - Just use the log_dir
        log_dir (str): The log directory.
        algorithm (str): The algorithm name.
        task (str): The task name.
        plot_frequency (int, optional): The frequency at which to plot training data. Defaults to 10.
        checkpoint_frequency (int, optional): The frequency at which to save model checkpoints. If not set model will not auto-save, use save_model externally to save.
        network (nn.Module, optional): The neural network model. Defaults to None.
    """

    def __init__(
        self,
        log_dir: str,
        algorithm: str,
        task: str,
        plot_frequency: int = 10,
        network: nn.Module | None = None,
    ) -> None:

        self.best_reward = float("-inf")

        self.log_dir = log_dir

        self.directory = f"{log_dir}"

        self.algorithm = algorithm
        self.task = task

        self.plot_frequency = plot_frequency

        self.train_data_path = f"{self.directory}/data/train.csv"
        self.train_data = (
            pd.read_csv(self.train_data_path)
            if os.path.exists(self.train_data_path)
            else pd.DataFrame()
        )
        self.eval_data_path = f"{self.directory}/data/eval.csv"
        self.eval_data = (
            pd.read_csv(self.eval_data_path)
            if os.path.exists(self.eval_data_path)
            else pd.DataFrame()
        )

        if not self.train_data.empty or not self.eval_data.empty:
            logging.warning("Data files not empty. Appending to existing data")

        self.network = network

        self.log_count = 0

        self.video: cv2.VideoWriter = None

        self.__initialise_directories()

    def save_config(self, configuration: dict, file_name: str) -> None:
        with open(
            f"{self.directory}/{file_name}.json", "w", encoding="utf-8"
        ) as outfile:
            json.dump(configuration.dict(exclude_none=True), outfile)

    def start_video(self, file_name, frame, fps=30):
        video_name = f"{self.directory}/videos/{file_name}.mp4"
        height, width, _ = frame.shape
        self.video = cv2.VideoWriter(
            video_name, cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height)
        )
        self.log_video(frame)

    def stop_video(self) -> None:
        self.video.release()

    def save_model(self, file_name):
        if self.network is not None:
            self.network.save_models(f"{file_name}", self.directory)

    def log_video(self, frame: np.ndarray) -> None:
        self.video.write(frame)

    def log_train(self, display: bool = False, **logs) -> None:
        self.log_count += 1

        self.train_data = pd.concat(
            [self.train_data, pd.DataFrame([logs])], ignore_index=True
        )
        self.save_data(self.train_data, self.train_data_path, logs, display=display)

        if self.log_count % self.plot_frequency == 0:
            plt.plot_train(
                self.train_data,
                f"Training-{self.algorithm}-{self.task}",
                f"{self.algorithm}",
                self.directory,
                "train",
                20,
            )

        reward = logs["episode_reward"]

        if reward > self.best_reward:
            logging.info(
                f"New highest reward of {reward} during training! Saving model..."
            )
            self.best_reward = reward

            self.save_model(f"{self.algorithm}-highest-reward-training")

    def log_eval(self, display: bool = False, **logs) -> None:
        self.eval_data = pd.concat(
            [self.eval_data, pd.DataFrame([logs])], ignore_index=True
        )
        self.save_data(self.eval_data, self.eval_data_path, logs, display=display)

        plt.plot_eval(
            self.eval_data,
            f"Evaluation-{self.algorithm}-{self.task}",
            f"{self.algorithm}",
            self.directory,
            "eval",
        )

        self.save_model(f"{self.algorithm}-eval-{logs['total_steps']}")

    def save_data(
        self, data_frame: pd.DataFrame, path: str, logs: dict, display: bool = True
    ) -> None:
        if data_frame.empty:
            logging.warning("Trying to save an Empty Dataframe")

        data_frame.to_csv(path, index=False)

        string = []
        for key, val in logs.items():
            if key != "info":
                string.append(f"{key}: {str(val)[0:10]:6s}")

        string = " | ".join(string)
        string = "| " + string + " |"

        if display:
            logging.info(string)

    def save(self) -> None:
        logging.info("Saving final outputs")
        self.save_data(self.train_data, self.train_data_path, {}, display=False)
        self.save_data(self.eval_data, self.eval_data_path, {}, display=False)

        if not self.eval_data.empty:
            plt.plot_eval(
                self.eval_data,
                f"Evaluation-{self.algorithm}-{self.task}",
                f"{self.algorithm}",
                self.directory,
                "eval",
            )
        if not self.train_data.empty:
            plt.plot_train(
                self.train_data,
                f"Training-{self.algorithm}-{self.task}",
                f"{self.algorithm}",
                self.directory,
                "train",
                20,
            )

        self.save_model(self.algorithm)

    def __initialise_directories(self) -> None:

        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

        if not os.path.exists(f"{self.directory}/data"):
            os.makedirs(f"{self.directory}/data")

        if not os.path.exists(f"{self.directory}/models"):
            os.makedirs(f"{self.directory}/models")

        if not os.path.exists(f"{self.directory}/figures"):
            os.makedirs(f"{self.directory}/figures")

        if not os.path.exists(f"{self.directory}/videos"):
            os.makedirs(f"{self.directory}/videos")
