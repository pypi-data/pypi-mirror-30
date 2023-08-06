import sys
sys.path.append('..')
from orthnet import Laguerre, Legendre, Legendre_Normalized, Chebyshev, Chebyshev2, Hermite, Hermite2, Jacobi
import numpy as np
import tensorflow as tf
import torch


def integral(f1, f2, x, weight):
	"""
	compute numerical integration with f1, f2, weight, and x

	input:
		f1, f2: vectors of function values
		x: points for integration 
		weight: the weight function
	"""
	return np.trapz(f1*f2*weight(x), x = x)

def test(degree, x, y, weight):
	res = np.zeros((degree+1, degree+1))
	for i in range(degree+1):
		for j in range(degree+1):
			res[i, j] = integral(y[:, i], y[:, j], x, weight)
	return res

def test_legendre(degree):
	x = np.linspace(-1, 1, 2, dtype = np.float32)
	x_tf = tf.reshape(tf.constant(x), [-1, 1])
	l = Legendre_Normalized('tensorflow', degree, x_tf)
	weight = lambda x: 1
	with tf.Session() as sess:
		y = sess.run(l.tensor)
	return test(degree, x, y, weight)

def test_laguerre(degree):
	x = np.linspace(0, 1e3, 10000, dtype = np.float32)
	x_tf = tf.reshape(tf.constant(x), [-1, 1])
	l = Laguerre('tensorflow', degree, x_tf)
	weight = lambda x: np.exp(-x)
	with tf.Session() as sess:
		y = sess.run(l.tensor)
	return test(degree, x, y, weight)

def test_hermite(degree):
	x = np.linspace(-1e4, 1e4, 100000, dtype = np.float32)
	x_tf = tf.reshape(tf.constant(x), [-1, 1])
	l = Hermite('tensorflow', degree, x_tf)
	weight = lambda x: np.exp(-x**2/2)
	with tf.Session() as sess:
		y = sess.run(l.tensor)
	return test(degree, x, y, weight)

def test_hermite2(degree):
	x = np.linspace(-1e4, 1e4, 100000, dtype = np.float32)
	x_tf = tf.reshape(tf.constant(x), [-1, 1])
	l = Hermite2('tensorflow', degree, x_tf)
	weight = lambda x: np.exp(-x**2)
	with tf.Session() as sess:
		y = sess.run(l.tensor)
	return test(degree, x, y, weight)

def test_chebyshev(degree):
	x = np.linspace(-1+1e-6, 1-1e-6, 100000, dtype = np.float32)
	x_tf = tf.reshape(tf.constant(x), [-1, 1])
	l = Chebyshev('tensorflow', degree, x_tf)
	weight = lambda x: 1./np.sqrt(1.-x**2)
	with tf.Session() as sess:
		y = sess.run(l.tensor)
	return test(degree, x, y, weight)

def test_chebyshev2(degree):
	x = np.linspace(-1+1e-6, 1-1e-6, 100000, dtype = np.float32)
	x_tf = tf.reshape(tf.constant(x), [-1, 1])
	l = Chebyshev2('tensorflow', degree, x_tf)
	weight = lambda x: np.sqrt(1.-x**2)
	with tf.Session() as sess:
		y = sess.run(l.tensor)
	return test(degree, x, y, weight)

def test_jacobi(degree, alpha, beta):
	x = np.linspace(-1+1e-6, 1-1e-6, 100000, dtype = np.float32)
	x_tf = tf.reshape(tf.constant(x), [-1, 1])
	l = Jacobi('tensorflow', degree, x_tf, alpha, beta)
	weight = lambda x: ((1-x)**alpha)*((1+x)**beta)
	with tf.Session() as sess:
		y = sess.run(l.tensor)
	return test(degree, x, y, weight)



if __name__ == '__main__':
	print(test_legendre(2))
	print(test_laguerre(2))
	print(test_hermite(2))
	print(test_hermite2(2))
	print(test_chebyshev(2))
	print(test_chebyshev2(2))
	print(test_jacobi(2, 1, 3))