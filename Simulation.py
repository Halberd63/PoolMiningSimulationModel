from sys import argv
from Simulation_Classes import *
from Simulation_Graphing import *






#Main function for running the simulation
#Params are pretty self explanitory 
#(Although it is worth noting that PuzzleDifficulty will be the... 
#...average number of cycles it will take to find each block)
def runSimulation():
    inFile = open("Simulation_Specs.txt", 'r')
    model = TheSimulation(inFile)
    
    for _ in range(1000):
        model.step()
    #model.showAgentDeets()
    #model.showPoolDeets()
    return model

if __name__ == "__main__":
    theModel = runSimulation()
    graphBlocksFoundOverTime(theModel)
    graphWealthoverID(theModel)