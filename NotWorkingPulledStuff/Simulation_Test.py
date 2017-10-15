from Simulation import *

#Test cases for the simulation
def testSimulation():
    #Model Tests
    N = 10
    P = 0
    D = 1
    theModel = TheSimulation(N,P,D)
    assert theModel.numberOfMiners == N, (
        "Test failed- Basic simulation construction incorrect (Wrong N)")
    assert theModel.numberOfPools == P, (
        "Test failed- Basic simulation construction incorrect (Wrong P)")
    assert theModel.puzzleDifficulty == D, (
        "Test failed- Basic simulation construction incorrect (Wrong D)")
    assert len(theModel.blockFindingTimes) == 0, (
        "Test failed- Basic simulation construction incorrect (Block finding times initialised wrong)")
    assert theModel.numberOfBlocksFound == 0, (
        "Test failed- Basic simulation construction incorrect (Total block count initialised wrong)")


    assert theModel.totalPower == N*10, (
        "Test failed- Creation of Miners is incorrect (Assuming they each have 10 power)")
    assert sum(theModel.getMinerWealth()) == 0, (
        "Test failed- Calculation of miner wealths isnt functioning correctly on initial state")
    assert sum(theModel.getNumPoolsPerMiner()) == 0, (
        "Test failed- Calculation of miner wealths isnt functioning correctly on initial state")

    theModel.step()

    assert theModel.numberOfBlocksFound == 1, (
        "Test failed- Block wasnt found once a cycle as 'D' says it should")
    assert len(theModel.blockFindingTimes) == 1, (
        "Test failed- Block times not being added to block time list")
    assert round(sum(theModel.getMinerWealth())) == BTCVALUE, (
        "Test failed- Calculation of miner wealths isnt functioning correctly after step()")
    assert theModel.totalPower == N*10, (
        "Test failed- Mining power shouldn't change over time (Assuming they each have 10 power)")



if __name__ == '__main__':
    testSimulation()
    print("Passed all tests!")