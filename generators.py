import math
import random

class RandomMiddleSqr:
    def __init__(self, x0=0.14159265358979323846):
        self.x0=x0
        self.n = 20/2

    def rand(self):
        x = self.x0
        x = x**2
        x = x * (10**(self.n * 3))
        x = math.trunc(x)
        x = math.fmod(x, (10 ** (self.n * 2)))
        x = x /(10 **(self.n * 2))
        self.x0 = x
        return x


class RandomIrrational:
    def __init__(self, irrational = math.pi):
        self.irrational=irrational
        self.i = 0
    def rand(self):
        self.i+=1
        return math.modf(self.irrational*self.i)[0]


class RandomCongruent:
    def __init__(self, x0=1124123):
        self.x = x0
        self.a = 106
        self.c = 1283
        self.m = 6075

    def rand(self):
        self.x = (self.a * self.x + self.c)%self.m
        return self.x/self.m


class RandomExp:
    def __init__(self, lambd, singleRand = None):
    
        self.lambd = lambd
        if(singleRand == None):
            self.singleRand = RandomCongruent(random.randint(0, 10000))
        else:
            self.singleRand = singleRand
    
    def rand(self):
        return -math.log(1 - self.singleRand.rand()) / self.lambd


class RandomNormal:
    def __init__(self, m, sigma, _singleRand1 = None, _singleRand2 = None ):
        self.sigma = sigma
        self.m = m

        if(_singleRand1 == None):
            self.singleRand1 = RandomCongruent(random.randint(0, 10000))
        else:
            self.singleRand1 = _singleRand1

        if(_singleRand2==None):
            self.singleRand2 =  RandomCongruent(random.randint(0, 10000))
        else:
            self.singleRand2 =_singleRand2

    def rand(self):
        rand2 = self.singleRand2.rand()
        if(rand2 == 0):
            return 0
        else:
            return self.sigma * math.cos(2 * math.pi * self.singleRand1.rand()) * math.sqrt(-2 * math.log(rand2)) + self.m
    

class RandomCorrel:
    def __init__(self, y_min, y_max, _C, _singleRand = None):
    
        if(_singleRand == None):
            self.singleRand = RandomNormal(1, 0, RandomCongruent(random.randint(0, 10000)),RandomCongruent(random.randint(0, 10000)))
        else:
            self.singleRand =_singleRand
        self.M = (y_max+y_min)/2
        self.q0 = self.singleRand.rand()
        self.q1 = self.singleRand.rand()
        self.q2 = self.singleRand.rand()
        self.q3 = self.singleRand.rand()
        self.C = _C

    def rand(self):
        rand = self.C[0]*self.q0+self.C[1]*self.q1+self.C[2]*self.q2+self.C[3]*self.q3+self.M
        self.q0=self.q1 
        self.q1=self.q2 
        self.q2=self.q3 
        self.q3=self.singleRand.rand()
        return rand