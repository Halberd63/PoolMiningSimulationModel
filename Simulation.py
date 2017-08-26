import random
from mesa import Agent, Model
from mesa.time import RandomActivation

#an arbitrary value used to denote wealth amongst miners
global BTCVALUE
BTCVALUE = 1000


#An agent that represents a cryptocurrency miner
class Miner(Agent):
    def __init__(self, uniqueID, model, power, soloPower = 0, poolMemberships = []):
        super().__init__(uniqueID, model)
        #Handle input arguments
        self.wealth = 0
        self.id = uniqueID
        #Computational power (This gets split between items in powerSplit)
        self.power = power
        #list of pools this miner needs to sign up for
        self.poolMemberships = poolMemberships
        #the power dedicated to solo mining (if any)
        self.soloDedicatedPower = soloPower

    #Give the miner wealth
    def giveWealth(self, wealth):
        self.wealth += wealth

    #Standard accessor functions
    def getPower(self):
        return self.power

    #Each step, the miners try to solve puzzles
    def step(self):
        #print(self.id)
        if (self.soloDedicatedPower > 0):
            if self.isBlockFound(self.soloDedicatedPower):
                self.foundBlockSolo()
        for membership in self.poolMemberships:
            if self.isBlockFound(membership.getCurrentContribution()):
                self.foundPoolBlock(membership.getPool())

    #Called when miner finds a block while mining alone
    def foundBlockSolo(self):
        self.wealth += BTCVALUE

    #Called when miner finds a block while mining in a pool
    #This function will be where behaviour is explored most
    #Currently, all miners are honest and report straight away
    def foundPoolBlock(self, pool):
        pool.foundBlock()


    #Returns true if block is found, false if not
    #We should ask Yevhen to double check this math
    def isBlockFound(self, power):
        effectivePower = power/self.model.getPuzzleDifficulty()
        passBar = 0.9*effectivePower
        return random.uniform(0,1) > passBar




#A linking class between a miner and their pool
#The class stores details such as:
#Total power contributed to the pool over history
#Current power contributed
#Length of time being a member
class PoolMembership:
    def __init__(self, pool, powerContribution, miner = None):
        #Handle input arguments
        self.pool = pool
        self.miner = miner
        self.currentContribution = powerContribution

        #Initialise history recording variables
        self.timeSinceJoining = 0
        self.totalPowerContributed = 0
        
    #This is called to set a miner to the membership after construction
    def linkToMiner(self, miner):
        self.miner = miner

    #Standard accessor functions
    def getMiner(self):
        return self.miner
    def getPool(self):
        return self.pool
    def getTotalPowerContribution(self):
        return self.totalPowerContributed
    def getTimeSinceJoining(self):
        return self.totalPowerContributed
    def getCurrentContribution(self):
        return self.currentContribution

    #Miner calls this function each step
    def makePowerContribution(self):
        self.timeSinceJoining += 1
        self.totalPowerContributed += self.currentContribution




class Pool:
    def __init__(self, fees, startingMembers = []):
        self.poolPower = 0
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
        self.poolPower += member.getCurrentContribution()

    #Miner (has the option to) call this after they've found a block
    def foundBlock(self):
        self.rewardMembers()

    #Function to give wealth to all members 
    #(In future, this function will differentiate different types of pools)
    def rewardMembers(self):
        for member in self.members:
            effort = member.getCurrentContribution / poolPowerAfterFees
            reward = BTCVALUE*effort
            reward *= 1-self.fees
            member.getMiner().giveWealth(reward)
        

    #O(n) function that updates the total power of the group
    #(Try not to call this often)
    def recalcPoolPower(self):
        totalPower = 0
        for member in self.members:
            totalPower += member.getCurrentContribution()
        self. totalPower








#The overarching simulation class.
#Takes in number of agents, number of pools and puzzle difficulty
class TheSimulation(Model):
    def __init__(self, N, P, D):
        #Input Validation
        assert N > 0, "INVALID SIMULATION: Need at least one miner"
        assert P >= 0, "INVALID SIMULATION: Can't have negative number of pools"
        assert D > 0, "INVALID SIMULATION: Difficulty must be a non-zero positive"

        #Handle the input arguments
        self.numberOfMiners = N
        self.numberOfPools = P
        self.puzzleDifficulty = D

        #Activate the schedule 
        #(Random means that agents act in a random order each turn)
        self.schedule = RandomActivation(self)
        
        #Create pools
        self.pools = [Pool(0.01) for _ in range(self.numberOfPools)]

        #Create agents
        for index in range(self.numberOfMiners):
            #Here, we make a bunch of random miners with different strategies
            #Many changes will need to be made in order to change agent behaviours
            #For now, this is the placeholder agent setup

            #Total miner power
            powerToSpend = 10
            initialPTS = powerToSpend

            #If the simulation has no pools then do the quicker miner creation
            if self.numberOfPools == 0:
                newMiner = Miner(index, self, powerToSpend, powerToSpend)
                self.schedule.add(newMiner)
                continue

            #Otherwise, if there are >0 pools then do the below code

            #Determine how independant the miner is
            percMineAlone = random.uniform(0,1)
            aloneMiningPower = 10*percMineAlone
            powerToSpend -= aloneMiningPower

            #Sign the miner up to pools with the remaining power
            numberOfPoolMemberships = 1
            if self.numberOfPools > 1:
                numberOfPoolMemberships = 1+random.randrange(self.numberOfPools)
            powerPerPool = powerToSpend / numberOfPoolMemberships
            poolMemberships = []
            availablePools = [pool for pool in self.pools] #DeepCopy
            for _ in range(numberOfPoolMemberships):
                poolIndex = random.randrange(len(availablePools))
                pool = availablePools[poolIndex]
                del availablePools[poolIndex]
                poolMemberships.append(PoolMembership(pool,powerPerPool))

            #Debugging help
            #print("ID: " + str(index) + "\t\tPower: " + str(initialPTS) 
            #    + "\tSoloMining Power: " + str(round(aloneMiningPower)) 
            #    + "\tNumber of pool memberships: " + str(len(poolMemberships)))

            #Actually create the miner
            newMiner = Miner(index, self, initialPTS, aloneMiningPower, poolMemberships)
            self.schedule.add(newMiner)

            #Link now created miner to all their memberships
            for membership in poolMemberships:
                membership.linkToMiner(newMiner)

        


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

    #Function to assist with debugging and early output
    def showAgentDeets(self):
        print("\n\n\n")
        for miner in self.schedule.agents:
            print("ID: " + str(miner.id) + "\t\tPower: " + str(miner.power) 
                + "\tSoloMining Power: " + str(round(miner.soloDedicatedPower)) 
                + "\tNumber of pool memberships: " + str(len(miner.poolMemberships))
                + "\tWealth: " + str(miner.wealth))


model = TheSimulation(50,3,100)
for _ in range(100):
    model.step()
model.showAgentDeets()