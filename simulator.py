import design
from model import System
from PyQt5 import QtWidgets


class Simulator:
    def Init(self, allTime, N, quality, isRandom, isRandomCorel):
        self.allTime = allTime
        self.N = N
        self.quality = quality
        self.isRandom = isRandom
        self.isRandomCorel = isRandomCorel

    def Simulate(self, table, UI, needFile = False, ColumnLabels = None, progressBar = None):
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
        Model = System(self.N, self.quality, self.isRandom, self.isRandomCorel)
        passTime = Model.modelTime * Model.timeFactor

        #========Начало симуляции========
        while(passTime < self.allTime):
            #обновление модели
            Model.Update()
            #обновление времени
            passTime = Model.modelTime * Model.timeFactor

            #обновление прогресс бара
            if(progressBar != None):
                progressBar.setValue(int((100*passTime)/self.allTime))
            #Получение события
            event = Model.GetEvent()
            
            outList =   [self.getTime(passTime),
                        100*Model.GetSystemPerformance(),
                        100*Model.GetMessageQuality(),
                        Model.countDestroingPackage,
                        Model.GetCostTransmitting(),
                        event]
            #вывод в таблицу
            if(event!=""):
                UI.PushInTable(table, outList)
            #вывод в файл
            if(f != None and event != ""):
                self.InputInFile(f, outList)
        #========Конец симуляции========
        


    #Секунды в форматированную строку
    def getTime(self, time):
        return str(int(time))+":"+str(int(time*1000)%1000) + "."+str(int(time*10000)%10)

    def InputInFile(self, fileOut, data):
            s = ""
            for index, val in enumerate(data):
                if(index + 1 == len(data)):
                    s += str(val) + ' : '
                else: 
                    s += str(val) + '\n'
            fileOut.write(s)


    
