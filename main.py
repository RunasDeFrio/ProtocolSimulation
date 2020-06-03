import sys  # sys нужен для передачи argv в QApplication
from PyQt5 import QtWidgets
import locale
import design
from model import System
from simulator import Simulator
from optimizer import Optimizer
from TesterRandomGenerators import TesterRandomGenerators
from TesterRandomCorelGenerator import TesterRandomCorelGenerator
import generators
import math
import random

class ExampleApp(QtWidgets.QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        self.ColumnLabels =  ["Время(сек:мсек)","Производительность системы (пакетов/сек)", "Качество сообщений", 
        "Количество уничтоженных сообщений", "Средняя стоимость передачи одного сообщения", "Событие"]

        self.ColumnLabelsOptomum = ["Порог искажений", "Производительность системы (пакетов/сек)", "Качество сообщений", 
        "Количество уничтоженных сообщений", "Средняя стоимость передачи одного сообщения"]
        super().__init__()
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна

        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(100)
        self.progressBar.setValue(0)

        self.Simulator = Simulator()
        self.Optimizer = Optimizer()
        self.TesterRandomGenerators = TesterRandomGenerators()
        self.TesterRandomCorelGenerator = TesterRandomCorelGenerator()


        self.modelProtocol.setColumnCount(len(self.ColumnLabels))
        self.modelProtocol.setHorizontalHeaderLabels(self.ColumnLabels)
        self.modelProtocol.setSelectionBehavior( QtWidgets.QAbstractItemView.SelectRows )
        self.modelProtocol.horizontalHeader().setStretchLastSection( True )
        self.modelProtocol.resizeColumnsToContents()
        self.modelProtocol.setShowGrid(True)
        self.startButton.clicked.connect(self.Simulation)
        self.optButton.clicked.connect(self.CreateOptimum)
        self.calcOpt.clicked.connect(self.CalcOptimum)

        self.CalcTestsButt.clicked.connect(self.TestGenerators)
        self.CalcCorelTestButt.clicked.connect(self.TestCorelGenerator)


    def PushInTable(self, table, collums):
        i = table.rowCount()
        table.insertRow(i)
        for index, val in enumerate(collums):
            table.setItem(i, index, QtWidgets.QTableWidgetItem(str(val)))
    
    def ClearTable(self, table, head):
        #очистка и заполнение таблицы
        table.clear()
        table.setRowCount(0)
        table.setColumnCount(len(head))
        table.setHorizontalHeaderLabels(head)

    def ScrollAndResizeTable(self, table):
        #прокрутка таблицы вниз
        table.scrollToBottom()
        table.horizontalHeader().setStretchLastSection(True)
        table.resizeColumnsToContents()

    def Simulation(self):
        #очистка и заполнение таблицы
        self.ClearTable(self.modelProtocol, self.ColumnLabels)

        #Получение настроек
        allTime = locale.atof(self.timeEdit.text())
        N = locale.atoi(self.lineN.text())

        isRandom      = self.isRandom.isChecked()
        isRandomCorel = self.isRandomCorel.isChecked()
        needFile      = self.needFile.isChecked()

        quality = locale.atof(self.qualityEdit.text())
        self.Simulator.Init(allTime, N, quality, isRandom, isRandomCorel)
        self.Simulator.Simulate(self.modelProtocol, self, needFile, self.ColumnLabels, self.progressBar)

        #прокрутка таблицы вниз и ресайз
        self.ScrollAndResizeTable(self.modelProtocol)

    def TestCorelGenerator(self):
        y_min  = locale.atof(self.yminEdit.text())
        y_max    = locale.atof(self.ymaxEdit.text())
        dt = locale.atof(self.dtEdit.text())
        N = locale.atoi(self.N_edit_2.text())
        m = locale.atoi(self.m_edit_2.text())
        C = [locale.atof(self.c0Edit.text()), 
            locale.atof(self.c1Edit.text()), 
            locale.atof(self.c2Edit.text()),
            locale.atof(self.c3Edit.text())]
        self.TesterRandomCorelGenerator.Init(N, m, y_min, y_max, dt, C)
        self.TesterRandomCorelGenerator.Calc(self, self.plot_corel)

    def TestGenerators(self):
        sigma  = locale.atof(self.lineSigma_2.text())
        mat    = locale.atof(self.lineM_2.text())
        lambd = locale.atof(self.lineLamda_2.text())
        N = locale.atoi(self.N_edit.text())
        m = locale.atoi(self.m_edit.text())
        t = locale.atoi(self.tauEdit.text())
        if t > N:
            t = N
        #Выберем метод для тестирования
        randMetod = self.randMethod.currentText()
        randFunc  = self.funcMethod.currentText()
        #Выберем метод генерации
        if randMetod == "Метод серединных квадратов":
            randF1 = generators.RandomMiddleSqr(0.14159265358979323846)
            randF2 = generators.RandomMiddleSqr(0.71828182845904523541)
        elif randMetod =="Метод иррационального числа":
            randF1 = generators.RandomIrrational(math.pi)
            randF2 = generators.RandomIrrational(math.e)
        elif randMetod =="Конгруэнтный метод":
            randF1 = generators.RandomCongruent(random.randint(0, 10000))
            randF2 = generators.RandomCongruent(random.randint(0, 10000))
        else: return
        #Выберем функцию распределения
        if randFunc == "Экспоненциальное распределение":
            isNormal = False
            rand = generators.RandomExp(lambd, randF1)
        elif randFunc =="Нормальное распределение":
            isNormal = True
            rand = generators.RandomNormal(mat, sigma , randF1, randF2)
        else: return

        self.TesterRandomGenerators.Init(m, N, lambd, mat, sigma, rand, t, isNormal)
        self.TesterRandomGenerators.Calc(self, self.plot_fx, self.plot_Fx)

        
    def CreateOptimum(self):
        #очистка и заполнение таблицы        
        self.ClearTable(self.optimumTable, self.ColumnLabelsOptomum)

        #Получение диапазона параметра для моделирования
        Nmin = int(self.lineNmin.text())
        Nmax = int(self.lineNmax.text())
        allTime = float(self.timeEditOpt.text())
        
        quality = locale.atof(self.qualityEdit_2.text())

        #Получение настроек
        isRandom      = self.isRandomOpt.isChecked()
        isRandomCorel = self.isRandomCorelOpt.isChecked()
        needFile      = self.needFileOpt.isChecked()

        self.Optimizer.Init(allTime, Nmin, Nmax, quality, isRandom, isRandomCorel)
        self.Optimizer.CreateOptimum(self.optimumTable, self, needFile, self.ColumnLabelsOptomum, self.progressBar_2)

        #прокрутка таблицы вниз и ресайз
        self.ScrollAndResizeTable(self.optimumTable)

    def CalcOptimum(self):
        self.ClearTable(self.optimumOutTable, self.ColumnLabelsOptomum)
        self.Optimizer.CalcOptimum(self.optimumOutTable, self.optimumTable, self)
        self.ScrollAndResizeTable(self.optimumOutTable)


def main():
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = ExampleApp()  # Создаём объект класса ExampleApp
    window.show()  # Показываем окно
    app.exec_()  # и запускаем приложение

if __name__ == '__main__':
    main()  # то запускаем функцию main()