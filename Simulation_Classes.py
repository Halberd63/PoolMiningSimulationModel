import random
from mesa import Agent, Model
from mesa.time import RandomActivation

#an arbitrary value used to denote wealth amongst miners
global BTCVALUE
BTCVALUE = 1000

#Variables that decide who actually found a block when one is found to be found
global passValue, currentValue, blockFound # We need a better names
passValue = 0
currentValue = 0
blockFound = False



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
        global blockFound
        if (self.soloDedicatedPower > 0):
            if not blockFound and self.isBlockFound(self.soloDedicatedPower):
                self.foundBlockSolo()
        for membership in self.poolMemberships:
            if not blockFound and self.isBlockFound(membership.getCurrentContribution()):
                self.foundPoolBlock(membership.getPool())

    #Each action, the miner makes shares and potentially misbehaves
    def act(self):
        if self.id == 0:
            for membership in self.poolMemberships:
                if membership.getCurrentContribution() > 0:
                    membership.setCurrentContribution(0)
            self.poolMemberships[random.randint(0, len(self.poolMemberships)-1)].setCurrentContribution(self.power)
        for membership in self.poolMemberships:
            membership.pool.recieveShares(membership)
            membership.makePowerContribution()
    def sharesFound(self, power):
        sharesFound = 0
        p = power/self.model.totalPower
        d = self.model.puzzleDifficulty
        #Chance of finding a share should be 2,000,000x easier
        #Than chance of finding block

        #TODO
        #Calculate how many shares this miner finds in each step

        return sharesFound


    #Called when miner finds a block while mining alone
    def foundBlockSolo(self):
        self.wealth += BTCVALUE

    #Called when miner finds a block while mining in a pool
    #This function will be where behaviour is explored most
    #Currently, all miners are honest and report straight away
    def foundPoolBlock(self, pool):
        pool.foundBlock()


    #Returns true if block is found, false if not
    def isBlockFound(self, power):
        global passValue, currentValue, blockFound
        currentValue += power
        if currentValue > passValue:
            currentValue = 0
            blockFound = True
            return True
        return False




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
    def setCurrentContribution(self,power):
        self.currentContribution = power
    def getCurrentContribution(self):
        return self.currentContribution

    #Miner calls this function each step
    def makePowerContribution(self):
        self.timeSinceJoining += 1
        self.totalPowerContributed += self.currentContribution
    def resetPowerContribution(self):
        self.timeSinceJoining = 0
        self.totalPowerContributed = 0



