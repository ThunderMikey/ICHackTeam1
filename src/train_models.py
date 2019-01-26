"""
Training function
"""
import model as model_gp

if __name__ == "__main__":

    # read in data

    for kernel in [0,1]:
        # using default jitter
        model_gp.gp_model.train_gp_model(X, y, kernel)



