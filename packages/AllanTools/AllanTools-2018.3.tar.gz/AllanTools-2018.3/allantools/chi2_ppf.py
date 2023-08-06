"""
This file is part of AllanTools

License
-------

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

import math
import numpy
 
def bisection(function, k, p, a, b, tol):
    # http://code.activestate.com/recipes/578417-bisection-method-in-python/
    assert (function(a,k)-p)*(function(b,k)-p) < 0 # a, b must bracket root
    c = (a+b)/2.0
    while (b-a)/2.0 > tol:
        if (function(c, k)-p) == 0:
            return c
        elif (function(a,k)-p)*(function(c,k)-p) < 0:
            b = c
        else :
            a = c
        c = (a+b)/2.0
    return c


def lower_gamma_first(s,x):
    # lower incomplete gamma function, first implementation
    # https://en.wikipedia.org/wiki/Incomplete_gamma_function#Evaluation_formulae
    g  = 0
    last_g = 1.0
    done = False
    tol = 1.0e-6
    k=0
    while not done:
        top = pow(x, s)*math.exp(-x)*pow(x,k)
        bot = numpy.prod( [float(s+j) for j in range(k+1) ] )
        dg = float(top)/float(bot)
        if dg == float("Inf"):
            break
        g += dg
        k += 1
        if k>100: # get at least 100 terms in the sum
            if g==0:
                break
            delta = abs(dg/g)
            if delta == float("Inf"):
                break
            if delta < tol:
                done = True
        last_g = g
    return g
    
def lower_gamma_second(s,x):
    # second implementation with better dynamic range
    # lower incomplete gamma function
    # https://en.wikipedia.org/wiki/Incomplete_gamma_function#Evaluation_formulae
    g  = 0
    last_g = 1.0
    done = False
    tol = 1.0e-6
    k=0
    while not done:
        if x != 0:
            log_top = math.log(x) * (s + k) - x
        else:
            log_top = 0
        log_bot = sum(math.log(s+j) for j in range(k+1))
        dg = math.exp(log_top - log_bot)
        if dg == float("Inf"):
            break
        g += dg
        k += 1
        if k>100: # get at least 100 terms in the sum
            if g==0:
                break
            delta = abs(dg/g)
            if delta == float("Inf"):
                break
            if delta < tol:
                done = True
        last_g = g
    return g
    
def log_lower_gamma(s,x):
    # second implementation with better dynamic range
    # lower incomplete gamma function
    # https://en.wikipedia.org/wiki/Incomplete_gamma_function#Evaluation_formulae
    g  = 0
    last_g = 1.0
    done = False
    tol = 1.0e-6
    k=0
    log_g = math.lgamma(s/2.0)
    print "gamma=", log_g
    print "x=",x
    
    while not done:
        if x != 0:
            log_top = math.log(x) * (s + k) - x
        else:
            log_top = 0
        log_bot = sum(math.log(s+j) for j in range(k+1))
        print "log_top ",log_top
        print "log_bot ",log_bot
        print "log_g ", log_g
        dg = math.exp( log_top - log_bot - log_g )
        if dg == float("Inf"):
            break
        g += dg
        k += 1
        print k, dg, log_top, log_bot, g
        if k>100: # get at least 100 terms in the sum
            if g==0:
                break
            delta = abs(dg/g)
            if delta == float("Inf"):
                break
            if delta < tol:
                done = True
        last_g = g
    return g
 
def chi2_cdf(x, k):
    # chi-squared cumulative density function
    # cdf(x; k) = lower_gamma(k/2, x/2) / gamma(k/2)
    #lg = lower_gamma_second(k/2.0, x/2.0)
    log_lg = log_lower_gamma(k/2.0, x/2.0)
    #print "lg = ",log_lg
    #log_g = math.lgamma(k/2.0)
    return log_lg
 
def chi2_ppf(p, k):
    # chi-squared Percent point function (inverse of cdf percentiles).
    # look for x such that
    # p = chi2_cdf( x=chi2_ppf(p, k), k)
    tol = 1e-8
    lolim = 0
    hilim = k
    print "p= ",p
    print "k= ",k
    while (chi2_cdf(lolim,k)-p)*(chi2_cdf(hilim,k)-p) > 0: 
        hilim *= 1.5
    return bisection( chi2_cdf, k, p, lolim, hilim, tol)

if __name__ == "__main__":
    import scipy.stats
    p=0.158
    k=782.0
    print "scipy cdf: ",scipy.stats.chi2.ppf(p, k)
    print "own   cdf: ",chi2_ppf(p, k)
     
     
    print "scipy ppf ", scipy.stats.chi2.ppf(0.4, 33)
    print "  own ppf ", chi2_ppf(0.4, 33)
     
    # test that we really found the inverse
    print scipy.stats.chi2.cdf(scipy.stats.chi2.ppf(0.4, 33), 33)
    print chi2_cdf( chi2_ppf(0.4, 33), 33 )
     
    # try to check the scipy function against our own function
    # for some random input of (p, k)
    for n in range(100):
        k = numpy.random.randint(20, 200)
        # some failures occur with p = .9999
        for p in .999, .99, .9, .5, .1, .01, .001, .0001:
            print k, p,
            a=scipy.stats.chi2.ppf(p, k)
            b=chi2_ppf(p, k)
            ok = numpy.isclose(a, b)
            print  int(ok)


