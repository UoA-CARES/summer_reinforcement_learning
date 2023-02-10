import os
import csv

import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import uuid


class Plot:
    def __init__(self, title='Training', x_label='Episode', y_label='Reward', x_data=None, y_data=None):
        if x_data is None:
            x_data = []
        if y_data is None:
            y_data = []

        plt.ion()

        self.title = title

        self.x_label = x_label
        self.y_label = y_label

        self.figure = plt.figure()
        self.figure.set_figwidth(8)

        self.x_data = x_data
        self.y_data = y_data

        sns.set_theme(style="darkgrid")

    def post(self, reward):
        self.x_data.append(len(self.x_data))
        self.y_data.append(reward)

        data_dict = {self.x_label: self.x_data, self.y_label: self.y_data}
        df = pd.DataFrame(data=data_dict)

        plt.clf()
        sns.lineplot(data=df, x=self.x_label, y=self.y_label)
        plt.pause(10e-10)

    def plot(self):
        plt.ioff()
        self.__create_plot()
        plt.show()

    def __create_plot(self):
        data_dict = {self.x_label: self.x_data, self.y_label: self.y_data}
        df = pd.DataFrame(data=data_dict)

        sns.lineplot(data=df, x=self.x_label, y=self.y_label)
        plt.title(self.title)

    def save_plot(self, file_name=str(uuid.uuid4().hex)):
        self.__create_plot()

        dir_exists = os.path.exists("figures")

        if not dir_exists:
            os.makedirs("figures")

        plt.savefig(f"figures/{file_name}")

    def save_csv(self, file_name=str(uuid.uuid4().hex), *args):
        dir_exists = os.path.exists("data")

        if not dir_exists:
            os.makedirs("data")

        data_dict = {self.x_label: self.x_data, self.y_label: self.y_data}
        df = pd.DataFrame(data=data_dict)

        df.to_csv(f"data/{file_name}", index=False)


# def write_to_file(column_title: str, file_name: str, *args):
#     """
#     Write arrays of data to file. Data written to raw_data directory
#
#     Parameters:
#         column_title: a string containing column headers separated by space
#             e.g. `column_title` = "episode reward"`
#         file_name: the name of the file to be written into
#         *args: any number of arrays that you want saved to file. Pass the arrays into the function as arguments
#
#     Returns:
#         Nothing
#
#     Example Usage:
#
#     write_to_file("Episode Reward", "results.csv", episode_array, reward_array)
#     """
#
#     dir_exists = os.path.exists("raw_data")
#
#     if not dir_exists:
#         os.makedirs("raw_data")
#
#     file_out = open(f"raw_data/{file_name}", "w")
#     csv_out = csv.writer(file_out)
#
#     csv_out.writerow(column_title.split(" "))
#
#     for row in zip(*args):
#         csv_out.writerow(row)
#
#
# def read_file(file_path: str):
#     """
#     Reads a file that contains rewards separated by new line
#
#     Parameters:
#         file_path: a string path to the data file
#     """
#     file = open(file_path, "r")
#     strings = file.readlines()
#     floats = [float(x) for x in strings]
#     return floats
#
#
# def plot_learning(title: str, reward, file_name: str = "figure.png"):
#     """
#     Plot the learning of the agent. Saves the figure to figures directory
#
#     Parameters:
#         title: title of the plot
#         reward: the array of rewards to be plot
#         file_name: the name of the figure when saved to disc
#     """
#     y = reward
#     x = range(1, len(reward) + 1)
#
#     print(reward)
#     print(x)
#
#     data_dict = {"Episode": x, "Reward": y}
#     df = pd.DataFrame(data=data_dict)
#
#     sns.set_theme(style="darkgrid")
#     plt.figure().set_figwidth(8)
#
#     sns.lineplot(data=df, x="Episode", y="Reward")
#     plt.title(title)
#
#     dir_exists = os.path.exists("figures")
#
#     if not dir_exists:
#         os.makedirs("figures")
#
#     plt.savefig(f"figures/{file_name}")
#     plt.show()
#
#
# def plot_learning_vs_average(title: str, reward, file_name: str = "figure.png", window_size: int = 10):
#     """
#     Plot the rolling average and the actual learning. Saves the figure to figures directory
#
#     Parameters:
#         title: title of the plot
#         reward: the array of rewards to be plot
#         file_name: the name of the figure when saved to disc
#         window_size: the size of the rolling average window
#     """
#     y = reward
#     x = range(1, len(reward) + 1)
#
#     data_dict = {"Episode": x, "Reward": y}
#     df = pd.DataFrame(data=data_dict)
#
#     df["Average Reward"] = df["Reward"].rolling(window_size).mean()
#
#     sns.set_theme(style="darkgrid")
#     plt.figure().set_figwidth(8)
#
#     sns.lineplot(data=df, x="Episode", y="Reward", alpha=0.4)
#     sns.lineplot(data=df, x="Episode", y="Average Reward")
#
#     plt.fill_between(df["Episode"], df["Reward"], df["Average Reward"], alpha=0.4)
#     plt.title(title)
#
#     dir_exists = os.path.exists("figures")
#
#     if not dir_exists:
#         os.makedirs("figures")
#
#     plt.savefig(f"figures/{file_name}")
#
#     plt.show()
#
#
# def plot_average_with_std(reward,
#                           title: str = "Cool Graph",
#                           file_name: str = "figure.png",
#                           window_size: int = 10):
#     """
#     Plot the rolling average and standard deviation. Saves the figure to figures directory
#
#     Parameters:
#         title: title of the plot
#         reward: the array of rewards to be plot
#         file_name: the name of the figure when saved to disc
#         window_size: the size of the rolling average window
#     """
#     y = reward
#     x = range(1, len(reward) + 1)
#
#     data_dict = {"Episode": x, "Reward": y}
#     df = pd.DataFrame(data=data_dict)
#
#     df["Average Reward"] = df["Reward"].rolling(window_size).mean()
#     df["Standard Deviation"] = df["Reward"].rolling(window_size).std()
#
#     sns.set_theme(style="darkgrid")
#     plt.figure().set_figwidth(8)
#
#     ax = sns.lineplot(data=df, x="Episode", y="Average Reward", label="Average Reward")
#     ax.set(xlabel="Episode", ylabel="Reward")
#     plt.fill_between(df["Episode"], df["Average Reward"] - df["Standard Deviation"], df["Average Reward"] +
#                      df["Standard Deviation"], alpha=0.4)
#
#     sns.move_legend(ax, "lower right")
#
#     plt.title(title)
#
#     dir_exists = os.path.exists("figures")
#
#     if not dir_exists:
#         os.makedirs("figures")
#
#     plt.savefig(f"figures/{file_name}")
#
#     plt.show()
#
