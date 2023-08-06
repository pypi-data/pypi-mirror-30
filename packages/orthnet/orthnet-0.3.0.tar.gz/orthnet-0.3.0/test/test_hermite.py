import sys
sys.path.append('../../')
from OrthNet.orthnet.poly.hermite import Hermite
import tensorflow as tf
import torch
from torch.autograd import Variable
import numpy as np

N = 3
x1 = tf.placeholder(dtype = tf.float32, shape = [None, N])
l1 = Hermite('tensorflow', 2, x1)
x2 = tf.placeholder(dtype = tf.float32, shape = [None, 1])
l2 = Hermite('tensorflow', 2, x2)
with tf.Session() as sess:
	x1_data = np.linspace(-1, 1, N)
	x1_data = np.asarray([x1_data, x1_data])
	y1 = sess.run(l1.tensor, feed_dict = {x1:x1_data})
	print(sess.run(l1.get_poly(2, 2), feed_dict = {x1:x1_data}))


print(y1)
print(l1.combination)
print(l1.length)