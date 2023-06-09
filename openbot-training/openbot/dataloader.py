# Created by Matthias Mueller - Intel Intelligent Systems Lab - 2020

import os
from typing import List
import tensorflow as tf


class dataloader:
    def __init__(self, data_dir: str, datasets: List[str]):
        self.data_dir = data_dir
        self.datasets = datasets
        self.labels = self.load_labels()
        self.index_table = self.lookup_table()
        self.label_values = tf.constant(
            [(float(label[0]), float(label[1])) for label in self.labels.values()]
        )
        self.cmd_values = tf.constant(
            [(float(label[2])) for label in self.labels.values()]
        )

    # Load labels
    def load_labels(self):
        corpus = []
        for dataset in self.datasets:
            for folder in [
                f
                for f in os.listdir(os.path.join(self.data_dir, dataset))
                if not f.startswith(".")
            ]:
                with open(
                    os.path.join(
                        self.data_dir,
                        dataset,
                        folder,
                        "sensor_data",
                        "matched_frame_ctrl_cmd_processed.txt",
                    )
                ) as f_input:
                    # discard header
                    header = f_input.readline()
                    data = f_input.read()
                    lines = (
                        data.replace(",", " ")
                        .replace("\\", "/")
                        .replace("\r", "")
                        .replace("\t", " ")
                        .split("\n")
                    )
                    data = [
                        [v.strip() for v in line.split(" ") if v.strip() != ""]
                        for line in lines
                        if len(line) > 0 and line[0] != "#"
                    ]
                    # Tuples containing id: framepath and label: throttle,steer,cmd
                    data = [(line[1], line[2:]) for line in data if len(line) > 1]
                    corpus.extend(data)
        return dict(corpus)

    # build a lookup table to get the frame index for the label
    def lookup_table(self):
        table = tf.lookup.StaticHashTable(
            initializer=tf.lookup.KeyValueTensorInitializer(
                keys=list(self.labels.keys()),
                values=list(i for i in range(len(self.labels.keys()))),
            ),
            default_value=tf.constant(-1),
            name="frame_index",
        )
        return table

    def get_label(self, file_path):
        index = self.index_table.lookup(file_path)
        return self.cmd_values[index], self.label_values[index] / 255
