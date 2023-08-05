library(pROC)
getRocCurve <- function(sorted.labels) {
    data.frame(TPR=cumsum(sorted.labels)/sum(sorted.labels), 
               FPR=cumsum(!sorted.labels)/sum(!sorted.labels), 
               sorted.labels)
}

getLabels <- function(file.name) {
    labels <- read.table(file.name, sep=",")
    return(as.numeric(labels[1, ]))
}

compare.roc <- function(file.a, file.b) {
    labels.a <- getLabels(file.a)
    labels.b <- getLabels(file.b)
    a <- roc(labels.a, length(labels.a):1, plot=T)
    b <- roc(labels.b, length(labels.b):1, plot=T)
    return(roc.test(b, a, plot=T))
    # roc.curve.a <- getRocCurve(labels.a)
    # roc.curve.b <- getRocCurve(labels.b)
    # plot(roc.curve.a$FPR, roc.curve.a$TPR)
}
