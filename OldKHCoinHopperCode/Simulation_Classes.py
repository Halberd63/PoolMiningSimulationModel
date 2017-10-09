import random
import queue
from mesa import Agent, Model
from mesa.time import RandomActivation

#an arbitrary value used to denote wealth amongst miners
global BTCVALUE
BTCVALUE = 1000

#Variables that decide who actually found a block when one is found to be found
global passValue, currentValue, blockFound, blockAvailable, coins, currentCoin # We need a better names
passValue = 0
currentValue = 0
blockFound = False
blockAvailable = 0
coins = 0
currentCoin = 0



#An agent that represents a cryptocurrency miner
class Miner(Agent):
    def __init__(self, uniqueID, model, behaviour,coin=0):
        super().__init__(uniqueID, model)
        #Handle input arguments
        self.wealth = 0
        self.id = uniqueID
        #Computational power (This gets split between items in powerSplit)
        self.power = 1
        self.coin = coin
        #list of pools this miner needs to sign up for
        self.poolMemberships = []

        #decides how the miner will act
        self.behaviour = behaviour

        #the power dedicated to solo mining (if any)
        self.soloDedicatedPower = 0
        if behaviour == "LONEWOLF":
            self.soloDedicatedPower = self.power
        if behaviour == "2POOLHOPPER" or behaviour == "COINHOPPER": self.currentPool = 0


        #percentage of time the miner will stay with pool 1 if they are a hopper
        self.hopPercentage = 0.5

    #Give the miner wealth
    def giveWealth(self, wealth):
        self.wealth += wealth

    #Standard accessor functions
    def getPower(self):
        return self.power
    def getBehaviour(self):
        return self.behaviour
    def getID(self):
        return self.id

    #Standard mutator functions
    def setPower(self, p):
        self.power = p
        if behaviour == "LONEWOLF": self.soloDedicatedPower = self.power

    #Given a list of pools, this miner will create memberships to each pool to link up
    def setPoolMemberships(self, pList):
        for pool in pList:
            self.poolMemberships.append(PoolMembership(pool, self))

    #Each step, the miners try to solve puzzles
    def step(self):
        global blockFound, currentCoin
        if (self.soloDedicatedPower > 0):
            if self.isBlockFound(self.soloDedicatedPower) and self.coin == currentCoin:
                self.foundBlockSolo()
        for membership in self.poolMemberships:
            if membership.pool.coin == currentCoin:
                if not blockAvailable:
                    if self.behaviour == "HONEST": membership.currentContribution = self.power/len(self.poolMemberships)
                else:
                    if self.isBlockFound(membership.getCurrentContribution()):
                        self.foundPoolBlock(membership.getPool())
        if self.behaviour == "2POOLHOPPER":
            if random.random() < self.hopPercentage:
                self.poolMemberships[self.currentPool].currentContribution = 0
                self.currentPool = (self.currentPool+1)%len(self.poolMemberships)
            self.poolMemberships[self.currentPool].currentContribution = self.power
        if self.behaviour == "COINHOPPER":
            # if block has been just found jump into a new pool which mines current coin
            if blockFound:
                membershipsWithCurrentCoin = []
                for membership in range(len(self.poolMemberships)):
                    if self.poolMemberships[membership].pool.coin == currentCoin:
                        membershipsWithCurrentCoin.append(membership)
                if membershipsWithCurrentCoin != []:
                    self.poolMemberships[self.currentPool].currentContribution = 0
                    self.currentPool = membershipsWithCurrentCoin[
                        random.randint(0, len(membershipsWithCurrentCoin) - 1)]
                    self.poolMemberships[self.currentPool].currentContribution = self.power

            



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
        global passValue, currentValue, blockFound, blockAvailable
        if blockAvailable and not blockFound:
            currentValue += power
            if currentValue > passValue:
                if power == 0:
                    print("here")
                #currentValue = 0
                blockFound = True
                return True
        return False




#A linking class between a miner and their pool
#The class stores details such as:
#Total power contributed to the pool over history
#Current power contributed
#Length of time being a member
class PoolMembership:
    def __init__(self, pool, miner):
        #Handle input arguments
        self.pool = pool
        pool.members.append(self)
        self.miner = miner
        self.currentContribution = 0

        #Initialise history recording variables
        self.timeSinceJoining = 0
        self.totalPowerContributed = 0

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
    def makeShareContribution(self):
        self.timeSinceJoining += 1
        self.totalPowerContributed += self.currentContribution
    def resetShareContribution(self):
        self.timeSinceJoining = 0
        self.totalPowerContributed = 0



