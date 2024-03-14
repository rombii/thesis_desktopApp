import os
import sys

import tensorflow as tf

if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

encoder_path = os.path.join(base_path)

def get_embedding(sentences):
    # Load the Universal Sentence Encoder model
    use_model_url = encoder_path
    embed = tf.saved_model.load(use_model_url)

    # Get embeddings for the sentences
    embeddings = embed(sentences)

    # Return the embeddings without reshaping
    return embeddings


def conditioning_augmentation(x):
    mean = x[:, :128]
    log_sigma = x[:, 128:]

    stddev = tf.math.exp(log_sigma)
    epsilon = tf.keras.backend.random_normal(shape=tf.keras.backend.shape(mean.shape[1], ), dtype='float')
    c = mean + stddev * epsilon
    return c

