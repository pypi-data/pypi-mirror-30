z.prop = function(x1,x2,n1,n2){
  numerator = (x1/n1) - (x2/n2)
  p.common = (x1+x2) / (n1+n2)
  denominator = sqrt(p.common * (1-p.common) * (1/n1 + 1/n2))
  z.prop.ris = numerator / denominator
  return(z.prop.ris)
}


binomial.test <- function(success.gpc, success.macs, total.gpc, total.macs) {
    n.gpc <- sum(total.gpc)
    n.macs <- sum(total.macs)
    print((sum(success.gpc)-sum(success.macs))/(n.gpc-n.macs))

    p.hat.gpc <- sum(success.gpc)/n.gpc
    p.hat.macs <- sum(success.macs)/n.macs
    print(c(p.hat.gpc, p.hat.macs))
    p.hat <- weighted.mean(c(p.hat.gpc, p.hat.macs), c(n.gpc, n.macs))
    print(p.hat)
    standard.error <- sqrt(p.hat*(1-p.hat)*(1/n.gpc+1/n.macs))
    z = (p.hat.gpc-p.hat.macs)/standard.error
    print(z)
    return(pnorm(z, lower.tail=F))
}

# ARIBIDOPSIS
aribidopsis.gpc.n = c(3683, 2598, 2993, 963, 3022)
aribidopsis.gpc.s <- c(165, 123, 160, 136, 350)
aribidopsis.macs.n <- c(2005, 4215, 4338, 2558, 2559)
aribidopsis.macs.s <- c(132, 161, 159, 275, 218)

##### HUMAN
human.gpc.n = c(2699, 2830)
human.gpc.s = c(836, 330)
human.macs.n = c(1191, 1450)
human.macs.s = c(368, 153)

# DROSOPHILA
drosophila.gpc.n = c(1594, 2753, 1429, 3163)
drosophila.gpc.s = c(55, 557, 222, 59)
drosophila.macs.n = c(464, 622, 291, 311)
drosophila.macs.s = c(12, 91, 50, 3)


print("ARIBIDOPSIS")
binomial.test(aribidopsis.gpc.s,
              aribidopsis.macs.s,
              aribidopsis.gpc.n,
              aribidopsis.macs.n)

print("HUMAN")
binomial.test(human.gpc.s,
              human.macs.s,
              human.gpc.n,
              human.macs.n)

print("DROSOPHILIA")
binomial.test(drosophila.gpc.s,
              drosophila.macs.s,
              drosophila.gpc.n,
              drosophila.macs.n)
              
