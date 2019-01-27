# forecasts spacetime temperatures
library(dbarts)

trainData <- read.csv("../data/max_temperature.csv", sep="\t")
trainData <- trainData[trainData$Year > 2005, ]
dim <- 3

testData <- cbind(Year = 2018, trainData[,c(2,3)])
for (year in 2019:2025) {
  testData <- rbind(cbind(Year=year, trainData[,c(2,3)]), testData)
}

model <- bart(trainData[,1:dim], trainData[,dim+1], keeptrees=TRUE, keepevery=20L, nskip=1000, ndpost=1000, ntree=50, k = 2)

y_pred <- colMeans(predict(model, testData[,c(1,2,3)]))

predictions <- data.frame(
    "Year"<- c(testData[, 1]),
    "Latitude" <- c(testData[, 2]),
    "Longitude" = c(testData[, 3]),
    "prediction"= y_pred
)
colnames(predictions) <- c("Year", "Latitude", "Longitude", "maxtemperature")

write.csv("../data/prediction_maxtemperature.csv", x = predictions)

data = read.csv("../data/prediction_maxprecipitation.csv")
write.csv(data, "../data/prediction_maxprecipitation.csv", sep = "\t")
write.
