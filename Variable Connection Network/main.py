import math
import random
import time
import numpy
import pygame
import copy
import matplotlib.pyplot as plot
import json
import os

random.seed(time.time())

def randomWeight():
    return random.random() * 2 - 1

def relu(number):
    return max(0, number)

# def drawTest(Window):
#     surface = pygame.Surface((4, 4))
#     surface.fill((255, 255, 255))
#     Window.fill((0, 0, 0))
#     ticks = 0
#     for x in range(128):
#         for y in range(128):
#             if (x/128 - 0.5)**2 + (y/128 - 0.5)**2 < 0.05:
#                 Window.blit(surface, (4*x, 4*y))
#                 pygame.display.flip()
#                 ticks += 1
#     print(ticks / 128**2)

class Neuron():

    def __init__(self, ConnectionCount= None, NumberOfNeuronsToConnectTo= None, Deactivate= False):
        self.bias = randomWeight()
        self.inputBuffer = 0
        self.input = 0
        self.ouptut = 0
        if Deactivate:
            self.maxconnections = 0
            self.weights = []
            self.connections = []
            return
        if ConnectionCount > NumberOfNeuronsToConnectTo:
            ConnectionCount = NumberOfNeuronsToConnectTo
        self.maxconnections = NumberOfNeuronsToConnectTo
        self.weights = [randomWeight() for i in range(ConnectionCount)]
        #samples random connections from the available ones
        self.connections = random.sample(range(NumberOfNeuronsToConnectTo), ConnectionCount)
    def SwitchBufferToInput(self):
        self.input = self.inputBuffer
        self.inputBuffer = 0
    def Run(self):
        if self.input > self.bias:
            self.output = 0
            return 0
        self.output = relu(self.input)
        return self.output

class VariableConnectionNetwork():

    def __init__(self, InputNeuronCount= None, HiddenNeuronCount= None, OutputNeuronCount= None, TotalConnections= None, Deactivate= False):
        self.output = []
        if Deactivate:
            self.inputNeuronCount = 0
            self.connectionCount = 0
            self.neuroncount = 0
            self.maxConnectionCount = 0
            self.hiddenNeuronCount = 0
            self.outputNeuronCount = 0
            self.averageConnectionsPerNeuron = 0
            self.maxConnectionsPerNeuron = 0
            self.inputneurons = []
            self.hiddenandoutputneurons = []
            return
        receivingNeuronCount = HiddenNeuronCount + OutputNeuronCount
        self.inputNeuronCount = InputNeuronCount
        self.connectionCount = TotalConnections
        self.neuroncount = InputNeuronCount + HiddenNeuronCount + OutputNeuronCount
        self.maxConnectionCount = InputNeuronCount * receivingNeuronCount + (receivingNeuronCount ** 2)
        self.hiddenNeuronCount = HiddenNeuronCount
        self.outputNeuronCount = OutputNeuronCount
        self.averageConnectionsPerNeuron = TotalConnections / self.neuroncount
        self.maxConnectionsPerNeuron = receivingNeuronCount

        #create neurons and connections
        connectionList = numpy.random.random(TotalConnections)
        connectionList *= TotalConnections / sum(connectionList)
        for i in range(len(connectionList)):
            connectionList[i] = max(1, connectionList[i])
        self.inputneurons = [Neuron(int(connectionList[i]), receivingNeuronCount) for i in range(InputNeuronCount)]
        self.hiddenandoutputneurons = [Neuron(int(connectionList[i + InputNeuronCount]), receivingNeuronCount) for i in range(receivingNeuronCount)]

    #def AddInputToNeuron(self, Input, NeuronIndex):
    #    if NeuronIndex < len(self.hiddenneurons):
    #        self.hiddenneurons[NeuronIndex].inputBuffer += Input
    #    else:
    #        self.outputneurons[NeuronIndex - self.hiddenNeuronCount].inputBuffer += Input

    def Run(self, InputArray):
        self.output = []
        #apply inputs to neurons
        for i, input in enumerate(InputArray):
            for x, weight in enumerate(self.inputneurons[i].weights):
                self.hiddenandoutputneurons[self.inputneurons[i].connections[x]].inputBuffer += input * weight
        #run the hidden and output neurons
        for i, neuron in enumerate(self.hiddenandoutputneurons):
            neuronoutput = neuron.Run()
            neuronweightedoutput = numpy.multiply(neuron.weights, neuronoutput)
            for x, weight in enumerate(neuronweightedoutput):
                self.hiddenandoutputneurons[neuron.connections[x]].inputBuffer += weight
            neuron.SwitchBufferToInput()
            if i < self.hiddenNeuronCount:
                continue
            self.output.append(neuronoutput)
        return self.output

    def Flush(self):
        for neuron in self.hiddenandoutputneurons:
            neuron.input = 0
            neuron.inputBuffer = 0
            neuron.output = 0

    def Mutate(self, MutationRate):
        for neuron in self.inputneurons:
            if random.random() <= MutationRate:
                if random.random() <= 0.8:
                    choice = int(random.random() * len(neuron.weights))
                    neuron.weights[choice] = randomWeight()
                else:
                    choice = int(random.random() * len(neuron.connections))
                    availableconnections = range(neuron.maxconnections)
                    availableconnections = list(set(availableconnections) - set(neuron.connections)) #remove used connections
                    neuron.connections[choice] = random.choice(availableconnections)
        for neuron in self.hiddenandoutputneurons:
            if random.random() <= MutationRate:
                if random.random() <= 0.8:
                    choice = int(random.random() * len(neuron.weights))
                    neuron.weights[choice] = randomWeight()
                else:
                    choice = int(random.random() * len(neuron.connections))
                    availableconnections = range(neuron.maxconnections)
                    availableconnections = list(set(availableconnections) - set(neuron.connections)) #remove used connections
                    neuron.connections[choice] = random.choice(availableconnections)

