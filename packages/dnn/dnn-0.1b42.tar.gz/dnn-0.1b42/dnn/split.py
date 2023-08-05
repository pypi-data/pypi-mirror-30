import numpy as np
from sklearn.model_selection import train_test_split
import random

def split (total_xs, total_ys, test_size = 500):
    train_xs, test_xs, train_ys, test_ys = train_test_split(total_xs, total_ys, test_size = test_size, random_state = random.randrange (100))
    return train_xs, test_xs, train_ys, test_ys

def resample (batch_xs, batch_ys, sample_size = 500):
    sample_xs, sample_ys = [], []     
    for idx in np.random.permutation(len(batch_ys))[:sample_size]:
        sample_xs.append (batch_xs [idx])
        sample_ys.append (batch_ys [idx])        
    return np.array (sample_xs), np.array (sample_ys)

def minibatch (train_xs, train_ys, batch_size = 0):
    while 1:
        if not batch_size:
            yield train_xs, train_ys
        else:  
            pos = 0
            batch_indexes = np.random.permutation(len(train_xs))
            while 1:
                batch_xs = []
                batch_ys = []
                while 1:
                    try:
                        idx = batch_indexes [pos]
                    except IndexError:
                        pos = 0
                        batch_indexes = np.random.permutation(len(train_xs))
                        idx = batch_indexes [0]
                    batch_xs.append (train_xs [idx])
                    batch_ys.append (train_ys [idx])
                    pos += 1                    
                    if len (batch_xs) == batch_size:
                        break
                yield np.array (batch_xs), np.array (batch_ys)
    