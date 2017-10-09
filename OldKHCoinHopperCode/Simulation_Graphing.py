import plotly
plotly.tools.set_credentials_file(username='karlerikoja', api_key='tJQ6g692vFMVs89glb3v')
import plotly.graph_objs as go
import plotly.plotly as py


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

def graphWealthoverID(model):
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


def graphPoweroverID(model):
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