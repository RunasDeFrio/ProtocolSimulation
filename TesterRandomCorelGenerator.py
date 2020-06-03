import math
import numpy as np
from scipy import stats
import generators
import random

class TesterRandomCorelGenerator:
    def Init(self, N, m, y_min, y_max, dt, C):
        self.y_min = y_min
        self.y_max = y_max
        self.dt = dt
        self.m = m
        
        if N % 2 == 1:
            self.N = N + 1
        else: self.N = N
        
        self.a = ((y_max - y_min)/6) ** 2
        self.b = -math.log(0.05)/(3 * dt)
        self.C = C

    def Smirnov(self, Fx, Fy, Nx, Ny):

        D = abs(Fx[0]-Fy[0])
        for i in range(len(Fx)):
            Di=abs(Fx[i]-Fy[i])
            if(D < Di):
                D = Di 

        return 1-math.exp(-2* (D ** 2) / (1/Nx + 1/Ny))


    def Student(self, Dx, Dy, xm, ym, Nx, Ny):
        D = ((Nx-1)*Dx+(Ny-1)*Dy)/(Nx + Ny-2)
        t = math.sqrt((xm - ym) ** 2) * Nx * Ny/(D * (Nx + Ny))

        b = Nx + Ny - 2
        #Находим пошагово максимальную вероятность постепенно увеличивая точность
        h = 0.2
        p = 0.0
        while h > 0.00001:
            p += h
            #t сравниваем с табличным
            if t <= stats.t.isf(p, b) or p > 1:
                p -= h
                h /= 10
        return p


    def Fisher(self, Dx, Dy, Nx, Ny):
        if Dx > Dy:
            F = Dx/Dy
        else: 
            F = Dy/Dx

        b1 = Nx - 1
        b2 = Ny - 1
        #Находим пошагово максимальную вероятность постепенно увеличивая точность
        h = 0.2
        p = 0
        while h > 0.00001:
            p += h
            #F сравниваем с табличным
            if F <= stats.f.ppf(p, b1, b2) or p > 1:
                p -= h
                h /= 10
        return p

    def f(self, x):
        return self.a * np.exp(-x * self.b)

    def Calc(self, UI, ploter):
        xm = 0 
        ym = 0 
        Dx = 0 
        Dy = 0

        rand = generators.RandomCorrel(self.y_min, self.y_max, self.C)

        x_rand = np.zeros(self.N)
        for i in range(len(x_rand)):
            x_rand[i] = rand.rand()

        x = np.zeros(self.N // 2)
        y = np.zeros(self.N // 2)
        ix = 0
        iy = 0
        
        for i in range(len(x_rand)):
            if i % 2 == 0:
                x[ix] = x_rand[i]
                xm += x[ix]
                ix += 1
            else:
                y[iy] = x_rand[i]
                ym += y[iy]
                iy += 1

        xm /= len(x)
        ym /= len(y)

        for i in range(len(x)):
            Dx+=((x[i] - xm) ** 2)/(len(x)-1)
        for i in range(len(y)):
            Dy+=((y[i] - ym) ** 2)/(len(y)-1)

        Fx, _, _ = ploter.CreateHist(x, self.m)
        Fy, _, _ = ploter.CreateHist(y, self.m)
        ploter.Clear()
        #Расчитаем точки функции
        x = np.linspace(0, 2, 1000)
        y = self.f(x)

        #Добавим на холст полученные точки
        ploter.AddFunc(x, y)

        #Рисуем всё
        ploter.Draw("Плотность вероятности")

        UI.lineSmirnov.setText(f'{100 * self.Smirnov(Fx, Fy, len(x), len(y)):3.3f}'+'%')
        UI.lineStudent.setText(f'{100 * self.Student(Dx, Dy, xm, ym, len(x), len(y)):3.3f}'+'%')
        UI.lineFisher.setText (f'{100 * self.Fisher (Dx, Dy, len(x), len(y)):3.3f}'+'%')