class Pool:
    def __init__(self, uniqueID, scheme, coin,N = 0):
        self.poolPower = 0
        #% of a block that the pool admin takes for themself
        self.fees = 0.02
        #list of members in the pool (poolmembership instances)
        self.members = []
        self.coin = coin

        #These variables are use to keep track of who submitted 
        #...what shares in order for PPLNS
        self.sharesSubmitted = queue.Queue()
        self.sharesSubmittedAmount = 0
        # Shares are equivalent to the average power contributed * number of ticks
        self.sharesSinceLastRound = 0 
        self.rewardScheme = scheme
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
        #if self.rewardScheme == "PPLNS":
        #    self.pplnsRewardMembers()
        #else: 
        self.propRewardMembers()

    #Function to give wealth to all members base on current input
    #Processing power (This is not accurate to real world as it
    #Does not consider shares, as such, only use it for testing)
    def propRewardMembers(self):
        print("Block was found!")
        for member in self.members:
            effort = member.getCurrentContribution() / (self.recalcPoolPower())
            reward = BTCVALUE*effort
            reward *= 1-self.fees
            member.getMiner().giveWealth(reward)

    #Reward scheme for pay per last N shares
    #UNUSED AND BROKEN
    #def pplnsRewardMembers(self):
    #    n = min(len(self.sharesSubmitted), self.lastN)
    #    worthOfEachShare = BTCVALUE/n
    #    worthOfEachShare *= 1-self.fees
    #    for i in range(-1,-n - 1,-1):
    #        self.sharesSubmitted[i].giveWealth(worthOfEachShare)


    #This function is called by miners who wish to submit shares to the pool
    def recieveShares(self, minersMembershipWhoSubmitted):
        #self.sharesSubmitted += [minersMembershipWhoSubmitted]
        shareValue = minersMembershipWhoSubmitted.getCurrentContribution()
        if self.rewardScheme == "PPLNS":
            self.sharesSubmittedAmount += shareValue

            self.sharesSubmitted.put([minersMembershipWhoSubmitted,shareValue])
        self.sharesSinceLastRound += shareValue

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
    def __init__(self, inFile):
        #Activate the schedule 
        #(Random means that agents act in a random order each turn)
        self.schedule = RandomActivation(self)

        self.interpretInput(inFile)


        #Handle the input arguments
        global coins
        self.simulationTime = [0 for _ in range(coins)]
        self.numberOfBlocksFound = 0
        self.blockFindingTimes = []





    #This interprets the file input into attribute for the simulation
    def interpretInput(self, inFile):
        global coins
        section = 0
        minerCount = 0
        poolCount = 0
        phMiners = []
        hMiners = []
        lwMiners = []
        pPools = []
        nPools = []
        for line in inFile:
            if line[0] == "#":
                section += 1
                if section == 5:
                    break
                continue

            if line[0] == ">":
                ci = line.index(',')
                pType = line[ci+2:len(line)-1]
                
                if pType == "Pool":
                    poolID = line[1:ci-1]
                    poolType = line[ci-1]
                elif pType == "Coins":
                    coins = int(line[1:ci])
                    print("number of coins: " + str(coins) + "\n")
                else:
                    number = float(line[1:ci])


                if section == 1:
                    for _ in range(int(number)):
                        if pType == "2-Pool-Hoppers":
                            #Make number default poolhoppers
                            minerCount += 1
                            phMiners.append(Miner(minerCount,self,"2POOLHOPPER"))

                        if pType == "Coin-Hoppers":
                            minerCount += 1
                            phMiners.append(Miner(minerCount,self,"COINHOPPER",random.randint(0,coins-1)))

                        if pType == "Honest":
                            #Make number default honest miners
                            minerCount += 1
                            hMiners.append(Miner(minerCount,self,"HONEST"))

                        if pType == "Lone-Wolf":
                            #Make number default loneWolf miners
                            minerCount += 1
                            lwMiners.append(Miner(minerCount,self,"LONEWOLF",random.randint(0,coins-1)))

                if section == 2:
                    for _ in range(int(number)):
                        if pType == "Proportional":
                            #Make proportianal pools
                            poolCount += 1
                            pPools.append(Pool(poolCount,"PROPORTIONAL",random.randint(0,coins-1)))

                        if pType[:5] == "PPLNS":
                            theN = int(pType[11:])
                            #Make pplns pools
                            poolCount += 1
                            nPools.append(Pool(poolCount,"PPLNS", theN,random.randint(0,coins-1)))
                if section == 4:
                    if pType == "Difficulty":
                        self.puzzleDifficulty = number
                        
        miners = phMiners + hMiners + lwMiners
        self.pools = nPools + pPools
        self.numberOfMiners = minerCount
        self.numberOfPools = poolCount
        self.totalPower = [0 for _ in range(coins)]
        for miner in miners:
            if miner.getBehaviour() == "HONEST" or len(self.pools) == 1:
                assert len(self.pools) >= 1, "Too few pools for non-lonewolves"
                miner.setPoolMemberships(self.pools)
                for membership in miner.poolMemberships:
                    membership.currentContribution = miner.power / len(miner.poolMemberships)

            elif miner.getBehaviour() == "2POOLHOPPER" or miner.getBehaviour() == "COINHOPPER":
                assert len(self.pools) >= 2, "Too few pools for pool hoppers"
                miner.setPoolMemberships(self.pools)
                miner.poolMemberships[0].currentContribution = miner.power
            self.schedule.add(miner)









    #Advance the model by a discrete step
    def step(self):
        global blockAvailable, coins, currentCoin, blockFound
        for coin in range(coins):
            self.simulationTime[coin] += 1
            blockAvailable = False
            blockFound = False
            currentCoin = coin
            totalCoinPower = 0
            for pool in self.pools:
                if pool.coin == coin: totalCoinPower += pool.recalcPoolPower()
            self.totalPower[coin] = totalCoinPower
        #Miners search for shares and/or misbehave
        
        #Run below code if somebody has found a block
            if random.randint(1,self.puzzleDifficulty) == 1:
                self.numberOfBlocksFound += 1
                global passValue, currentValue
                blockAvailable = True
                passValue = random.uniform(0,1)*self.totalPower[coin]
                self.blockFindingTimes.append(self.simulationTime[coin])
                self.simulationTime[coin] = 0
                blockFound = False
                self.schedule.step()
                currentValue = 0
                for pool in self.pools:
                    pool.roundEnd()
                for member in self.schedule.agents:
                    for membership in member.poolMemberships:
                        membership.resetShareContribution()
            else:
                pass
                #self.schedule.step()



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

    #List of miner's end powers
    def getMinerPower(self):
        minerPowers = []
        for miner in self.schedule.agents:
            minerPowers.append(miner.power)
        return minerPowers

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