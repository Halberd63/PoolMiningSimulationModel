from sys import argv
from Simulation_Classes import *
from Simulation_Graphing import *






#Main function for running the simulation
#Params are pretty self explanitory 
#(Although it is worth noting that PuzzleDifficulty will be the... 
#...average number of cycles it will take to find each block)
def runSimulation():
    model = TheSimulation(open("Simulation_Specs.txt"))
    for _ in range(noOfCycles):
        model.step()
    model.showAgentDeets()
    model.showPoolDeets()
    return model

if __name__ == "__main__":
    theModel = runSimulation()
    graphBlocksFoundOverTime(theModel)
    graphWealthoverID(theModel)