thing = VariableConnectionNetwork(2, 6, 4, 40)
start = time.time()
count = 0
while time.time() - start < 15:
    thing.Run([random.random() for i in range(2)])
    count += 1
print(int(count / 15))
time.sleep(999)

class Creature():

    #input is time
    #output is moveX, moveY
    def __init__(self, InputNeuronCount= None, HiddenNeuronCount= None, OutputNeuronCount= None, TotalConnections= None, Size = 4, Deactivate= False):
        self.size = Size
        self.color = [200 * random.random() + 55 for i in range(3)]
        self.x, self.y = random.random(), random.random()
        self.WindowSize = None
        self.clampX = 1
        self.clampY = 1
        self.totalmovement = 0
        if Deactivate == True:
            return
        self.brain = VariableConnectionNetwork(InputNeuronCount, HiddenNeuronCount, OutputNeuronCount, TotalConnections)
    def CopyCreatureBrain(self, creature):
        self.brain = copy.deepcopy(creature.brain)
        self.size = creature.size
        self.color = [200 * random.random() + 55 for i in range(3)]
        self.x, self.y = random.random(), random.random()
        return self
    def Tick(self, input):
        output = self.brain.Run(input)
        previousX, previousY = self.x, self.y
        if output[0] > output[2]:
            self.x += output[0] / 100
        else:
            self.x -= output[2] / 100
        if output[1] > output[3]:
            self.y += output[1] / 100
        else:
            self.y -= output[3] / 100
        self.x = numpy.clip(self.x, 0, 1)
        self.y = numpy.clip(self.y, 0, 1)
        self.totalmovement += abs(self.x - previousX) + abs(self.y - previousY)
    def Flush(self):
        self.brain.Flush()
        self.totalmovement = 0
    def DrawToWindow(self, Window):
        if self.WindowSize == None:
            self.WindowSize = Window.get_size()
            self.clampX = (self.WindowSize[0] - self.size) / self.WindowSize[0]
            self.clampY = (self.WindowSize[1] - self.size) / self.WindowSize[1]
        surface = pygame.Surface((self.size, self.size))
        surface.fill(self.color)
        Window.blit(surface, (self.x * self.WindowSize[0] * self.clampX, self.y * self.WindowSize[1] * self.clampY))

