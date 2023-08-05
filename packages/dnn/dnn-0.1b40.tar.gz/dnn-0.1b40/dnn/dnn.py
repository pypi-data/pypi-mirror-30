import tensorflow as tf
import numpy as np
import sys
import os, shutil
import random
from aquests.lib import pathtool
from . import overfit, optimizers
import sys
from functools import partial

class DNN:
    def __init__ (self, gpu_usage = 0, is_linear = False, name = None):
        self.gpu = gpu_usage        
        self.is_linear = is_linear
        self.name = name
        
        self.sess = None      
        self.in_service = True
        self.writers = {}
        self.overfitwatch = None
        
        self.summaries_dir = None
        self.verbose = True
        self.filter_func = None
        self.norm_factor = None
        self.input_standardize = False
        self.input_nornalize = False
        self.train_dir = None
        self.max_acc = 0.0
        self.accuracy_threshold = 0.0
        self.is_validating = False
        self.is_improved = False
        self.batch_size = 0
          
        self.graph = tf.Graph ()
        with self.graph.as_default ():
            self.make_default_place_holders ()
            self.make_place_holders ()
            self.logit = self.make_logit ()
            self.label = self.make_label ()
            self.saver = tf.train.Saver (tf.global_variables())
            self.temp = self.make_eval_tensor ()
    
    def  get_best_accuracy (self):
        return self.name, self.max_acc
    
    def get_norm_factor (self, verbose = False):
        if not self.norm_factor:
            return
        factor = self.norm_factor + (self.input_standardize, self.input_nornalize)
        if verbose:
            return "DNN.set_norm_factor ({:.1f}, {:.1f}, {:.1f}, {:.1f}, {}, {})\n".format (*factor)
        return factor
   
    def set_norm_factor (self, mean, std, max_, min_, standardize = True, nornalize = True):
        self.norm_factor = (mean, std, max_, min_)
        self.input_standardize = standardize
        self.input_nornalize = nornalize
            
    def normalize (self, x, standardize = True, nornalize = True):
        if self.norm_factor:
            mean, std, max_, min_ = self.norm_factor
            if self.input_standardize:
                x = (x - mean) / std
        else:    
            mean = np.mean (x)
            std = np.std (x, 0)
            if self.input_standardize:
                x = (x - mean) / std
            max_ = np.max (x)
            min_ = np.min (x)
            self.set_norm_factor (mean, std, max_, min_, standardize, nornalize)
            
        if self.input_nornalize:
            x = (x - min_) / (max_ - min_)
        return x

    def make_default_place_holders (self):    
        self.dropout_rate = tf.placeholder_with_default (tf.constant (0.0), [])
        self.is_training = tf.placeholder_with_default (tf.constant (False), [])
        self.n_sample = tf.placeholder ("int32", [])
        
        self.random_dropout_rate = tf.random_uniform ([], minval=0.1, maxval=0.7, dtype=tf.float32)
        
    def set_filter (self, func):
        self.filter_func = func
    
    def filter (self, ys, *args):
        is_no_x = True
        xs = None
        if args:
            is_no_x = False        
            xs = args [0]
             
        if self.filter_func:
            ys, xs = self.filter_func (ys, xs)
        if is_no_x:
            return ys
        return ys, xs
        
    def turn_off_verbose (self):
        self.verbose = False
            
    def init_session (self):
        if self.gpu:
            self.sess = tf.Session (graph = self.graph, config = tf.ConfigProto(gpu_options=tf.GPUOptions (per_process_gpu_memory_fraction = self.gpu), log_device_placement = False))
        else:
            self.sess = tf.Session(graph = self.graph)            
        self.sess.run (tf.global_variables_initializer())     
    
    def reset_dir (self, target):
        if os.path.exists (target):
            shutil.rmtree (target)
        if not os.path.exists (target):
            os.makedirs (target)
    
    def set_train_dir (self, path, reset = False):
        if self.name:
            path = os.path.join (path, self.name.strip ())
        self.train_dir = path        
        if reset:
            self.reset_dir (self.train_dir)
        else:
            pathtool.mkdir (self.train_dir)    
            
    def set_tensorboard_dir (self, summaries_dir, reset = True):
        self.summaries_dir = summaries_dir
        if reset:
            os.system ('killall tensorboard')
            if tf.gfile.Exists(summaries_dir):
                tf.gfile.DeleteRecursively(summaries_dir)
            tf.gfile.MakeDirs(summaries_dir)
            tf.summary.merge_all ()
                     
    def get_writers (self, *writedirs):        
        return [tf.summary.FileWriter(os.path.join (self.summaries_dir, "%s%s" % (self.name and self.name.strip () + "-" or "", wd)), self.sess.graph) for wd in writedirs]
    
    def make_writers (self, *writedirs):
        for i, w in enumerate (self.get_writers (*writedirs)):
            self.writers [writedirs [i]] = w
    
    def get_epoch (self):
        with self.sess.as_default ():
            return self.global_step.eval ()
                
    def write_summary (self, writer, feed_dict, verbose = True):
        if writer not in self.writers:
            return
        
        summary = tf.Summary()
        output = []
        for k, v in feed_dict.items ():
            if self.name:
                k = "{}:{}".format (self.name, k)
            summary.value.add(tag = k , simple_value = v)
            if isinstance (v, (float, np.float64, np.float32)):
                output.append ("{} {:.7f}".format (k, v))
            elif isinstance (v, (int, np.int64, np.int32)):
                output.append ("{} {:04d}".format (k, v))    
            else:
                output.append ("{} {}".format (k, v))        
            
        if self.is_overfit ():
            output.append ("!Overfitted")
        if self.is_improved:
            output.append ("*Improved")
            self.is_improved = False
            
        epoch = self.get_epoch ()
        self.writers [writer].add_summary(summary, epoch)
        if verbose and self.verbose:
            print ("[%d:%7s] %s" % (epoch, writer, " | ".join (output)))
        
    def restore (self):
        if self.name:
            path = os.path.join (self.train_dir, self.name.strip ())        

        with self.graph.as_default ():
            self.init_session ()
            self.saver.restore(self.sess, tf.train.latest_checkpoint(self.train_dir))
        
    def save (self, filename):
        path = os.path.join (self.train_dir, filename)
        with self.graph.as_default ():
            self.saver.save (self.sess, path, global_step = self.global_step)
    
    def get_latest (self, path):    
        if not os.listdir (path):
            return 0
        return max ([int (ver) for ver in os.listdir (path) if ver.isdigit () and os.path.isdir (os.path.join (path, ver))])    

    def export (self, path, predict_def, inputs, outputs):
        if self.name:
            path = os.path.join (path, self.name.strip ())
        pathtool.mkdir (path)
        version = self.get_latest (path) + 1
        
        with self.graph.as_default ():            
            builder = tf.saved_model.builder.SavedModelBuilder("{}/{}/".format (path, version))
            prediction_signature = (
              tf.saved_model.signature_def_utils.build_signature_def(
                  inputs=dict ([(k, tf.saved_model.utils.build_tensor_info (v)) for k,v in inputs.items ()]),
                  outputs=dict ([(k, tf.saved_model.utils.build_tensor_info (v)) for k,v in outputs.items ()]),
                  method_name=tf.saved_model.signature_constants.PREDICT_METHOD_NAME))
            
            builder.add_meta_graph_and_variables(
              self.sess, [tf.saved_model.tag_constants.SERVING],
              signature_def_map = {
                  predict_def: prediction_signature
              }
            )
            builder.save()
        return version    
            
    def get_best_cost (self):
        return overfitwatch.min_cost
    
    def is_overfit (self):
        return self.overfitwatch.is_overfit ()
        
    def maybe_save_checkpoint (self, acc):
        if acc < self.accuracy_threshold:
            return        
        
        save = False
        if acc > self.max_acc:
            self.max_acc = acc
            save = True
        #elif self.overfitwatch.is_renewaled ():
            #save = True
        if save:
            self.is_improved = True
            self.save ("acc-%.7f+cost-%.7f" % (acc, self.overfitwatch.latest_cost))    
            
    def eval (self, tensor):
        with self.sess.as_default ():
            return tensor.eval ()
                
    # make trainable ----------------------------------------------------------
    def trainable (self, start_learning_rate=0.00001, decay_step=3000, decay_rate=0.99, overfit_threshold = 0.02, accuracy_threshold = 0.0):
        self.in_service = False
        self.overfitwatch = overfit.Overfit (overfit_threshold)
        self.accuracy_threshold = accuracy_threshold
        
        self.start_learning_rate = start_learning_rate
        self.decay_step = decay_step
        self.decay_rate = decay_rate
        
        with self.graph.as_default ():
            self.global_step = tf.Variable (0, trainable=False)
            self.learning_rate = tf.train.exponential_decay (self.start_learning_rate, self.global_step, self.decay_step, self.decay_rate, staircase=False)            
            self.cost = self.make_cost ()        
            try:
                self.accuracy = self.calculate_accuracy ()
            except TypeError:
                # custom
                self.accuracy = tf.constant (0.0)    
            self.update_ops = tf.get_collection (tf.GraphKeys.UPDATE_OPS)
            with tf.control_dependencies (self.update_ops):                
                self.train_op = self.make_optimizer ()
            self.init_session ()
    
    def run (self, *ops, **kargs):  
        if "y" in kargs:
            kargs ["y"], kargs ["x"] = self.filter (kargs ["y"], kargs ["x"])
            kargs ["n_sample"] = len (kargs ["y"])
        
        if self.norm_factor and self.in_service and "x" in kargs:
            kargs ["x"] = self.normalize (kargs ["x"])
        
        feed_dict = {}
        for k, v in kargs.items ():
            feed_dict [getattr (self, k)] = v
        
        result = self.sess.run (ops, feed_dict = feed_dict)
        return result
    
    def evaluate (self, x, y, is_training, *args, **kargs):
        class Result:
            def __init__ (self, x, y, is_training, accfunc, logit, cost, acc):
                self.__x = x
                self.__y = y
                self.__is_training = is_training
                self.__accfunc = accfunc
                
                self.logit = logit
                self.cost = cost
                self.accuracy = acc
            
            def update (self, *args, **karg): 
                self.accuracy = self.__accfunc (self.logit, self.__y, *args, **karg)

        logits = []
        costs = []
        accs = []
        for i in range (0, len (x), self.batch_size):
            x_ = x [i:i + self.batch_size]
            y_ = y [i:i + self.batch_size]            
            logit, cost, acc =  self.run (self.logit, self.cost, self.accuracy, x = x_, y = y_, dropout_rate = 0.0, is_training = is_training, **kargs)
            logits.append (logit)
            costs.append (cost)
            accs.append (acc)
        
        result = Result (
            x, y, is_training, self.custom_accuracy,
            np.concatenate(logits, 0),
            np.mean (costs), 
            np.mean (accs)
        )
        return result
    
    def fit (self, x, y, **kargs):
        self.batch_size = len (x)
        r = self.run (self.train_op, self.learning_rate, x = x, y = y, is_training = True, **kargs)
        return r [1:]
        
    def train (self, x, y, **kargs):
        return self.evaluate (x, y, True, **kargs)
        
    def valid (self, x, y, **kargs):
        r = self.evaluate (x, y, False, **kargs)        
        self.overfitwatch.add_cost (r.cost)
        self.is_validating = True
        if r.accuracy:
            self.maybe_save_checkpoint (r.accuracy)
        return r
        
    # layering -------------------------------------------------------------------
    def dropout (self, layer, dropout = True, activation = None):
        if activation is not None:
           layer = activation (layer)
        if self.in_service or not dropout:
            return layer
        dr = tf.where (tf.less (self.dropout_rate, 0.0), self.random_dropout_rate, self.dropout_rate)
        return tf.layers.dropout (inputs=layer, rate = dr, training = self.is_training)
        
    def lstm_with_dropout (self, n_input, hidden_size, lstm_layers = 1, activation = None, dynamic = True):
        return self.lstm (n_input, hidden_size, lstm_layers, activation, dynamic, dropout = True)
        
    def lstm (self, n_input, hidden_size, lstm_layers = 1, activation = None, dynamic = True, dropout = False):
        try:
            rnn = tf.nn.rnn_cell
            type_rnn = dynamic and tf.nn.dynamic_rnn or tf.nn.static_rnn                    
        except AttributeError:
            rnn = tf.contrib.rnn
            type_rnn = dynamic and rnn.dynamic_rnn or rnn.static_rnn
        
        cells = []
        for i in range (lstm_layers):
            lstm = rnn.BasicLSTMCell (hidden_size, activation = activation)
            if dropout:
                lstm = rnn.DropoutWrapper (lstm, output_keep_prob = 1.0 - self.dropout_rate)
            cells.append (lstm)
            
        cell = rnn.MultiRNNCell (cells)
        initial_state = cell.zero_state (self.n_sample, tf.float32)
        
        # transform time major form      
        shape = len (n_input.get_shape())
        lstm_in = tf.transpose (n_input, [1, 0] + list (range (max (2, shape - 2), shape)))
        if dynamic:            
            output, final_state = type_rnn (cell, lstm_in, time_major = True, dtype = tf.float32, initial_state = initial_state)
        else:
            seq_len = shape [1]
            n_channel = len (shape) >= 3 and shape [2] or 0
            if n_channel:
                lstm_in = tf.reshape (lstm_in, [-1, n_channel])
            lstm_in = tf.layers.dense (lstm_in, hidden_size)
            lstm_in = tf.split (lstm_in, seq_len, 0)
            output, final_state = type_rnn (cell, lstm_in, dtype = tf.float32, initial_state = initial_state)
                
        return output
    
    def full_connect (self, tensor):
        n_output = 1
        for d in tensor.get_shape ()[1:]:
            n_output *= int (d)
        return tf.reshape (tensor, [-1, n_output])
    
    def sequencial_connect (self, tensor, seq_len, n_output):
        # outputs is rnn outputs
        fc = self.full_connect (tensor)
        outputs = tf.layers.dense (fc, n_output, activation = None)
        return tf.reshape (outputs, [self.n_sample, seq_len, n_output])
    
    def batch_norm (self, n_input, activation = None, momentum = 0.99, center = True, scale = True):
        layer = tf.layers.batch_normalization (n_input, momentum = momentum, training = self.is_training, center = center, scale = scale)
        if activation is not None:
           return activation (layer)
        return layer
    
    def batch_norm_with_dropout (self, n_input, activation = None, momentum = 0.99, center = True, scale = True):
       layer = self.batch_norm (n_input, activation, momentum, center = center, scale = scale)
       return self.dropout (layer) 
   
    def dense (self, n_input, n_output, activation = None):
        return tf.layers.dense (inputs = n_input, units = n_output, activation = activation)
        
    def conv1d (self, n_input, filters, kernel = 2, strides = 1, activation = None,  padding = "same"):
        return tf.layers.conv1d (inputs = n_input, filters = filters, kernel_size = kernel, strides = strides, padding = padding, activation = activation)
    
    def max_pool1d (self, n_input, pool = 2, strides = 2, padding = "same"):
        return tf.layers.max_pooling1d (inputs = n_input, pool_size = pool, strides = strides, padding = padding)
    
    def avg_pool1d (self, n_input, pool = 2, strides = 2, padding = "same"):
        return tf.layers.average_pooling1d (inputs = n_input, pool_size = pool, strides = strides, padding = padding)
    
    def conv2d (self, n_input, filters, kernel = (4, 4), activation = None, padding = "same"):
        return tf.layers.conv2d (inputs = n_input, filters = filters, kernel_size = kernel, strides = strides, padding = padding, activation = activation)
    
    def max_pool2d (self, n_input, pool = (2, 2), strides = 2, padding = "same"):
        return tf.layers.max_pooling2d (inputs = n_input, pool_size = pool, strides = strides, padding = padding)
    
    def avg_pool2d (self, n_input, pool = (2, 2), strides = 2, padding = "same"):
        return tf.layers.average_pooling2d (inputs = n_input, pool_size = pool, strides = strides, padding = padding)
    
    def conv3d (self, n_input, filters, kernel = (4, 4, 4), activation = None, padding = "same"):
        return tf.layers.conv3d (inputs = n_input, filters = filters, kernel_size = kernel, strides = strides, padding = padding, activation = activation)
    
    def max_pool3d (self, n_input, pool = (2, 2, 2), strides = 2, padding = "same"):
        return tf.layers.max_pooling3d (inputs = n_input, pool_size = pool, strides = strides, padding = padding)
    
    def avg_pool3d (self, n_input, pool = (2, 2, 2), strides = 2, padding = "same"):
        return tf.layers.average_pooling3d (inputs = n_input, pool_size = pool, strides = strides, padding = padding)
        
    # helpers ------------------------------------------------------------------
    def swish (self, x):
        return tf.nn.sigmoid (x) * x
    
    def optimizer (self, name = 'adam', *args, **karg):
        return getattr (optimizers, name) (self.cost, self.learning_rate, self.global_step, *args, **karg)
    
    # override theses ----------------------------------------------------------            
    def make_eval_tensor (self):
        return tf.random_uniform ([], minval=0.1, maxval=0.7, dtype=tf.float32)
    
    def make_place_holders (self):
        self.x = tf.placeholder ("float", [None, n_input])
        self.y = tf.placeholder ("float", [None, n_output])
            
    def make_optimizer (self):
        return self.optimizer ("adam")    
    
    def make_label (self):
        return self.logit
    
    def make_logit (self):
        return self.dense (self.x, 1)
    
    def make_cost (self):
        return tf.constant (0.0)
     
    def calculate_accuracy (self):
        raise NotImplemented
        
    def custom_accuracy (self, logit, y, *args, **karg):
        acc = self.calculate_accuracy (logit, self.filter (y), *args, **karg)
        if self.is_validating:
            self.maybe_save_checkpoint (acc)
            self.is_validating = False
        return acc
        
        