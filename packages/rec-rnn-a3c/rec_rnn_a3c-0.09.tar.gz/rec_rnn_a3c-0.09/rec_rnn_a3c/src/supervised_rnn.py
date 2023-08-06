import numpy as np
import tensorflow as tf
from tensorflow.contrib import slim

from rec_rnn_a3c.src.embedding import BloomEmbedding
from rec_rnn_a3c.src.util import normalized_columns_initializer


def length(sequence):
    used = tf.sign(tf.abs(sequence))
    length = tf.reduce_sum(used, 1)
    length = tf.cast(length, tf.int32)
    return length

class SupervisedRNN(object):
    def __init__(self, optimizer, params, scope):
        # TODO: Make parameter
        self.scope = scope

        with tf.variable_scope(self.scope):
            self.optimizer = optimizer

            self.item_dim = params['item_dim']
            self.output_dim = params['output_dim']
            self.hidden_dim = params['hidden_dim']
            self.batch_dim = params['batch_dim']

            self.input = tf.placeholder(tf.int32, shape=[None, None], name='input')
            with tf.device("/cpu:0"):

                E = tf.get_variable(name="E", shape=[self.item_dim, self.hidden_dim])
                input = tf.nn.embedding_lookup(params=E, ids=self.input)

            self.length = length(self.input)

            rnn_cell = tf.nn.rnn_cell.BasicLSTMCell(num_units=self.hidden_dim, state_is_tuple=True)
            rnn_cell = tf.nn.rnn_cell.DropoutWrapper(rnn_cell, output_keep_prob=0.5)

            c_init = np.zeros((self.batch_dim, rnn_cell.state_size.c), np.float32)
            h_init = np.zeros((self.batch_dim, rnn_cell.state_size.h), np.float32)
            self.rnn_zero_state = [c_init, h_init]

            self.c_input = tf.placeholder(tf.float32, [None, rnn_cell.state_size.c], name='c_input')
            self.h_input = tf.placeholder(tf.float32, [None, rnn_cell.state_size.h], name='h_input')
            state_input = tf.nn.rnn_cell.LSTMStateTuple(self.c_input, self.h_input)

            rnn_output, (rnn_c, rnn_h) = tf.nn.dynamic_rnn(
                inputs=input,
                cell=rnn_cell,
                dtype=tf.float32,
                initial_state=state_input,
                sequence_length=self.length)

            self.output_shape = output_shape = tf.shape(rnn_output)

            self.state_output = (rnn_c, rnn_h)

            """
            self.action_logit_dist = slim.fully_connected(
                inputs=rnn_output,
                num_outputs=self.item_dim,
                activation_fn=None,
                weights_initializer=normalized_columns_initializer(0.01),
                biases_initializer=None
            )
            self.logit_dist = tf.reshape(self.action_logit_dist, [self.batch_dim, -1, self.output_dim])
            self.prob_dist = tf.nn.softmax(self.action_logit_dist)
            """
            self.labels = tf.placeholder(tf.int32, [None, None], name='target')
            """
            self.loss = tf.contrib.seq2seq.sequence_loss(
                logits=self.action_logit_dist,
                targets=self.labels,
                weights=tf.ones(shape=shape),
                average_across_timesteps=False,
                average_across_batch=True,
            )
            """
            with tf.device("/cpu:0"):
                #self.w = tf.get_variable("w", [self.item_dim, self.hidden_dim], dtype=tf.float32)
                self.b = tf.get_variable("b", [self.item_dim], dtype=tf.float32)

            self.loss = tf.nn.sampled_softmax_loss(
                weights=E,
                biases=self.b,
                labels=tf.reshape(self.labels, [-1, 1]),
                inputs=tf.reshape(rnn_output, [-1, self.hidden_dim]),
                num_sampled=5,
                num_classes=self.item_dim)

            self.loss = tf.reshape(self.loss, [output_shape[0], output_shape[1]])
            self.loss = tf.reduce_mean(self.loss, axis=0)
            self.loss = tf.reduce_sum(self.loss)

            self.test1 = self.logit_dist = tf.matmul(tf.reshape(rnn_output, [-1, self.hidden_dim]), E, transpose_b=True)
            self.test2 = self.logit_dist = tf.nn.bias_add(self.logit_dist, self.b)
            self.logit_dist = tf.reshape(self.logit_dist, [output_shape[0], output_shape[1], self.item_dim])
            self.prob_dist = tf.nn.softmax(self.logit_dist)

            trainable_vars = tf.trainable_variables()
            grads, _ = tf.clip_by_global_norm(tf.gradients(self.loss, trainable_vars), 40.0)
            self.optimizer = tf.train.AdamOptimizer(0.001)
            self.train_op = self.optimizer.apply_gradients(zip(grads, trainable_vars))


