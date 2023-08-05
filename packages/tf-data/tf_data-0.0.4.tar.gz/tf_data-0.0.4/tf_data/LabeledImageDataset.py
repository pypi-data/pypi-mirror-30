import tensorflow as tf
import numpy as np
from tf_data.ImagePatches import ImagePatches


class LabeledImagePlaceholder:
    def __init__(self, info, patch_size=None):
        self.info = info
        self._position = 0

        self.image_flat = tf.placeholder(tf.float32, [None, np.prod(self.info.dim_image)])
        self.label = tf.placeholder(tf.int32, [None, 1])
        self.image = tf.reshape(self.image_flat, [-1] + self.info.dim_image)
        self.label_one_hot = tf.one_hot(self.label, self.info.label_count)

        if patch_size:
            self.patches = ImagePatches(self.image, patch_size, self.info.color_channels)

    def train(self, batch_size=40):
        p = self._position
        self._position += batch_size

        labels = self.info.raw_data['train_labels'][p:p + batch_size]
        images = self.info.raw_data['train_data'][p:p + batch_size]
        images = np.reshape(images, (-1, np.prod(self.info.dim_image)))

        return {self.image_flat: self.info.map_data(images), self.label: self.info.map_labels(labels)}

    def test(self, splits=1):
        labels = self.info.raw_data['test_labels']
        images = self.info.raw_data['test_data']
        images = np.reshape(images, (-1, np.prod(self.info.dim_image)))

        images_split = np.split(images, splits)
        labels_split = np.split(labels, splits)
        results = [{
            self.image_flat: self.info.map_data(images_split[i]),
            self.label: self.info.map_labels(labels_split[i])
        } for i in range(splits)]

        return results[0] if splits == 1 else results


class LabeledImageDataset:
    def __init__(self, width, height, color_channels, label_count, file, map_data=None, map_labels=None):
        self.raw_file = file
        self.raw_data = np.load(file)
        self.map_data = map_data or (lambda x: x)
        self.map_labels = map_labels or (lambda x: x)
        self.dim_image = [width, height, color_channels]

        self.width = width
        self.height = height
        self.label_count = label_count
        self.color_channels = color_channels
        self.placeholder = lambda: LabeledImagePlaceholder(self)