class Pool:
    def __init__(self, fees, startingMembers = []):
        self.poolPower = 0
        #% of a block that the pool admin takes for themself
        self.fees = fees
        #list of members in the pool (poolmembership instances)
        self.members = []
        for miner in startingMembers:
            self.recruit(miner)

        self.sharesSubmitted = []
        self.sharesSinceLastRound = 0 # Shares are equivalent to the average power contributed * number of ticks
        self.rewardScheme = None


    #Set the reward scheme of the pool. Scheme options:
    #PPLNS = Pay per last N Shares
    #PROP = Proportional
    #PPS = Pay per share
    def setRewardScheme(self, scheme, N = 0):
        self.rewardScheme = scheme
        if scheme == "PPLNS":
            self.lastN = N

    #Adds a miner to the list of members
    def recruit(self, miner, member=None):
        if member == None:
            member = PoolMembership(self,miner)
        if member not in self.members:
            self.members.append(member)
        self.poolPower += member.getCurrentContribution()

    def minerLeaves(self,miner,member):
        self.poolPower -= member.getCurrentContribution()

    #Miner (has the option to) call this after they've found a block
    def foundBlock(self):
        if self.rewardScheme == "PPLNS":
            self.pplnsRewardMembers()
        else: 
            self.genericRewardMembers()

    #Function to give wealth to all members base on current input
    #Processing power (This is not accurate to real world as it
    #Does not consider shares, as such, only use it for testing)
    def genericRewardMembers(self):
        sum = 0
        for member in self.members:
            sum += member.getTotalPowerContribution()
            effort = member.getTotalPowerContribution() / self.sharesSinceLastRound
            reward = BTCVALUE*effort
            reward *= 1-self.fees
            member.getMiner().giveWealth(reward)

    #Reward scheme for pay per last N shares
    def pplnsRewardMembers(self):
        n = min(len(self.sharesSubmitted), self.lastN)
        worthOfEachShare = BTCVALUE/n
        worthOfEachShare *= 1-self.fees
        for i in range(-1,-n - 1,-1):
            self.sharesSubmitted[i].giveWealth(worthOfEachShare)


    #This function is called by miners who wish to submit shares to the pool
    def recieveShares(self, minersMembershipWhoSubmitted):
        #self.sharesSubmitted += [minersMembershipWhoSubmitted]
        self.sharesSinceLastRound += minersMembershipWhoSubmitted.getCurrentContribution()

    #called by the model whenever a block is found
    def roundEnd(self):
        self.sharesSinceLastRound = 0

    #O(n) function that updates the total power of the group
    #(Try not to call this often)
    def recalcPoolPower(self):
        totalPower = 0
        for member in self.members:
            totalPower += member.getCurrentContribution()
        return totalPower








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
        self.totalPower = 0
        self.simulationTime = 0
        self.numberOfBlocksFound = 0
        self.blockFindingTimes = []

        #Activate the schedule 
        #(Random means that agents act in a random order each turn)
        self.schedule = RandomActivation(self)
        
        #Create pools
        self.pools = [Pool(0.00) for _ in range(self.numberOfPools)]

        #Create agents
        for index in range(self.numberOfMiners):
            #Here, we make a bunch of random miners with different strategies
            #Many changes will need to be made in order to change agent behaviours
            #For now, this is the placeholder agent setup

            #Total miner power
            powerToSpend = 10
            initialPTS = powerToSpend
            self.totalPower += powerToSpend

            #If the simulation has no pools then do the quicker miner creation
            if self.numberOfPools == 0:
                newMiner = Miner(index, self, powerToSpend, powerToSpend)
                self.schedule.add(newMiner)
                continue

            #Otherwise, if there are >0 pools then do the below code

            #Determine how independant the miner is
            percMineAlone = random.uniform(0,1)
            aloneMiningPower = 0 #initialPTS*percMineAlone
            powerToSpend -= aloneMiningPower

            #Sign the miner up to pools with the remaining power
            numberOfPoolMemberships = 1
            if self.numberOfPools > 1:
                numberOfPoolMemberships = self.numberOfPools #1+random.randrange(self.numberOfPools)
            powerPerPool = powerToSpend / numberOfPoolMemberships
            poolMemberships = []
            availablePools = [pool for pool in self.pools] #DeepCopy
            usedPools = []
            for _ in range(numberOfPoolMemberships):
                poolIndex = random.randrange(len(availablePools))
                pool = availablePools[poolIndex]
                usedPools.append(pool)
                del availablePools[poolIndex]
                poolMemberships.append(PoolMembership(pool,powerPerPool))

            if index == 0:
                aloneMiningPower = 0
                poolMemberships = [PoolMembership(pool,0) for pool in self.pools]
                poolMemberships[0].setCurrentContribution(powerToSpend)

            #Actually create the miner
            newMiner = Miner(index, self, initialPTS, aloneMiningPower, poolMemberships)
            self.schedule.add(newMiner)

            #Link now created miner to all their memberships
            for membership in poolMemberships:
                membership.linkToMiner(newMiner)
                membership.getPool().recruit(newMiner,membership)






        


    #Advance the model by a discrete step
    def step(self):
        self.simulationTime += 1
        #Miners search for shares and/or misbehave
        for miner in self.schedule.agents:
            miner.act()
        #Run below code if somebody has found a block
        if random.randint(1,self.puzzleDifficulty) == 1:
            self.numberOfBlocksFound += 1
            global passValue, blockFound
            passValue = random.uniform(0,1)*self.totalPower
            self.blockFindingTimes.append(self.simulationTime)
            self.simulationTime = 0
            self.schedule.step()
            blockFound = False
            for pool in self.pools:
                pool.roundEnd()
            for member in self.schedule.agents:
                for membership in member.poolMemberships:
                    membership.resetPowerContribution()


    #Standard accessor functions
    def getNoOfMiners(self):
        return self.numberOfMiners
    def getNoOfPools(self):
        return self.numberOfPools
    def getPuzzleDifficulty(self):
        return self.puzzleDifficulty
    def getPoolList(self):
        return self.pools
    def getNoOfBlocksFound(self):
        return self.numberOfBlocksFound

    #Function to assist with debugging and early output
    def showAgentDeets(self):
        print("\n\n\n")
        for miner in self.schedule.agents:
            print("ID: " + str(miner.id) + "\t\tPower: " + str(miner.power) 
                + "\tSoloMining Power: " + str(round(miner.soloDedicatedPower)) 
                + "\tNumber of pool memberships: " + str(len(miner.poolMemberships))
                + "\tWealth: " + str(miner.wealth))


    def showPoolDeets(self):
        print("\n")
        for i in range(len(self.getPoolList())):
            pool = self.getPoolList()[i]
            print("Pool #" + str(i))
            print("Number of members: " + str(len(pool.members)) + "\nTotal pool power: " + str(pool.recalcPoolPower()) + "\n")

    #Get number of pools each miner is a member of
    def getNumPoolsPerMiner(self):
        numPools = []
        for miner in self.schedule.agents:
            numPools.append(len(miner.poolMemberships))
        return numPools

    #List of miner's end wealths
    def getMinerWealth(self):
        minerWealths = []
        for miner in self.schedule.agents:
            minerWealths.append(miner.wealth)
        return minerWealths

    #List of miner's solo mining power
    def getSoloMiningPower(self):
        soloMiningPowers = []
        for miner in self.schedule.agents:
            soloMiningPowers.append(miner.soloDedicatedPower)
        return soloMiningPowers

    def getMinerID(self):
        minersID = []
        for miner in self.schedule.agents:
            minersID.append(miner.id)
        return minersID


    #A list of times representing when a block was found
    def getMiningTimes(self):
        return self.blockFindingTimes

    #Total number of blocks found during the run
    def getNumberOfBlocksFound(self):
        return len(self.blockFindingTimes)