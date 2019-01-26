from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, Matern
from joblib import dump, load
import pandas as pd

# define model
def train_gp_model(X, y, kernel, alpha = 1e-10):
	"""define our kriging model

	input:
		
		kernel: 0 for gaussian kernel, 1 for Matern
		alpha:
		X: latitude and longitudes as pandas dataframe
		y: regressors as pandas dataframe

	output:

		gp_model: Gaussian process model fitted
	"""
	# define gp kernel
	if kernel == 0:
		kernel = Matern(length_scale=1.0, length_scale_bounds=(1e-05, 100000.0), nu=1.5)
	else:
		kernel = RBF(length_scale=1.0, length_scale_bounds=(1e-05, 100000.0))

	# alpha is jitter added to inverting the covariance matrix
	# optimisier is the optmisier
	gp_model = GaussianProcessRegressor(kernel=kernel, alpha=alpha, optimizer="fmin_l_bfgs_b", n_restarts_optimizer=0, 
						normalize_y=False, copy_X_train=True, random_state=None).fit(X, y)

	# save our regression model
	dump(gp_model, "./saved_gp_models/gp_ker{}.joblib".format(kernel))
	
	return gp_model


def gp_prediction(X_test, gp_model):
	"""Gaussian process regression model

	input:

		X_test:
		gp_model:

	output:

		pred_mean:
		pred_std:
	"""

	pred_mean, pred_std = gp_model.predict(X_test, return_std=True) 

	return pred_mean, pred_std

def use_pretrain(name):
	"""Load pretrained model

	input:

		name: string of gp model name

	output:

		model: pretrained model
	"""

	model = load("./saved_gp_models/{}.joblib".format(name))

	return model