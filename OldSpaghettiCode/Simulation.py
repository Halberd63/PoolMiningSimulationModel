from sys import argv
from Simulation_Classes import *
from Simulation_Graphing import *






#Main function for running the simulation
#Params are pretty self explanitory 
#(Although it is worth noting that PuzzleDifficulty will be the... 
#...average number of cycles it will take to find each block)
def runSimulation(noOfMiners,noOfPools,puzzleDifficulty,noOfCycles):
    model = TheSimulation(noOfMiners,noOfPools,puzzleDifficulty)
    for _ in range(noOfCycles):
        model.step()
    model.showAgentDeets()
    model.showPoolDeets()
    minersVsWealth(model)
    return model

runSimulation(20,50,100,10000)

if __name__ == "__main__":
    if (len(argv) < 2):
        print("Usage: Simulation.py No_of_Miners No_of_Pools" 
            + " Puzzle_Difficulty No_of_Cycles")
    else:
        theModel = runSimulation(int(argv[1]),int(argv[2]),int(argv[3]),int(argv[4]))
        graphBlocksFoundOverTime(theModel)
        graphWealthoverIndependance(theModel)