import numpy as np 
import matplotlib.pyplot as plt
from scipy import sparse 

means = [[2, 2], [8, 3], [3, 6]]
cov = [[1, 0], [0, 1]]
N = 500
X0 = np.random.multivariate_normal(means[0], cov, N)
X1 = np.random.multivariate_normal(means[1], cov, N)
X2 = np.random.multivariate_normal(means[2], cov, N)

# each column is a datapoint
X = np.concatenate((X0, X1, X2), axis = 0).T 
# extended data
X = np.concatenate((np.ones((1, 3*N)), X), axis = 0)
C = 3

original_label = np.asarray([0]*N + [1]*N + [2]*N).T


def convert_labels(y, C = C):
    """
    convert 1d label to a matrix label: each column of this 
    matrix coresponding to 1 element in y. In i-th column of Y, 
    only one non-zeros element located in the y[i]-th position, 
    and = 1 ex: y = [0, 2, 1, 0], and 3 classes then return

            [[1, 0, 0, 1],
             [0, 0, 1, 0],
             [0, 1, 0, 0]]
    """
    Y = sparse.coo_matrix((np.ones_like(y), 
        (y, np.arange(len(y)))), shape = (C, len(y))).toarray()
    return Y 


# softmax function
def softmax(Z):
    """
    Compute softmax values for each sets of scores in V.
    each column of V is a set of score.    
    """
    e_Z = np.exp(Z)
    A = e_Z / e_Z.sum(axis = 0)
    return A

def softmax_stable(Z):
	e_Z = np.exp(Z - np.max(Z, axis = 0, keepdims = True))
	A = e_Z/ e_Z.sum(axis = 0)
	return A

#cost or loss function
def cost(X, Y, W) :
	A = softmax_stable(W.T.dot(X))
	return -np.sum(Y*np.log(A))

# gradient function
def grad(X, Y, W):
	A = softmax_stable(W.T.dot(X))
	E = A - Y
	return X.dot(E.T)

# check gradient function
def numerical_grad(X, Y, W, cost):
	eps = 1e-6
	g = np.zeros_like(W)
	for i in range(W.shape[0]) :
		for j in range(W.shape[1]) :
			W_p = W.copy()
			W_n = W.copy()
			W_p[i, j] += eps
			W_n[i, j] -= eps
			g[i, j] = (cost(X, Y, W_p) - cost(X, Y, W_n))/(2*eps)
	g1 = grad(X, Y, W)
	if np.linalg.norm(g - g1) > 1e-7 :
		print("CHECK GRADIENT FUNCTION!")

def softmax_regression(X, y, W_init, eta, tol = 1e-4, max_count = 10000):
	W = [W_init]
	C = W_init.shape[1]
	Y = convert_labels(y,C)
	it = 0
	N = X.shape[1]
	d = X.shape[0]

	count = 0
	check_w_after = 20
	while count < max_count :
		#mix data
		mix_id = np.random.permutation(N)
		for i in mix_id :
			xi = X[:, 1].reshape(d, 1)
			yi = Y[:, 1].reshape(C, 1)
			ai = softmax_stable(np.dot(W[-1].T, xi))
			W_new = W[-1] + eta*xi.dot((yi- ai).T)
			count += 1
			# stopping criteria
			if count%check_w_after == 0 :
				if np.linalg.norm(W_new - W[-check_w_after]) < tol :
					return W
			W.append(W_new)
		return W

def pred(W,X):
	A = softmax_stable(W.T.dot(X))
	return np.argmax(A, axis = 0)

eta = .05
d = X.shape[0]
W_init = np.random.randn(X.shape[0], C)
W = softmax_regression(X, original_label, W_init, eta)
print(W[-1])

print(pred(W[-1], [[1],[2],[3]]))