library(forecast)
library(tseries)
library(doParallel)

trainData <- read.csv("../data/min_temperature.csv", sep="\t")
num_obs <- length(trainData[trainData["Year"] == 2006,1])

year2006_data <- trainData[trainData["Year"] == 2006,]

cl <- makeCluster(4)
registerDoParallel(cl)

predictions <- foreach(i=1:num_obs, .combine = rbind, .packages = c("forecast", "tseries")) %dopar% { 
  
  latitude <- year2006_data[i,2]
  longitude <- year2006_data[i,3]
  
  index <- intersect(which(c(trainData[,c(2)] == latitude)), which(c(trainData[,c(3)] == longitude)))
  #fit AR2 models
  fit <- arima(trainData[index, 4], order = c(1,0,0))
  y_pred <- forecast(fit, h = 8)$mean
  pred_val <- c(y_pred[1], latitude, longitude, 2018)
  
  for (j in 2:8) {
    pred_val <- rbind(c(y_pred[j], latitude, longitude, (2017+j)), pred_val)
  }
  print(pred_val)
}

stopCluster(cl)

predictions <- data.frame(predictions)
colnames(predictions) <- c("mintemperature", "Latitude", "Longitude", "Year")

write.csv("../data/prediction_mintemperature_time.csv", x = predictions, row.names=FALSE)

