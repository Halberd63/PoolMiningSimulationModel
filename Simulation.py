import random
from mesa import Agent, Model
from mesa.time import RandomActivation

#an arbitrary value used to denote wealth amongst miners
global BTCVALUE
BTCVALUE = 1000


#An agent that represents a cryptocurrency miner
class Miner(Agent):
    def __init__(self, uniqueID, model, power, powerSplit):
        super().__init__(uniqueID, model)
        #Handle input arguments
        self.wealth = 0
        self.id = uniqueID
        #Computational power (This gets split between items in powerSplit)
        self.power = power
        #powersplit is a list of pairs: 
        #[pool (instance), % power given to pool (float)]
        #if "pool" is null then it counts as independant mining
        #(this null case will always be first in the list if it exists)
        self.powerSplit = powerSplit

    
    #Each step, the miners try to solve puzzles
    def step(self):
        print(self.id)




#A linking class between a miner and their pool
#The class stores details such as:
#Total power contributed to the pool over history
#Current power contributed
#Length of time being a member
class PoolMembership:
    def __init__(self, pool, miner):
        #Handle input arguments
        self.pool = pool
        self.miner = miner
        self.timeSinceJoining = 0
        self.totalPowerContributed = 0
        self.currentContribution = 0

    #Standard accessor functions
    def getTotalPowerContribution(self):
        return self.totalPowerContributed
    def getTimeSinceJoining(self):
        return self.totalPowerContributed
    def getCurrentContribution(self):
        return self.currentContribution

    #Miner calls this function each step
    def recordContribution(self, power):
        self.timeSinceJoining += 1
        self.totalPowerContributed += power
        self.currentContribution = power




class Pool:
    def __init__(self, fees, startingMembers = []):
        #% of a block that the pool admin takes for themself
        self.fees = fees
        #list of members in the pool (poolmembership instances)
        self.members = []
        for miner in startingMembers:
            self.recruit(miner)

    #Adds a miner to the list of members
    def recruit(self, miner):
        member = PoolMembership(self,miner)
        self.members.append(member)

    def rewardMembers(self):
        pass







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
            newMiner = Miner(i, self, 1, [None, 1])
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