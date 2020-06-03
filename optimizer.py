import design
from model import System

class Optimizer:
    def Init(self, allTime, Nmin, Nmax, quality, isRandom, isRandomCorel):
        self.allTime = allTime
        self.Nmin = Nmin
        self.Nmax = Nmax
        self.isRandom = isRandom
        self.isRandomCorel = isRandomCorel
        self.quality = quality

    def CreateOptimum(self, table, UI, needFile = False, ColumnLabels = None, progressBar = None):

        #Работа с файлом
        f = None
        if(needFile):
            f = open('Protocol.txt', 'w')
            for text in ColumnLabels:
                f.write(text+". ")
            f.write('\n')
        
        #Перебор всех значений N
        for N in range(self.Nmin, self.Nmax+1):
            #Передача настроек в модель
            Model = System(N, self.quality, self.isRandom, self.isRandomCorel)
            passTime = Model.modelTime * Model.timeFactor
            #========Начало симуляции========
            while(passTime < self.allTime):
                #обновление модели
                Model.Update()
                #обновление времени
                passTime = Model.modelTime * Model.timeFactor
            #========Вывод результатов симуляции========
            #обновление прогресс бара
            if(progressBar != None):
                if(self.Nmax-self.Nmin > 0):
                    progressBar.setValue((100*(N-self.Nmin))//(self.Nmax-self.Nmin))
                else:
                    progressBar.setValue(100)
            
            outList =  [N,
                        100*Model.GetSystemPerformance(),
                        100*Model.GetMessageQuality(),
                        Model.countDestroingPackage,
                        Model.GetCostTransmitting()]
            #вывод в таблицу
            UI.PushInTable(table, outList)

            #вывод в файл
            if(f != None):
                self.InputInFile(f, outList)

    #Взять данные из таблицы и передать в другую таблицу
    def CalcOptimum(self, tableOut, tableIn, UI):
        rowCount = tableIn.rowCount()
        columnCount = tableIn.columnCount()
        
        arrayPareto = list()
        #чтение с таблицы
        for i in range(0, rowCount):
            element = list()
            for j in range(0, columnCount):
                element.append(float(tableIn.item(i, j).text()))
            
            arrayPareto.append(element)

        i = 0
        while (i < len(arrayPareto)):
            j = 0
            while (j < len(arrayPareto)):
                if ((j != i)    and (arrayPareto[i][1] >= arrayPareto[j][1]) 
                                and (arrayPareto[i][2] >= arrayPareto[j][2]) 
                                and (arrayPareto[i][3] <= arrayPareto[j][3])
                                and (arrayPareto[i][4] <= arrayPareto[j][4])):
                    arrayPareto.pop(j)
                    j -= 1
                    if (i > j):
                        i -= 1
                j+=1
            i += 1
        #Вывод в другую таблицу
        for data in arrayPareto:
            UI.PushInTable(tableOut, data)


    def InputInFile(self, fileOut, data):
            s = ""
            for index, val in enumerate(data):
                if(index + 1 == len(data)):
                    s += str(val) + ' : '
                else: 
                    s += str(val) + '\n'
            fileOut.write(s)