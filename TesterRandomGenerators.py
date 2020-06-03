import math
import numpy as np
from scipy import stats
import generators
import random
from scipy import integrate

class TesterRandomGenerators:
    #Настройка тестера
    def Init(self, m, N, lamda, mat, sigma,  rand, t, isNormal):
        self.lamda = lamda
        self.mat = mat
        self.sigma = sigma

        self.m = m
        self.N = N
        self.t = t
        
        self.rand = rand
        self.isNormal = isNormal

    #Среднеквадратическое отклонение
    def SD(self):
        summ = 0.0
        for i in range(len(self.hist)):
            summ += (self.hist[i]-self.f(self.bins[i]+0.5 * self.h))**2
        return math.sqrt(summ/(len(self.hist)-1))

    #Критерий колмогорова
    def Kolmogorov(self):
        maxD = 0.0
        for i in range(len(self.histF)):
            D = abs(self.histF[i]-self.Integral(self.x_min, self.bins[i + 1]+0.5 * self.h)) #!!!!!!!!!!!!!!!!!!!!!!!!!!!
            if(maxD < D):
                maxD = D
        lamda = maxD*math.sqrt(float(self.m))
        p = 1.0
        for i in range(-1000, 1000):
            p -= pow(-1.0, float(i)) * math.exp(-2*i*i*lamda*lamda)

        return p

    #Критерий пирсона
    def Pirson(self):
        X = 0.0
        for i, P in enumerate(self.hist):
            Pj = self.Integral(self.bins[i], self.bins[i + 1])
            X += ((P - Pj) ** 2) / Pj
        X *= self.m
        if(self.isNormal):
            b = self.m - 3
        else:
            b = self.m - 2
        if b <= 0:
            return 0.0

        #Находим пошагово максимальную вероятность постепенно увеличивая точность
        h = 0.2
        p = 0.0
        while h > 0.00001:
            p += h
            #Хи2 сравниваем с табличным
            if X >= stats.chi2.isf(p, b - 1) or p > 1:
                p -= h
                h /= 10
        return p

    #Проверка по корреляционному моменту
    def Corel(self):
        maxp = 0.0
        for t in range(self.t):
            summ1, summ2, summ3, summ4, summ5 = (0.0, 0.0, 0.0, 0.0, 0.0)
            if t >= len(self.x_rand) -1:
                break
            for i in range(len(self.x_rand) - t):
                summ1 += self.x_rand[i] * self.x_rand[i+t]
                summ2 += self.x_rand[i]
                summ3 += self.x_rand[i+t]
                summ4 += self.x_rand[i] ** 2
                summ5 += self.x_rand[i+t] ** 2
            
            Kxy = (1/(self.N-t))*summ1 - (1/pow(self.N-t,2))*summ2*summ3
            Dx =  (1/(self.N-t))*summ4 - (1/pow(self.N-t,2))*summ2*summ2
            Dy =  (1/(self.N-t))*summ5 - (1/pow(self.N-t,2))*summ3*summ3
            p =abs(Kxy/math.sqrt(Dx*Dy))
            
            if(maxp < p):
                maxp = p
        h = 0.2
        p = 0.0
        while h > 0.00001:
            p += h
            #Проверяем условие
            if maxp <= (1-p)*math.sqrt(1/self.N) or p > 1:
                p -= h
                h /= 10
        return p
    
    #Функция плотности распределения
    def Integral(self, a, b):
        return integrate.quad(self.f, a, b)[0]
    
    #Функция распределения 
    def f(self, x):
        if self.isNormal:
            return np.exp(-(x-self.mat)**2/(2*(self.sigma)**2))/(self.sigma*np.sqrt(2 * math.pi))
        else:
            return self.lamda*np.exp(-self.lamda*x)

    def Calc(self, UI, plot_f, plot_F):
        #Очищаем графики
        plot_f.Clear()
        plot_F.Clear()
        
        #Генерируем случайные величины
        self.x_rand = np.zeros(self.N)
        for i in range(len(self.x_rand)):
            self.x_rand[i] = self.rand.rand()
        
        self.x_min = np.min(self.x_rand)
        self.x_max = np.max(self.x_rand)
        #Строим гистограмму на графике и получаем параметры этой гистограммы (Высоту элементов, границы элементов)
        self.hist, self.bins, _ = plot_f.CreateHist(self.x_rand, self.m)
        #Гистограмма равномерная, поэтому размер элемента получим из первых двух границ
        self.h = self.bins[1] - self.bins[0]
        
        #Проведём расчёт гистограммы F
        self.histF = self.hist.copy()

        self.histF[0] *= self.h
        for i in range(1, len(self.histF)):
            self.histF[i]=self.histF[i-1] + self.hist[i] * self.h

        #Добавим получившуюся гистограмму на график
        plot_F.AddHist(self.histF, self.bins + self.h/2)

        #Расчитаем точки функций распределения и плотности вероятности
        x = np.linspace(self.x_min, self.x_max, 1000)
        y = self.f(x)
        y_integr = y.copy()

        #Численно интегрируем данные простым методом (так быстрее всего)
        y_integr[0] = 0.0
        for i in range(1, len(y)):
            y_integr[i] = y_integr[i-1] + y[i] * (x[i] - x[i - 1])

        #Добавим на холст полученные точки
        plot_f.AddFunc(x, y)
        plot_F.AddFunc(x, y_integr)

        #Выводим показатели
        UI.editSD.setText    (f'{self.SD():3.6f}')
        UI.editCorel.setText (f'{100 * self.Corel():3.3f}'+'%')
        UI.editKolmag.setText(f'{100 * self.Kolmogorov():3.3f}'+'%')
        UI.editPirs.setText  (f'{100 * self.Pirson():3.3f}'+'%')
        #Рисуем всё
        plot_f.Draw("Плотность вероятности")
        plot_F.Draw("Функции распределения")
