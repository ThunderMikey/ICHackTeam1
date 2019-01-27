"""
Training function
"""
import model.gp_model
import pandas as pd

if __name__ == "__main__":

    # read in data
    data_csv = pd.read_csv("./data/california_spacetime.csv")
    covariates = data_csv.iloc[:, [1,2,3]]
    for job in [4,6,7]:
        print("Training {}".format(job))
        response = data_csv.iloc[:, [job]]
        
        # using default jitter
        model.gp_model.train_gp_model(covariates, response, job)

    



