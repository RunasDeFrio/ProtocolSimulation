import sys  # sys нужен для передачи argv в QApplication
from PyQt5 import QtWidgets
import pyqtgraph as pg
import pyqtgraph.exporters
import numpy as np
import design
from model import System

class ExampleApp(QtWidgets.QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        ColumnLabels =  ["Время(сек:мсек)","Производительность системы (пакетов/сек)", "Качество сообщений", 
        "Количество уничтоженных сообщений", "Средняя стоимость передачи одного сообщения", "Событие"]
        super().__init__()
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна

        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(100)
        self.progressBar.setValue(0)

        self.modelProtocol.setColumnCount(len(ColumnLabels))
        self.modelProtocol.setHorizontalHeaderLabels(ColumnLabels)
        self.modelProtocol.setSelectionBehavior( QtWidgets.QAbstractItemView.SelectRows )
        self.modelProtocol.horizontalHeader().setStretchLastSection( True )
        self.modelProtocol.resizeColumnsToContents()
        self.modelProtocol.setShowGrid(True)
        self.update_graph()
        self.startButton.clicked.connect(self.Start)
        #self.optButton.clicked.connect(self.CreateOptimum)
        #self.calcOpt.clicked.connect(self.CalcOptimum)
        
    def Start(self):
        #очистка и заполнение таблицы
        ColumnLabels =  ["Время(сек:мсек)","Производительность системы (пакетов/сек)", "Качество сообщений", 
        "Количество уничтоженных сообщений", "Средняя стоимость передачи одного сообщения", "Событие"]
        self.modelProtocol.clear()
        self.modelProtocol.setRowCount(0)
        self.modelProtocol.setColumnCount(len(ColumnLabels))
        self.modelProtocol.setHorizontalHeaderLabels(ColumnLabels)

        #Получение настроек
        isRandom = self.checkBox_2.isChecked()
        isRandomCorel = self.checkBox_3.isChecked()
        needFile = self.checkBox_5.isChecked()

        N = int(self.lineN.text())

        allTime = float(self.timeEdit.text())

        #Работа с файлом
        f = None
        if(needFile):
            f = open('Protocol.txt', 'w')
            for text in ColumnLabels:
                f.write(text+". ")
            f.write('\n')
        #Текст события
        event = ""
        #Передача настроек в модель
        Model = System(N, isRandom, isRandomCorel)
        passTime = Model.modelTime * Model.timeFactor

        #========Начало симуляции========
        while(passTime < allTime):
            #обновление модели
            Model.Update()
            passTime = Model.modelTime * Model.timeFactor
            #обновление прогресс бара
            self.progressBar.setValue(int((100*passTime)/allTime))
            #Получение события
            event = Model.GetEvent()
            #вывод в таблицу
            if(event!=""):
                i = self.modelProtocol.rowCount()
                self.modelProtocol.insertRow(i)
                self.modelProtocol.setItem(i,0, QtWidgets.QTableWidgetItem(self.getTime(passTime)))
                self.modelProtocol.setItem(i,1, QtWidgets.QTableWidgetItem(str(100*Model.GetSystemPerformance())))
                self.modelProtocol.setItem(i,2, QtWidgets.QTableWidgetItem(str(100*Model.GetMessageQuality())))
                self.modelProtocol.setItem(i,3, QtWidgets.QTableWidgetItem(str(Model.countDestroingPackage)))
                self.modelProtocol.setItem(i,4, QtWidgets.QTableWidgetItem(str(Model.GetCostTransmitting())))
                self.modelProtocol.setItem(i,5, QtWidgets.QTableWidgetItem(event))
            #вывод в файл
            if(needFile):   
                if(event!=""):
                    f.write(self.getTime(passTime) + ' : ')
                    f.write(str(100*Model.GetSystemPerformance()) + ' : ')
                    f.write(str(100*Model.GetMessageQuality()) + ' : ')
                    f.write(str(Model.countDestroingPackage) + ' : ')
                    f.write(str(Model.GetCostTransmitting()) + ' : ')
                    f.write(event +'\n')
        #========Конец симуляции========
        
        #прокрутка таблицы вниз
        self.modelProtocol.scrollToBottom()
        self.modelProtocol.horizontalHeader().setStretchLastSection(True)
        self.modelProtocol.resizeColumnsToContents()

    #Секунды в форматированную строку
    def getTime(self, time):
        return (str(int(time))+":"+str(int(time*1000)%1000) + "."+str(int(time*10000)%10))
    

    def CreateOptimum(self):
        #очистка и заполнение таблицы
        ColumnLabels = ["Производительность системы (пакетов/сек)", "Качество сообщений", 
        "Количество уничтоженных сообщений", "Средняя стоимость передачи одного сообщения"]
        self.modelProtocol.clear()
        self.modelProtocol.setRowCount(0)
        self.modelProtocol.setColumnCount(len(ColumnLabels))
        self.modelProtocol.setHorizontalHeaderLabels(ColumnLabels)

        #Получение диапазона параметра для моделирования
        Nmin = int(self.linemin1.text())
        Nmax = int(self.linemax1.text())
        
        #Получение настроек
        isRandom = self.checkBox_2.isChecked()
        isRandomCorel = self.checkBox_3.isChecked()
        needFile = self.checkBox_5.isChecked()

        allTime = int(self.timeEdit.text())

        #Работа с файлом
        f = None
        if(needFile):
            f = open('Protocol.txt', 'w')
            for text in ColumnLabels:
                f.write(text+". ")
            f.write('\n')
        
        #Перебор всех значений N
        for N in range(Nmin, Nmax+1):
            print(N, ":")
            #Передача настроек в модель
            Model = System(N, isRandom, isRandomCorel)
            #========Начало симуляции========
            while(Model.modelTime < allTime):
                #обновление модели
                Model.Update()
                #обновление времени
                
            if(Nmax-Nmin > 0):
                self.progressBar.setValue((100*(N-Nmin))//(Nmax-Nmin))
            else:
                self.progressBar.setValue(100)
            #вывод в таблицу
            if(needTable):
                i = self.modelProtocol.rowCount()
                self.modelProtocol.insertRow(i)
                self.modelProtocol.setItem(i,0, QtWidgets.QTableWidgetItem(str(N)))
                self.modelProtocol.setItem(i,1, QtWidgets.QTableWidgetItem(str(100*Model.GetSystemPerformance())))
                self.modelProtocol.setItem(i,2, QtWidgets.QTableWidgetItem(str(100*Model.GetMessageQuality())))
                self.modelProtocol.setItem(i,3, QtWidgets.QTableWidgetItem(str(Model.countDestroingPackage)))
                self.modelProtocol.setItem(i,3, QtWidgets.QTableWidgetItem(str(Model.GetCostTransmitting())))

            #вывод в файл
            if(needFile):
                f.write(str(N)+' : ')
                f.write(str(100*Model.GetSystemPerformance()) + ' : ')
                f.write(str(100*Model.GetMessageQuality()) + ' : ')
                f.write(str(Model.countDestroingPackage) + ' : ')
                f.write(str(Model.GetCostTransmitting()) + '\n')

    def CalcOptimum(self):
        rowCount = self.modelProtocol.rowCount()
        columnCount = self.modelProtocol.columnCount()
        
        arrayPareto = list()

        for i in range(0, rowCount):
            element = list()
            for j in range(0, columnCount):
                element.append(float(self.modelProtocol.item(i, j).text()))
            
            arrayPareto.append(element)

        i = 0
        while (i < len(arrayPareto)):
            j = 0
            while (j < len(arrayPareto)):
                if ((j != i) and (arrayPareto[i][1] <= arrayPareto[j][1]) and (arrayPareto[i][2] <= arrayPareto[j][2]) and (arrayPareto[i][3] >= arrayPareto[j][3])):
                    arrayPareto.pop(j)
                    j -= 1
                    if (i > j):
                        i -= 1
                j+=1
            i += 1

        ColumnLabels = ["Производительность системы (пакетов/сек)", "Качество сообщений", 
        "Количество уничтоженных сообщений", "Средняя стоимость передачи одного сообщения"]
        self.modelProtocol.clear()
        self.modelProtocol.setRowCount(0)
        self.modelProtocol.setColumnCount(len(ColumnLabels))
        self.modelProtocol.setHorizontalHeaderLabels(ColumnLabels)

        for i, mass in enumerate(arrayPareto):
            self.modelProtocol.insertRow(i)
            for j, data in enumerate(mass):
                self.modelProtocol.setItem(i,j, QtWidgets.QTableWidgetItem(str(data)))

    def update_graph(self):

        fs = 500
        f = 25
        ts = 1/fs
        length_of_signal = 100
        t = np.linspace(0,1,length_of_signal)
        
        cosinus_signal = np.cos(2*np.pi*f*t)
        sinus_signal = np.sin(2*np.pi*f*t)

        self.MplWidget.canvas.axes.clear()
        self.MplWidget.canvas.axes.plot(t, cosinus_signal)
        self.MplWidget.canvas.axes.plot(t, sinus_signal)
        self.MplWidget.canvas.axes.legend(('cosinus', 'sinus'),loc='upper right')
        self.MplWidget.canvas.axes.set_title('Cosinus - Sinus Signal')
        self.MplWidget.canvas.draw()

def main():
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = ExampleApp()  # Создаём объект класса ExampleApp
    window.show()  # Показываем окно
    app.exec_()  # и запускаем приложение

if __name__ == '__main__':
    main()  # то запускаем функцию main()