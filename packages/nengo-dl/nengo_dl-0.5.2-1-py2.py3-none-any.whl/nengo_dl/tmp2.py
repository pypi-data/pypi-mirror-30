import sys
import os
from urllib.request import urlopen
import io

import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
import tensorflow.contrib.slim as slim
import scipy

import nengo
import nengo_dl

sys.path.append(r"D:\Documents\tensorflow_models\slim")
from datasets import dataset_utils, imagenet
from nets import inception
from preprocessing import inception_preprocessing

checkpoints_dir = '/tmp/checkpoints'
image_shape = (740, 1024, 3)
input_shape = inception.inception_v1.default_image_size

class InceptionNode(object):
    def pre_build(self, shape_in, shape_out):
        # download model checkpoint file
        if not tf.gfile.Exists(checkpoints_dir):
            tf.gfile.MakeDirs(checkpoints_dir)

        url = "http://download.tensorflow.org/models/inception_v1_2016_08_28.tar.gz"
        dataset_utils.download_and_uncompress_tarball(url, checkpoints_dir)

    def __call__(self, t, x):
        image = tf.reshape(tf.cast(x, tf.uint8), image_shape)

        processed_image = inception_preprocessing.preprocess_image(
            image, input_shape, input_shape, is_training=False)
        processed_images = tf.expand_dims(processed_image, 0)

        # create model
        with slim.arg_scope(inception.inception_v1_arg_scope()):
            logits, _ = inception.inception_v1(processed_images,
                                               num_classes=1001,
                                               is_training=False)
        probabilities = tf.nn.softmax(logits)

        return probabilities

# load images
url = 'https://upload.wikimedia.org/wikipedia/commons/7/70/EnglishCockerSpaniel_simon.jpg'
image_string = urlopen(url).read()
image = scipy.ndimage.imread(io.BytesIO(image_string))

with nengo.Network() as net:
    input = nengo.Node(output=image.flatten())

    incep_node = nengo_dl.TensorNode(
        InceptionNode(), size_in=np.prod(image_shape), size_out=1001)
    nengo.Connection(input, incep_node, synapse=None)

    input_p = nengo.Probe(input)
    p = nengo.Probe(incep_node)

with nengo_dl.Simulator(net) as sim:

    with sim.tensor_graph.graph.as_default():
        # load checkpoint
        init_fn = slim.assign_from_checkpoint_fn(
            os.path.join(checkpoints_dir, 'inception_v1.ckpt'),
            slim.get_model_variables('InceptionV1'))
    init_fn(sim.sess)

    sim.step()

probabilities = sim.data[p][0]
sorted_inds = [i[0] for i in
               sorted(enumerate(-probabilities), key=lambda x: x[1])]

print(probabilities.shape, probabilities)

names = imagenet.create_readable_names_for_imagenet_labels()
for i in range(5):
    index = sorted_inds[i]
    print('Probability %0.2f%% => [%s]' % (
    probabilities[index] * 100, names[index]))

plt.figure()
plt.imshow(sim.data[input_p][0].reshape(image_shape).astype(np.uint8))
plt.axis('off')
plt.show()