class Simulation():
    def __init__(self, Creatures, Frames):
        self.creatures = Creatures
        self.frames = Frames
        self.fitness = []
    def Mutate(self, CreatureParameters, CreatureCount, MutationRate, Window= None):
        i = 0
        if Window:
            Window.fill((0, 0, 0))
        while i < len(self.creatures):
            creature = self.creatures[i]
            #abs((creature.x - 0.5) * (creature.y - 0.5)) > 0.0625
            #(creature.x - 0.5) ** 2 + (creature.y - 0.5) ** 2 < 0.05
            if creature.x < 0.5:
                creature.Flush()
                if Window:
                    creature.DrawToWindow(Window)
                creature.x, creature.y = random.random(), random.random()
                #creature.skin.fill((0, 255, 0))
            else:
                self.creatures.pop(i)
                i -= 1
            i += 1
        if Window:
            pygame.display.flip()
        survivors = len(self.creatures)
        self.fitness.append((survivors / CreatureCount) ** 2)
        if len(self.creatures) == 0:
            self.creatures = [Creature(*CreatureParameters) for i in range(CreatureCount)]
            return
        if len(self.creatures) > CreatureCount / 10:
            self.creatures = random.sample(self.creatures, int(CreatureCount / 10))
        while len(self.creatures) < CreatureCount:
            mutatingCreature = Creature(Deactivate= True).CopyCreatureBrain(random.choice(self.creatures))
            mutatingCreature.brain.Mutate(MutationRate)
            self.creatures.append(mutatingCreature)

    def Run(self, Generations= 1, CreatureParameters= None, CreatureCount= None, MutationRate= 0.01, Window= None, FitnessThreshold= 1, SaveFile= None):
        if not CreatureCount:
            CreatureCount = len(self.creatures)
        if not CreatureParameters:
            CreatureParameters = (self.creatures[0].brain.inputNeuronCount, self.creatures[0].brain.hiddenNeuronCount, self.creatures[0].brain.outputNeuronCount, self.creatures[0].brain.connectionCount)
        index = 0
        while index < Generations:
            random.seed(time.time())
            for i in range(self.frames):
                if Window:
                    Window.fill((0, 0, 0))
                for creature in self.creatures:
                    creature.Tick([i / self.frames, random.random()])
                    if Window:
                        creature.DrawToWindow(Window)
                if Window:
                    pygame.display.flip()
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
            self.Mutate(CreatureParameters, CreatureCount, MutationRate, Window)
            time.sleep(0.25)
            if self.fitness[-1] > FitnessThreshold and index > 0:
                break
            print("Generation", len(self.fitness) - 1, "fitness:", round(self.fitness[-1], 6))
            index += 1
            if SaveFile:
                self.Save(SaveFile)
        return self.creatures
    def GraphFitness(self):
        xpoints = range(len(self.fitness))
        ypoints = self.fitness[:]
        xaxisrange = [0, len(xpoints) - 1]
        yaxisrange = [0, 1]
        plot.plot(xpoints, ypoints, '-')
        if sum(xaxisrange) != 0:
            plot.axis([*xaxisrange, *yaxisrange])
        plot.xlabel("Generations")
        plot.ylabel("Fitness")
        plot.suptitle("Population Graph")
        plot.show()
    def Save(self, FileName):
        with open(FileName, 'w') as SIMULATIONFILE:
            savedata = {'brains': [], 'fitness': self.fitness, 'frames': self.frames}
            for creature in self.creatures:
                savedata['brains'].append({'inputneurons': [], 'hiddenandoutputneurons': [],
                                           'outputneuroncount': creature.brain.outputNeuronCount,
                                           'connectioncount': creature.brain.connectionCount})
                for neuron in creature.brain.inputneurons:
                    savedata['brains'][-1]['inputneurons'].append(
                        {'weights': neuron.weights, 'connections': neuron.connections, 'bias': neuron.bias, 'maxconnections': neuron.maxconnections})
                for neuron in creature.brain.hiddenandoutputneurons:
                    savedata['brains'][-1]['hiddenandoutputneurons'].append(
                        {'weights': neuron.weights, 'connections': neuron.connections, 'bias': neuron.bias, 'maxconnections': neuron.maxconnections})
            SIMULATIONFILE.write(json.dumps(savedata))
            SIMULATIONFILE.close()
    def Load(self, FileName):
        with open(FileName, 'r') as SIMULATIONFILE:
            if os.stat(FileName).st_size == 0:
                print("Simulation file not found")
                return False
            loaddata = json.load(SIMULATIONFILE)
            creatures = []
            for i, brain in enumerate(loaddata['brains']):
                newbrain = VariableConnectionNetwork(Deactivate=True)
                newbrain.inputNeuronCount = len(brain['inputneurons'])
                newbrain.outputNeuronCount = brain['outputneuroncount']
                newbrain.hiddenNeuronCount = len(brain['hiddenandoutputneurons']) - newbrain.outputNeuronCount
                newbrain.connectionCount = brain['connectioncount']
                for neuron in loaddata['brains'][i]['inputneurons']:
                    newneuron = Neuron(Deactivate=True)
                    newneuron.weights = neuron['weights']
                    newneuron.connections = neuron['connections']
                    newneuron.bias = neuron['bias']
                    newneuron.maxconnections = neuron['maxconnections']
                    newbrain.inputneurons.append(newneuron)
                for neuron in loaddata['brains'][i]['hiddenandoutputneurons']:
                    newneuron = Neuron(Deactivate=True)
                    newneuron.weights = neuron['weights']
                    newneuron.connections = neuron['connections']
                    newneuron.bias = neuron['bias']
                    newneuron.maxconnections = neuron['maxconnections']
                    newbrain.hiddenandoutputneurons.append(newneuron)
                newcreature = Creature(Deactivate=True)
                newcreature.brain = newbrain
                creatures.append(newcreature)
            newsimulation = Simulation(creatures, loaddata['frames'])
            newsimulation.fitness = loaddata['fitness']
            return newsimulation


creatureCount = 128
frames = 384
creatureParameters = 2, 6, 4, 40
creatures = [Creature(*creatureParameters) for i in range(creatureCount)]
mutationRate = 0.01
survivors = creatureCount
averagemovement = 0

mainSimulation = Simulation.Load(Simulation, "SIMULATION.txt")#Simulation(creatures, 256)
if not mainSimulation:
    mainSimulation = Simulation(creatures, frames)

pygame.init()
Window = pygame.display.set_mode((512, 512))
Window.fill((0, 0, 0))
pygame.quit()

start = time.time()
mainSimulation.Run(3)
print((time.time() - start) / 3)

mainSimulation.Run(math.inf, Window= Window, FitnessThreshold= 0.9, SaveFile= "SIMULATION.txt")
mainSimulation.GraphFitness()
mainSimulation.Run(math.inf, Window= Window, FitnessThreshold= 1.0, SaveFile= "SIMULATION.txt")
pygame.quit()
mainSimulation.GraphFitness()

print("DONE")
exit()