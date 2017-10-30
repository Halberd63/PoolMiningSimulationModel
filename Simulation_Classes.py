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


#C0 - Number of cycles
#C1 – number of full solutions found when the miner is with coin_1;
#C2 – total number of full solutions found in coin_1; 
#C3 – number of iterations when the miner is with coin_1; 
#C4 – number of iterations since the beginning of the current hopping period


#An agent that represents a cryptocurrency miner
class Miner(Agent):
    def __init__(self, uniqueID, model, behaviour,coin=0,beta = 0, delta = 0, power = 1):
        super().__init__(uniqueID, model)
        #Handle input arguments
        self.wealth = 0
        self.id = uniqueID
        #Computational power (This gets split between items in powerSplit)
        self.power = power
        self.coin = coin
        self.beta = beta
        self.delta = delta

        self.C1 = 0
        self.C2 = 0
        self.C3 = 0
        self.C4 = 0

        #list of pools this miner needs to sign up for
        self.poolMemberships = []

        #decides how the miner will act
        self.behaviour = behaviour

        #the power dedicated to solo mining (if any)
        self.soloDedicatedPower = 0
        if behaviour == "LONEWOLF":
            self.soloDedicatedPower = self.power
        if behaviour == "2POOLHOPPER" or behaviour == "COINHOPPER" or behaviour == "YEVCOINHOP": self.currentPool = coin


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


        #Mining mechanics-----------------------------------------------
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




        #Hopping mechanics--------------------------------------------
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
        if self.behaviour == "YEVCOINHOP":

            minedCoin = self.poolMemberships[self.currentPool].pool.coin

            if minedCoin == self.coin: self.C3 += 1
            #print(str(minedCoin) + " " + str(self.coin) + " ----- " + str(self.C3))
            
            hop = 0
            if self.C4 == round(self.beta*self.delta):
                hop = 2
            if self.C4 == round(self.delta): hop = 1
            if blockFound and currentCoin == self.coin: 
                hop = 1
                if minedCoin == self.coin: self.C1 += 1
                self.C2 += 1
            self.C4 += 1

            if hop == 1: self.C4 = 0
            if hop == 2 and minedCoin == self.coin:
                SecondaryCoins = []
                for membership in range(len(self.poolMemberships)):
                    if self.poolMemberships[membership].pool.coin != self.coin:
                        SecondaryCoins.append(membership)
                if SecondaryCoins != []:
                    self.poolMemberships[self.currentPool].currentContribution = 0
                    self.currentPool = SecondaryCoins[
                        random.randint(0, len(SecondaryCoins) - 1)]
                    self.poolMemberships[self.currentPool].currentContribution = self.power
                    
            if hop == 1 and minedCoin != self.coin:
                PrimaryCoins = []
                for membership in range(len(self.poolMemberships)):
                    if self.poolMemberships[membership].pool.coin == self.coin:
                        PrimaryCoins.append(membership)
                if PrimaryCoins != []:
                    self.poolMemberships[self.currentPool].currentContribution = 0
                    self.currentPool = PrimaryCoins[
                        random.randint(0, len(PrimaryCoins) - 1)]
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
        self.fees = 0#0.02
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
        #print("Block was found!")
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
        self.tickNumber = 0

        self.interpretInput(inFile)


        #Handle the input arguments
        global coins
        self.simulationTime = [0 for _ in range(coins)]
        self.numberOfBlocksFound = 0
        self.blockFindingTimes = []

        # calculate initial power of coin
        for coin in range(coins):
            totalCoinPower = 0
            for pool in self.pools:
                if pool.coin == coin: totalCoinPower += pool.recalcPoolPower()
            self.totalPower[coin] = totalCoinPower



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
        self.focussedMiners = []
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

                        if pType[:16] == "Yev-Coin-Hoppers":
                            params = pType[26:].split()
                            minerCount += 1
                            # yevCoinHopper = Miner(minerCount,self,"YEVCOINHOP",0
                            #     ,float(params[0]),int(params[1]),int(params[2]))
                            yevCoinHopper = Miner(minerCount,self,"YEVCOINHOP",random.randint(0,coins-1)
                                ,float(params[0]),int(params[1]),int(params[2]))
                            phMiners.append(yevCoinHopper)
                            self.focussedMiners.append(yevCoinHopper)
                            print("Made yevcoinhopper")

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
                        if pType[:26] == "Proportional-With-Set-Coin":
                            theC = int(pType[27:])
                            assert theC < coins, "Too few coins for 'Proportional-With-Set-Coin' pool"
                            #Make proportianal pools
                            poolCount += 1
                            pPools.append(Pool(poolCount,"PROPORTIONAL",theC))
                            print("Made set coin pools")
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
        self.minersTotalPower = minerCount
        self.totalPower = [0 for _ in range(coins)]
        for miner in miners:
            if miner.getBehaviour() == "HONEST" or len(self.pools) == 1:
                assert len(self.pools) >= 1, "Too few pools for non-lonewolves"
                miner.setPoolMemberships(self.pools)
                miner.setPoolMemberships([self.pools[random.randint(0,len(self.pools)-1)]])
                for membership in miner.poolMemberships:
                    membership.currentContribution = miner.power / len(miner.poolMemberships)

            elif miner.getBehaviour() == "2POOLHOPPER" or miner.getBehaviour() == "COINHOPPER"or miner.getBehaviour() == "YEVCOINHOP":
                assert len(self.pools) >= 2, "Too few pools for pool hoppers"
                miner.setPoolMemberships(self.pools)
                miner.poolMemberships[miner.coin].currentContribution = miner.power
            self.schedule.add(miner)






    def printLoadBar(self):
        print(self.tickNumber)



    #Advance the model by a discrete step
    def step(self):
        #self.printLoadBar()

        self.tickNumber += 1
        global blockAvailable, coins, currentCoin, blockFound
        # hasStepped = False
        # Calculate the power for each coin before new time unit starts
        for coin in range(coins):
            hasStepped = False
            self.simulationTime[coin] += 1
            blockAvailable = False
            blockFound = False
            currentCoin = coin
            currentTotalCoinPower = 0
            for pool in self.pools:
                if pool.coin == coin: currentTotalCoinPower += pool.recalcPoolPower()
        
        # Run below code if somebody has found a block
            #print(self.puzzleDifficulty)
            # print(self.totalPower[coin])
            # print(hopperPower)
            if currentTotalCoinPower == 0:
                # If current power in coin is 0 make it almost impossible to find a block.
                currentTotalCoinPower = 0.000000001
            if random.randint(1,int(self.puzzleDifficulty*(self.totalPower[coin])/currentTotalCoinPower)) == 1:

                #coin = random.randint(0,coins - 1)
                # currentCoin = coin
                # print(coin)
                self.numberOfBlocksFound += 1
                global passValue, currentValue
                blockAvailable = True
                passValue = random.uniform(0,1)*self.totalPower[coin]
                self.blockFindingTimes.append(self.simulationTime[coin])
                self.simulationTime[coin] = 0
                blockFound = False
                self.schedule.step()
                hasStepped = True
                currentValue = 0
                for pool in self.pools:
                    pool.roundEnd()
                for member in self.schedule.agents:
                    for membership in member.poolMemberships:
                        membership.resetShareContribution()

        if not hasStepped: self.schedule.step()



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

    #Specialised output for yevhens coinhopping miner to print their counters
    def showFocussedMinerDeets(self):
        print("\n\n\n")
        if len(self.focussedMiners) != 0:
            averageWealth = 0
            for miner in self.schedule.agents:
                if miner not in self.focussedMiners:
                    averageWealth += miner.wealth
            averageWealth /= (len(self.schedule.agents)-len(self.focussedMiners))
            averageWealthCoinHop = 0
            averageC1 = 0
            averageC2 = 0
            averageC3 = 0
            for miner in self.schedule.agents:
                if miner in self.focussedMiners:
                    averageWealthCoinHop += miner.wealth
                    averageC1 += miner.C1
                    averageC2 += miner.C2
                    averageC3 += miner.C3
            averageWealthCoinHop /= len(self.focussedMiners)
            averageC1 /= len(self.focussedMiners)
            averageC2 /= len(self.focussedMiners)
            averageC3 /= len(self.focussedMiners)
            print("The Yevhen-Coin-Hopper:\nWealth / AvePeerWealth = " + str(averageWealthCoinHop / averageWealth)
                + "\nC0 = " + str(self.tickNumber)
                + "\nC1 = " + str(averageC1)
                + "\nC2 = " + str(averageC2)
                + "\nC3 = " + str(averageC3))
            print("C1/C2 - C3/C0 = " + str(averageC1/averageC2 - averageC3/self.tickNumber))


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