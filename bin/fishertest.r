filename = "matrix_name.csv"
M = read.csv(filename,header=F)
M = M[,colSums(abs(M)) != 0]
M = M[rowSums(abs(M)) != 0,]
test = fisher.test(M,hybrid=TRUE,simulate.p.value=TRUE,B=10000)
test$p.value
