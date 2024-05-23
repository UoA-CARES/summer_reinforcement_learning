import argparse
import json
import logging
import os
from glob import glob

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

logging.basicConfig(level=logging.INFO)


# TODO make the plots look how people want them too. This is just a basic example
def plot_data(
    plot_frame,
    title,
    label,
    x_label,
    y_label,
    directory,
    filename,
    display=True,
    close_figure=True,
):
    # TODO make font size a parameter

    plt.xlabel(x_label, fontsize=21)
    plt.ylabel(y_label, fontsize=21)
    plt.title(title, fontsize=30)
    plt.xticks(
        fontsize=15,
    )
    plt.yticks(
        fontsize=15,
    )
    plt.gca().xaxis.offsetText.set_fontsize(15)

    sns.lineplot(
        data=plot_frame,
        x=plot_frame["steps"],
        y="avg",
        label=label,
        errorbar="sd",
    )

    plt.legend(fontsize="15", loc="upper left")

    # Resize the plotted figure. Pixel = DPI * Inch. PLT Default DPI: 100.
    fig = plt.gcf()
    width = 800
    height = 650
    default_dpi = 100
    fig.set_dpi(default_dpi)
    fig.set_size_inches(width / default_dpi, height / default_dpi)

    plt.savefig(f"{directory}/figures/{filename}.png")

    if display:
        plt.show()

    if close_figure:
        plt.close()


def plot_comparisons(
    plot_frames, title, labels, x_label, y_label, directory, filename, display=True
):
    for plot_frame, label in zip(plot_frames, labels):
        plot_data(
            plot_frame,
            title,
            label,
            x_label,
            y_label,
            directory,
            filename,
            display=False,
            close_figure=False,
        )

    if display:
        plt.show()

    plt.close()


def prepare_eval_plot_frame(eval_data):
    x_data = "total_steps"
    y_data = "episode_reward"

    plot_frame = pd.DataFrame()

    frame_average = eval_data.groupby([x_data], as_index=False).mean()
    frame_std = eval_data.groupby([x_data], as_index=False).std()

    plot_frame["steps"] = eval_data[x_data]
    plot_frame["avg"] = eval_data[y_data]
    # plot_frame["std_dev"] = frame_std[y_data]

    # plot_frame["steps"] = frame_average[x_data]
    # plot_frame["avg"] = frame_average[y_data]
    # plot_frame["std_dev"] = frame_std[y_data]

    return plot_frame


def plot_eval(eval_data, title, label, directory, filename, display=False):
    eval_plot_frame = prepare_eval_plot_frame(eval_data)
    plot_data(
        eval_plot_frame,
        title,
        label,
        "Steps",
        "Average Reward",
        directory,
        filename,
        display,
    )


def prepare_train_plot_frame(train_data, window_size):
    x_data = "total_steps"
    y_data = "episode_reward"

    plot_frame = pd.DataFrame()
    plot_frame["steps"] = train_data[x_data]
    plot_frame["avg"] = (
        train_data[y_data].rolling(window_size, step=1, min_periods=1).mean()
    )
    plot_frame["std_dev"] = (
        train_data[y_data].rolling(window_size, step=1, min_periods=1).std()
    )

    return plot_frame


def plot_train(
    train_data, title, label, directory, filename, window_size, display=False
):
    train_plot_frame = prepare_train_plot_frame(train_data, window_size)
    plot_data(
        train_plot_frame,
        title,
        label,
        "Steps",
        "Average Reward",
        directory,
        filename,
        display,
    )


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-s",
        "--save_directory",
        type=str,
        required=True,
        help="Directory you want to save the data into",
    )
    parser.add_argument(
        "-d",
        "--data_path",
        type=str,
        nargs="+",
        help="List of Directories with data you want to compare",
        required=True,
    )
    parser.add_argument("-w", "--window_size", type=int, default=1)

    parser.add_argument("-p", "--param_tag", type=str, default="")

    parser.add_argument("-ps", "--plot_seeds", type=int, default=0)

    # converts into a dictionary
    args = vars(parser.parse_args())
    args["plot_seeds"] = True if args["plot_seeds"] == 1 else False
    return args


def main():
    args = parse_args()

    directory = args["save_directory"]
    window_size = args["window_size"]
    param_tag = args["param_tag"]

    eval_plot_frames = []
    labels = []
    title = "Undefined Task"

    for d, data_directory in enumerate(args["data_path"]):
        logging.info(
            f"Processing {d+1}/{len(args['data_path'])} Data for {data_directory}"
        )
        result_directories = glob(f"{data_directory}/*")

        average_train_data = pd.DataFrame()
        average_eval_data = pd.DataFrame()

        result_directory = result_directories[0]
        with open(f"{result_directory}/env_config.json", "r", encoding="utf-8") as file:
            env_config = json.load(file)

        with open(
            f"{result_directory}/train_config.json", "r", encoding="utf-8"
        ) as file:
            train_config = json.load(file)

        with open(f"{result_directory}/alg_config.json", "r", encoding="utf-8") as file:
            alg_config = json.load(file)

        algorithm = alg_config["algorithm"]

        param = str(alg_config[param_tag]) if param_tag in alg_config else ""
        param += str(train_config[param_tag]) if param_tag in train_config else ""
        param = f"_{param_tag}_{param}" if param else ""
        label = algorithm + param
        labels.append(label)
        task = env_config["task"]
        title = task

        seed_plot_frames = []
        seed_label = []
        for i, result_directory in enumerate(result_directories):
            logging.info(
                f"Processing Data for {algorithm}: {i+1}/{len(result_directories)} on task {task}"
            )

            if "train.csv" not in os.listdir(f"{result_directory}/data"):
                logging.warning(
                    f"Skipping {result_directory} as it does not have train.csv"
                )
                continue

            train_data = pd.read_csv(f"{result_directory}/data/train.csv")
            eval_data = pd.read_csv(f"{result_directory}/data/eval.csv")

            average_train_data = pd.concat(
                [average_train_data, train_data], ignore_index=True
            )
            average_eval_data = pd.concat(
                [average_eval_data, eval_data], ignore_index=True
            )

            if args["plot_seeds"]:
                seed_label.append(f"{label}_{i}")
                seed_plot_frame = prepare_eval_plot_frame(eval_data)
                seed_plot_frames.append(seed_plot_frame)

        if args["plot_seeds"]:
            plot_comparisons(
                seed_plot_frames,
                f"{title}",
                seed_label,
                "Steps",
                "Average Reward",
                directory,
                f"{title}-{algorithm}-eval",
                False,
            )

        eval_plot_frame = prepare_eval_plot_frame(average_eval_data)

        eval_plot_frames.append(eval_plot_frame)

    plot_comparisons(
        eval_plot_frames,
        f"{title}",
        labels,
        "Steps",
        "Average Reward",
        directory,
        f"{title}-compare-eval",
        True,
    )


if __name__ == "__main__":
    main()
