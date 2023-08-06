import numpy as np
import tensorflow as tf
import time
from rec_rnn_a3c.src.supervised_rnn import SupervisedBloomRNN, SupervisedRNN

tf.logging.set_verbosity(tf.logging.INFO)


class SupervisedRNNModel(object):
    def __init__(self, optimizer, params, scope='supervised_rnn'):
        self.optimizer = optimizer

        self.params = params

        self.unfold_dim = params['unfold_dim']
        self.item_dim = params['item_dim']

        #self.reward_network = SupervisedBloomRNN(optimizer=optimizer, params=params, scope=scope)
        self.reward_network = SupervisedRNN(optimizer=optimizer, params=params, scope=scope)
        rnn_state_c, rnn_state_h = self.reward_network.rnn_zero_state
        self.rnn_state_c = rnn_state_c
        self.rnn_state_h = rnn_state_h

        self.files = tf.placeholder(tf.string, shape=[None], name='files')

        self.merged_summary = tf.summary.merge_all()

    def predict(self, seq, sess, num_predictions=1):
        print("Checkpoint 1")
        seq_len = len(seq)

        rnn_state_c, rnn_state_h = self.reward_network.rnn_zero_state
        rnn_state_c = rnn_state_c[:1, :]
        rnn_state_h = rnn_state_h[:1, :]

        diff = self.unfold_dim - seq_len
        if diff < 0:
            seq = seq[-diff:]
        elif diff > 0:
            seq += [0 for _ in range(self.unfold_dim - seq_len)]

        seq = map(int, seq)
        seq = np.expand_dims(seq, axis=0)

        feed_dict = {
            self.reward_network.input: seq,
            self.reward_network.c_input: rnn_state_c,
            self.reward_network.h_input: rnn_state_h,
            self.reward_network.target_index: seq_len - 1
        }

        fetches = [self.reward_network.partial_prob_dist]
        predictions = []

        for i in range(0, num_predictions):
            probs = sess.run(feed_dict=feed_dict, fetches=fetches)
            probs = np.reshape(probs, [-1, self.item_dim])

            #sorted_probs = np.sort(probs, axis=1)[0][::-1]

            prediction_ = np.argmax(probs, axis=1)
            print(prediction_)
            seq[0, seq_len + i] = i+2
            seq_len += 1

            feed_dict = {
                self.reward_network.input: seq,
                self.reward_network.c_input: rnn_state_c,
                self.reward_network.h_input: rnn_state_h,
                self.reward_network.target_index: seq_len - 1
            }

            predictions.append(prediction_)

        return np.reshape(predictions, [-1])

    def eval(self, sess, iterator):
        next_element = iterator.get_next()

        total_loss = 0.0
        total_steps = 0
        while True:
            try:
                total_steps += 1
                step_loss = 0.0
                sequence, label_sequence = sess.run(next_element)

                num_sequence_splits = np.max([1, np.shape(sequence)[1] // self.unfold_dim])

                for split in range(num_sequence_splits):
                    seq_split = sequence[:, split * self.unfold_dim:(split + 1) * self.unfold_dim]
                    label_seq_split = label_sequence[:, split * self.unfold_dim:(split + 1) * self.unfold_dim]

                    batch_size = np.shape(seq_split)[0]


                    rnn_state_c, rnn_state_h = self.reward_network.rnn_zero_state
                    rnn_state_c = rnn_state_c[:batch_size, :]
                    rnn_state_h = rnn_state_h[:batch_size, :]


                    feed_dict = {
                        self.reward_network.input: seq_split,
                        self.reward_network.c_input: rnn_state_c,
                        self.reward_network.h_input: rnn_state_h,
                        self.reward_network.labels: label_seq_split
                    }

                    fetches = [
                        self.reward_network.state_output,
                        self.reward_network.loss,
                    ]

                    (self.rnn_state_c, self.rnn_state_h), loss = sess.run(
                        feed_dict=feed_dict,
                        fetches=fetches
                    )

                    step_loss += loss

                total_loss += step_loss / num_sequence_splits
            except tf.errors.OutOfRangeError:
                break

        tf.logging.info("Evaluation -- Error: %s " % (total_loss / total_steps))

    def fit(self, sess, iterator, iteration, num_iterations, step, num_steps, saver=None, save_path=None):
        #train_writer = tf.summary.FileWriter(save_path + '/train', sess.graph)

        next_element = iterator.get_next()

        total_loss = 0.0
        time_deltas = 0.0
        for current_step in range(step, num_steps):
            start = time.time()
            try:
                step_loss = 0.0
                # TODO: Possible without feeding? (Improves performance)
                sequence, label_sequence = sess.run(next_element)

                # TODO: Reset states?
                #self.rnn_state_c, self.rnn_state_h = self.reward_network.rnn_zero_state

                num_sequence_splits = np.max([1, np.shape(sequence)[1] // self.unfold_dim])

                for split in range(num_sequence_splits):
                    seq_split = sequence[:, split * self.unfold_dim:(split + 1) * self.unfold_dim]
                    label_seq_split = label_sequence[:, split * self.unfold_dim:(split + 1) * self.unfold_dim]

                    batch_size = np.shape(seq_split)[0]

                    rnn_state_c, rnn_state_h = self.reward_network.rnn_zero_state
                    rnn_state_c = rnn_state_c[:batch_size, :]
                    rnn_state_h = rnn_state_h[:batch_size, :]

                    feed_dict = {
                        self.reward_network.input: seq_split,
                        self.reward_network.c_input: rnn_state_c,
                        self.reward_network.h_input: rnn_state_h,
                        self.reward_network.labels: label_seq_split
                    }

                    fetches = [
                        self.reward_network.state_output,
                        self.reward_network.loss,
                        self.reward_network.train_op,
                    ]

                    (self.rnn_state_c, self.rnn_state_h), loss, _ = sess.run(
                        feed_dict=feed_dict,
                        fetches=fetches
                    )
                    step_loss += loss

                total_loss += step_loss / num_sequence_splits
            except tf.errors.OutOfRangeError:
                break
            end = time.time()

            time_delta = end - start
            time_deltas += time_delta

            tf.logging.info(
                "Episode [%d/%d] -- Step [%d/%d] -- Error: %s -- Average Time: %3f secs"
                % (iteration, num_iterations, current_step, num_steps, total_loss / (current_step + 1), time_deltas / (current_step + 1)))

            #summary, _ = sess.run([self.merged_summary, self.reward_network.loss], feed_dict=feed_dict)
            #train_writer.add_summary(summary, iteration * num_steps + step)

            if saver and save_path and current_step % 100 == 0 and False:
                saver.save(sess, save_path, global_step=iteration * num_steps + current_step)
                tf.logging.info("Saved model to: %s" % save_path)
