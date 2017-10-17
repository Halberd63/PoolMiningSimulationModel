from sys import argv
from Simulation_Classes import *
from Simulation_Graphing import *
import time






#Main function for running the simulation
#Params are pretty self explanitory 
#(Although it is worth noting that PuzzleDifficulty will be the... 
#...average number of cycles it will take to find each block)
def runSimulation():
    inFile = open("Simulation_Specs.txt", 'r')
    model = TheSimulation(inFile)
    inFile.close()
    
    #Get number of cycles
    inFile = open("Simulation_Specs.txt", 'r')
    for line in inFile:
        cycles = int(line[1:line.index(',')])
        break
    inFile.close()

    for i in range(cycles):
        model.step()
        if i%1000 == 0:
            #Spends too much time on printing percentage
            print(str(100 * i / cycles) + "%")
    #model.showAgentDeets()
    #model.showPoolDeets()
    model.showFocussedMinerDeets()
    return model

if __name__ == "__main__":
    theModel = runSimulation()
    #graphBlocksFoundOverTime(theModel)
    graphWealthoverID(theModel)
    getCSVOutput(theModel)
    #graphPoweroverID(theModel)