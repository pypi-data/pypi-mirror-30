import sys
sys.path.append('../../')
from OrthNet.orthnet.poly.jacobi import Jacobi
from OrthNet.orthnet.poly.legendre import Legendre
import tensorflow as tf
import torch
from torch.autograd import Variable
import numpy as np

N = 3
x1 = tf.placeholder(dtype = tf.float32, shape = [None, N])
l1 = Jacobi('tensorflow', 2, x1, 0, 0)
l2 = Legendre('tensorflow', 2, x1)

with tf.Session() as sess:
	x1_data = np.linspace(-1, 1, N)
	x1_data = np.asarray([x1_data, x1_data])
	y1 = sess.run(l1.tensor, feed_dict = {x1:x1_data})
	y2 = sess.run(l2.tensor, feed_dict = {x1:x1_data})


print(y1)
print(y2)