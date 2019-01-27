from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import Matern
import pickle
import pandas as pd

# define model
def train_gp_model(X, y, data_name, alpha = 1e-10):
	"""define our kriging model

	input:
		X: latitude, longitudes and time as pandas dataframe
		y: regressors as pandas dataframe
		alpha: jitter for covariance matrix. Default 1e-10

	output:

		gp_model: Gaussian process model fitted
	"""
	# define gp kernel
	kernel = Matern()

	# alpha is jitter added to inverting the covariance matrix
	# optimisier is the optmisier
	gp_model = GaussianProcessRegressor(kernel=kernel, alpha=alpha, optimizer="fmin_l_bfgs_b", n_restarts_optimizer=0, 
						normalize_y=False, copy_X_train=True, random_state=None).fit(X, y)

	# save our regression model
	pickle.dump(gp_model, open("./saved_gp_models/spatiotemporal{}.joblib".format(data_name), 'wb'))
	
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

	pred_mean = gp_model.predict(X_test, return_std=False) 

	return pred_mean

def use_pretrain(name):
	"""Load pretrained model

	input:

		name: string of gp model name

	output:

		model: pretrained model
	"""

	model = pickle.load(open("./saved_gp_models/{}.joblib".format(name), "rb"))

	return model