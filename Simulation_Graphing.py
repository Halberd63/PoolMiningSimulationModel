import plotly
plotly.tools.set_credentials_file(username='karlerikoja', api_key='tJQ6g692vFMVs89glb3v')
import plotly.graph_objs as go
import plotly.plotly as py
import matplotlib.pyplot as plt


#This graph is mostly used to prove our algorithm works correctly
def graphBlocksFoundOverTime(model):
    #Code for proving that the block finding is calculated correctly
    miningTimes = model.getMiningTimes()
    miningTimes.sort()
    print(miningTimes)
    numberOfBlocksOverTime = []
    for i in range(1,miningTimes[-1]+1):
        for j in range(len(miningTimes)):
            if i < miningTimes[j]:
                numberOfBlocksOverTime.append(j)
                break
    print(numberOfBlocksOverTime)

    trace = go.Scatter(
        x = [i for i in range(miningTimes[-1]+1)],
        y = numberOfBlocksOverTime,
        mode = 'markers'
    )
    data = [trace]
    layout = go.Layout(
        title = "Number of Blocks Mined over Time",
        titlefont = dict(
            size = 32
        ),
        xaxis = dict(
            title = "Time",
            titlefont = dict(
                size = 18
            )
        ),
        yaxis = dict(
            title = "Number of Blocks Found Within Given Time",
            titlefont = dict(
                size = 18
            )
        )
    )
    py.plot(go.Figure(data = data, layout = layout)
        , filename='Number of blocks mined vs time')






#This graph is mostly used to prove our algorithm works correctly
def graphWealthoverIndependance(model):
    trace = go.Scatter(
        x = model.getSoloMiningPower(),
        y = model.getMinerWealth(),
        mode = 'markers'
    )
    data = [trace]
    layout = go.Layout(
        title = "Miner Wealth vs Miner Independance",
        titlefont = dict(
            size = 32
        ),
        xaxis = dict(
            title = "Processing Power Dedicated to Mining Alone",
            titlefont = dict(
                size = 18
            )
        ),
        yaxis = dict(
            title = "Wealth of the Miner",
            titlefont = dict(
                size = 18
            )
        )
    )
    py.plot(go.Figure(data = data, layout = layout)
        , filename='Solo Power vs Wealth')

def graphWealthoverID_Legacy(model):
    trace = go.Scatter(
        x=model.getMinerID(),
        y=model.getMinerWealth(),
        mode='markers'
    )
    data = [trace]
    layout = go.Layout(
        title="Miner Wealth vs ID",
        titlefont=dict(
            size=32
        ),
        xaxis=dict(
            title="Miners",
            titlefont=dict(
                size=18
            )
        ),
        yaxis=dict(
            title="Wealth of the Miner",
            titlefont=dict(
                size=18
            )
        )
    )
    py.plot(go.Figure(data=data, layout=layout)
            , filename='MinerID vs Wealth')


def graphPoweroverID_Legacy(model):
    trace = go.Scatter(
        x=model.getMinerID(),
        y=model.getMinerPower(),
        mode='markers'
    )
    data = [trace]
    layout = go.Layout(
        title="Miner Power vs ID",
        titlefont=dict(
            size=32
        ),
        xaxis=dict(
            title="Miners",
            titlefont=dict(
                size=18
            )
        ),
        yaxis=dict(
            title="Power of the Miner",
            titlefont=dict(
                size=18
            )
        )
    )
    py.plot(go.Figure(data=data, layout=layout)
            , filename='MinerPower vs Wealth')





def graphPoweroverID(model):
    x=model.getMinerID()
    y=model.getMinerPower()
    plt.plot(x,y)
    plt.xlabel('Miner ID')
    plt.ylabel('Miner Power')
    plt.title('Miner Power vs ID')
    plt.show()

def graphWealthoverID(model):
    x=model.getMinerID()
    y=model.getMinerWealth()
    plt.plot(x,y, 'ro')
    plt.xlabel('Miner ID')
    plt.ylabel('Miner Wealth')
    plt.title('Miner Wealth vs ID')
    plt.show()
        
def getCSVOutput(model):
    outFile = open('CSVOutput.txt', 'w')
    miners = model.schedule.agents
    for miner in miners:
        outFile.write(str(miner.id) + ",")
        outFile.write(str(miner.behaviour) + ",")
        outFile.write(str(miner.wealth) + ",")
        outFile.write(str(miner.power) + ",")
        outFile.write(str(miner.poolMemberships[0].pool) + "\n")
    outFile.close()

    # outFile = open('CSVBlocksFound.txt', 'w')
    # miningTimes = model.getMiningTimes()
    # miningTimes.sort()
    # print(miningTimes)
    # numberOfBlocksOverTime = []
    # for i in range(1,miningTimes[-1]+1):
    #     for j in range(len(miningTimes)):
    #         if i < miningTimes[j]:
    #             numberOfBlocksOverTime.append(j)
    #             break
    # print(numberOfBlocksOverTime)
    #
    # for i in range(miningTimes[-1]+1):
    #     outFile.write(str(miningTimes[i]) + ",")
    #     outFile.write(str(numberOfBlocksOverTime[i]) + "\n")
    #
    # outFile.close()
