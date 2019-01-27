"""
Training script
"""
import model.gp_model
import pandas as pd


if __name__ == "__main__":

    covariates = pd.read_csv("./data/california_spacetime_test.csv")
    covariates = covariates.iloc[:, [1,2,3]]

    gp_model = model.gp_model.use_pretrain("spatiotemporal7")
    predictions = pd.DataFrame(model.gp_model.gp_prediction(covariates, gp_model), columns=["maxprecipitation"])
    predictions
    print(predictions)
    predictions_df = pd.concat([covariates, predictions], axis=1)
    predictions_df.to_csv("california_spacetime_prediction_maxprecipitation.csv", index=False)
