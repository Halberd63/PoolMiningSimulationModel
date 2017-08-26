import random
from mesa import Agent, Model
from mesa.time import RandomActivation

class Miner(Agent):
    
    def __init__(self, uniqueID, model, power):
        super().__init__(uniqueID, model)
        self.wealth = 0
        self.power = power
        self.id = uniqueID
    
    #Each step, the miners try to solve a puzzle
    def step(self):
        print(self.id)

class Pool:
    def __init__(self):
        pass #TODO


#The overarching simulation class.
#Takes in number of agents, number of pools and puzzle difficulty
class TheSimulation(Model):
    def __init__(self, N, P, D):
        #Handle the input arguments
        self.numberOfMiners = N
        self.numberOfPools = P
        self.puzzleDifficulty = D

        #Activate the schedule 
        #(Random means that agents act in a random order each turn)
        self.schedule = RandomActivation(self)
        
        #Create agents
        for i in range(self.numberOfMiners):
            newMiner = Miner(i, self, 1)
            self.schedule.add(newMiner)

        #Create pools
        self.pools = [Pool() for _ in range(self.numberOfPools)]

    #Advance the model by a discrete step
    def step(self):
        self.schedule.step()

    #Standard accessor functions
    def getNoOfMiners(self):
        return self.numberOfMiners
    def getNoOfPools(self):
        return self.numberOfPools
    def getPuzzleDifficulty(self):
        return self.puzzleDifficulty
    def getPoolList(self):
        return self.pools


model = TheSimulation(10,0,100)
model.step()
model.step()