import math
import generators
#Класс для работы с величинами, которые могут быть как случайными так и детерминированными. По факту просто контейнер с режимом
class RandomValue:
    def __init__(self, valueStandart, randomGenerator, isRandom):
        self.value = valueStandart
        self.generator = randomGenerator
        self.isRandom = isRandom

    def Get(self):
        if(self.isRandom):
            self.value  = self.generator.rand()
        return self.value

    def GetGreaterZero(self):
        if(self.isRandom):
            while(self.value <= 0):        
                self.value  = self.generator.rand()
        return self.value

#Класс канала, в данном классе содержится вся логика обработки пакета по каналу
class Channel:
    def __init__(self, isRandom, isRandomCorrel, System, N, i):
        #настройки моделирования
        self.isRandom = isRandom
        self.isRandomCorrel = isRandomCorrel

        #генераторы случайных значений
        randt1 = generators.RandomNormal(5, 1) #в миллисекундах
        randt3 = generators.RandomNormal(3, 1) #в миллисекундах
        randn = generators.RandomCorrel(0, 2, [0.333333332979894, 0.000015350131228, 0.00000000070688, 0.000000000000033])#данные из 3 пункта

        #статические значения
        self.t1  = RandomValue(5.0, randt1, isRandom)  #Время передачи пакета по каналу
        self.t3  = RandomValue(3.0, randt3, isRandom)  #Время ускоренной передачи пакета по каналу
        self.N   = N  #Лимит кол-ва искажений
        self.n   = RandomValue(1.0, randn, isRandomCorrel)  #скорость возникновения искажений

        #модель
        self.System = System

        self.eventStr = "" #строка для события
        self.i = i #номер канала

        self.havePackage = False      #передаётся ли пакет по каналу
        self.acceleration = False     #включено ли ускорения канала
        self.channelSpeed = 1/self.t1.GetGreaterZero() #скорость прохождения 1 пакета данных через канал
        self.packageComplete = 0.0    #процент прибытия пакета
        self.distortions = 0.0        #счётчик искажений


    def Update(self):
         #обрабатываем процесс передачи пакета по каналу
        if(self.havePackage):
            #проверяем сколько искажений в пакете
            if(self.distortions > self.N):
                self.eventStr += "Пакет на канале " + str(self.i) +" был уничтожен из-за сильных искажений."
                self.System.AddDestroyPackage()
                self.havePackage = False
                if(not self.acceleration):
                    self.System.AccelerationChannels()
            else:
                #проверяем пакет
                if(self.packageComplete >= 1.0):
                    self.eventStr += "Пакет на канале " + str(self.i) +" успешно передан."
                    self.havePackage = False
                    self.System.AddCompletePackage(self.distortions)
                else:
                    #обрабатываем процессы передачи пакета и накопления искажений
                    self.packageComplete += self.channelSpeed * self.System.deltaTime
                    self.distortions += self.n.Get() * self.System.deltaTime


    #Функция для обновления случайной скорости канала
    def UpdateSpeed(self):
        if(self.acceleration): 
            self.channelSpeed = 1/self.t3.GetGreaterZero()
        else: 
            self.channelSpeed = 1/self.t1.GetGreaterZero()

    #устанавливаем случайную скорость
    def AccelerationChannel(self):
        self.channelSpeed = 1/self.t3.GetGreaterZero()
        self.acceleration = True
    
    
    #устанавливаем обычную скорость
    def StandartSpeedChannel(self):
        self.channelSpeed = 1/self.t1.GetGreaterZero()
        self.acceleration = False