class SupervisedBloomRNN(object):
    def __init__(self, optimizer, params, scope):
        self.scope = scope

        with tf.variable_scope(self.scope):
            self.optimizer = optimizer

            self.item_dim = params['item_dim']
            self.output_dim = params['output_dim']
            self.hidden_dim = params['hidden_dim']
            self.batch_dim = params['batch_dim']
            self.unfold_dim = params['unfold_dim']
            self.embedding_dim = params['embedding_dim']
            self.compression_ratio = params['compression_ratio']
            self.num_hash_funcs = params['num_hash_funcs']

            bloom_embedding = BloomEmbedding(
                num_embeddings=self.item_dim,
                compression_ratio=self.compression_ratio,
                num_hash_functions=self.num_hash_funcs)

            self.to_embed = tf.placeholder(dtype=tf.int64, shape=[None, None])
            self.bloom_embedded_tensor = bloom_embedding.forward(self.to_embed)


            self.input = tf.placeholder(tf.int32, shape=[None, None], name='input')
            ####### Bloom Embeddings #######
            with tf.device("/cpu:0"):
                self.hashed_input = bloom_embedding.forward(self.input)
                #TODO: Is this correct?
                E_i = tf.get_variable(name="input_embeddings", shape=[self.embedding_dim, self.hidden_dim])
                input = tf.nn.embedding_lookup(params=E_i, ids=self.hashed_input)
            input = tf.reduce_sum(input, axis=2)


            """
            self.input = tf.placeholder(tf.int32, shape=[None, None], name='input')
            E = tf.get_variable(name="E", shape=[self.item_dim, self.hidden_dim])
            input = tf.nn.embedding_lookup(params=E, ids=self.input)
            """

            ####### RNN Cells #######
            rnn_cell = tf.nn.rnn_cell.BasicLSTMCell(num_units=self.hidden_dim, state_is_tuple=True)
            rnn_cell = tf.nn.rnn_cell.DropoutWrapper(rnn_cell, output_keep_prob=0.5)

            c_init = np.zeros((self.batch_dim, rnn_cell.state_size.c), np.float32)
            h_init = np.zeros((self.batch_dim, rnn_cell.state_size.h), np.float32)
            self.rnn_zero_state = [c_init, h_init]

            self.c_input = tf.placeholder(tf.float32, [None, rnn_cell.state_size.c], name='c_input')
            self.h_input = tf.placeholder(tf.float32, [None, rnn_cell.state_size.h], name='h_input')
            state_input = tf.nn.rnn_cell.LSTMStateTuple(self.c_input, self.h_input)

            self.length = length(self.input)

            rnn_output, (rnn_c, rnn_h) = tf.nn.dynamic_rnn(
                inputs=input,
                cell=rnn_cell,
                dtype=tf.float32,
                initial_state=state_input,
                sequence_length=self.length
            )

            self.state_output = (rnn_c, rnn_h)

            self.logit_dist = slim.fully_connected(
                inputs=rnn_output,
                num_outputs=self.embedding_dim,
                activation_fn=None,
                weights_initializer=normalized_columns_initializer(0.01),
                biases_initializer=None
            )
            self.prob_dist = tf.nn.softmax(self.logit_dist)
            self.sigmoids = tf.nn.sigmoid(self.logit_dist)

            ####### Likelihoods with target sequence index #######
            self.target_index = tf.placeholder(dtype=tf.int32)
            target_sigmoids = self.sigmoids[:, self.target_index, :]

            self.hashed_indices = hashed_indices = bloom_embedding.forward(tf.range(self.item_dim))
            self.hashed_likelihoods = hashed_likelihoods = tf.gather(
                params=target_sigmoids,
                indices=hashed_indices,
                axis=1)
            self.likelihoods = tf.reduce_prod(hashed_likelihoods, axis=2)
            self.predictions = tf.argmax(self.likelihoods, axis=1)

            ###### Likelihoods with target action index ########
            self.target_action_index = tf.placeholder(dtype=tf.int32, shape=[None, None])
            self.hashed_action_indices = bloom_embedding.forward(self.target_action_index)
            self.hashed_action_likelihoods = tf.gather(
                params=self.sigmoids,
                indices=self.hashed_action_indices,
                #axis=1
            )
            self.action_likelihood = tf.reduce_prod(self.hashed_action_likelihoods, axis=2)


            ###### Labels ########
            self.labels = tf.placeholder(tf.int32, [None, None], name='target')

            self.hashed_labels = bloom_embedding.forward(self.labels)
            self.hashed_labels = tf.one_hot(self.hashed_labels, self.embedding_dim, axis=2)
            self.hashed_labels = tf.reduce_sum(self.hashed_labels, axis=3)

            ####### Loss #######
            self.output_loss = self.loss = tf.nn.sigmoid_cross_entropy_with_logits(
                logits=self.logit_dist,
                labels=self.hashed_labels
            )
            """
            self.loss = tf.keras.backend.binary_crossentropy(
                target=self.hashed_labels,
                output=self.logit_dist,
                from_logits=True
            )
            """
            self.loss = tf.reduce_mean(self.loss, axis=0)
            self.loss = tf.reduce_sum(self.loss)

            tf.summary.scalar('loss', self.loss)

            trainable_vars = tf.trainable_variables()
            grads, _ = tf.clip_by_global_norm(tf.gradients(self.loss, trainable_vars), 40.0)
            self.optimizer = tf.train.AdamOptimizer(0.001)
            self.train_op = self.optimizer.apply_gradients(zip(grads, trainable_vars))