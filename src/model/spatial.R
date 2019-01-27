# forecasts spacetime temperatures
library(dbarts)

trainData <- read.csv("../data/max_temperature.csv", sep="\t")
trainData <- trainData[trainData$Year > 2005, ]
dim <- 3

testData <- cbind(Year = 2018, trainData[trainData$Year == 2006,c(2,3)])
for (year in 2019:2025) {
  testData <- rbind(cbind(Year=year, trainData[trainData$Year == 2006,c(2,3)]), testData)
}

dim(trainData[trainData$Year == 2006,c(2,3)])

model <- bart(trainData[,1:dim], trainData[,dim+1], keeptrees=TRUE, keepevery=20L, nskip=1000, ndpost=1000, ntree=50, k = 2)

y_pred <- colMeans(predict(model, testData[,c(1,2,3)]))

predictions <- data.frame(
    "Year"<- c(testData[, 1]),
    "Latitude" <- c(testData[, 2]),
    "Longitude" = c(testData[, 3]),
    "prediction"= y_pred
)
colnames(predictions) <- c("Year", "Latitude", "Longitude", "maxtemperature")


data <- read.csv("../data/prediction_maxprecipitation.csv", sep="\t")
data <- data[data$Year== 2020, -c(1)]

df2 <- read.csv("../data/prediction_maxtemperature.csv", sep="\t")
df2 <- df2[df2$Year== 2020, -c(1)]
data$maxtemperature <- df2$maxtemperature

df2 <- read.csv("../data/prediction_mintemperature.csv", sep="\t")
df2 <- df2[df2$Year== 2020, -c(1)]

data$mintemperature <- df2$mintemperature

write.csv("../data/prediction_space.csv", x = data, row.names = FALSE)