class System:
    def __init__(self, N, quality, isRandom = False, isRandomCorrel = False):
        #Настройки параметров моделирования
        self.isRandom = isRandom
        self.isRandomCorrel = isRandomCorrel
        #Создание каналов
        self.Channels = [Channel(isRandom, isRandomCorrel, self, N, i) for i in range(0, 2)] #список терминалов
        self.N = N
        #Настройки времени модели
        self.modelTime = 0
        self.deltaTime = 0.1 #в миллисекундах
        self.timeFactor = 0.001 #коэфициент перевода секунд во время модели
        #Переменные для моделирования
        self.timerNewPackage = 0.0   #таймер отчёта прибытия нового пакета
        randt2 = generators.RandomNormal(6, 3) #в миллисекундах
        self.t2  = RandomValue(6.0, randt2, isRandom)  #Интервал поступления нового пакета
        self.quality = quality

        #Переменные для вывода
        self.cost = 10000               #стоимость передачи пакета за единицу времени
        self.allDistortions = 0.0       #общее качество пакетов
        self.countDestroingPackage = 0  #кол-во уничтоженных пакетов
        self.countCompletePackage = 0   #кол-во переданных пакетов
        self.timeForCompletePackage = 0.0 #сумма времени (стоимостей) необходимое для передачи одного сообщения
        self.lastCompletePackageTime = 0.0   #предыдущее время успешной передачи пакета
        self.event = ""

    def Update(self):
        #обновляем таймер поступления нового пакета
        if(self.timerNewPackage > 0.0):
            self.timerNewPackage -= self.deltaTime
        for channel in self.Channels:
            channel.Update()
            if(channel.acceleration and self.GetMessageQuality() > self.quality):
                self.StandartSpeedChannels()

            #обрабатываем поступление нового пакета
            if(self.timerNewPackage <= 0.0 and not channel.havePackage):
                #если канал не занят - передаём по нему пакет
                channel.eventStr += "Канал " + str(channel.i) +" начал передачу пакета."
                channel.havePackage = True
                channel.distortions = 0.0 #обнуляем счётчик искажений
                channel.packageComplete = 0.0 #обнуляем процент прибытия пакета
                if(self.isRandom):
                    channel.UpdateSpeed() #обновляем скорость (имеет смысл только для случайной модели, т.к. время может измениться)

                #заного выставляем таймер
                self.timerNewPackage = self.t2.Get()

        self.modelTime += self.deltaTime

    def AddCompletePackage(self, distortions):
        self.allDistortions += 1.0 - distortions/self.N #переводим в процент качества передачи
        self.countCompletePackage += 1
        self.timeForCompletePackage += self.modelTime - self.lastCompletePackageTime
        self.lastCompletePackageTime = self.modelTime
    
    def AddDestroyPackage(self):
        self.allDistortions += 0.0 #качество максимально плохое
        self.countDestroingPackage += 1

    #ускорить каналы
    def AccelerationChannels(self):
        self.event += "Ускорение системы."
        for channel in self.Channels:
            channel.AccelerationChannel()

    #вернуть каналы в стандартный режим
    def StandartSpeedChannels(self):
        self.event += "Восстановление прежней скорости."
        for channel in self.Channels:
            channel.StandartSpeedChannel()

    def GetEvent(self):
        eventGet = self.event
        self.event = ""
        for channel in self.Channels:
            eventGet += channel.eventStr
            channel.eventStr = ""
        return eventGet

    #производительность системы: кол-во пакетов/сек
    def GetSystemPerformance(self):
        if(self.modelTime > 0.0):
            return self.countCompletePackage / (self.modelTime * self.timeFactor)
        else: return 0

    #Качество пакетов: сумма процентов качества искажений на кол-во пакетов
    def GetMessageQuality(self):
        if(self.countCompletePackage + self.countDestroingPackage > 0):
            return self.allDistortions / (self.countCompletePackage + self.countDestroingPackage)
        else: return 0

    #Средняя стоимость передачи сообщения: сколько времени нужно, чтобы передать одно сообщение
    def GetCostTransmitting(self):
        if(self.countCompletePackage > 0):
            return self.cost * self.timeForCompletePackage * self.timeFactor/self.countCompletePackage 
        else: return 0
