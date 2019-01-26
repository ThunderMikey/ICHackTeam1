"""
Training function
"""
import model_gp
import mongodbutil as ml

if __name__ == "__main__":

    model = model_gp.gp_model.train_gp_model()