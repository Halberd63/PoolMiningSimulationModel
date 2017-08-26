import random
from mesa import Agent, Model
from mesa.time import RandomActivation

class Miner(Agent):
    """An agent with fixed initial wealth."""
    def __init__(self, unique_id, model, power):
        super().__init__(unique_id, model)
        self.wealth = 1
        self.power = power
        self.id = unique_id
    def step(self):
        print(self.id)

class Pool (Model):
    """A model with some number of agents."""
    def __init__(self, N):
        self.num_agents = N
        self.schedule = RandomActivation(self)
        # Create agents
        self.pool_power = N
        for i in range(self.num_agents):
            a = Miner(i, self, 1)
            self.schedule.add(a)

    def step(self):
        '''Advance the model by one step.'''
        self.schedule.step()


model = Pool(10)
model.step()