import numpy as np

from pydgin import fastmodel


def random(agents):
    us = np.asarray(agents)  # Should be an array of objects; we're just going to use boolean stuff on them
    them = np.random.choice(us, size=len(agents), replace=True)

    while np.any(us == them):
        # Whittle down the bits of "them" where they would result in an agent speaking to itself
        idx = us == them
        them[idx] = np.random.choice(us, size=np.count_nonzero(idx), replace=True)

    return zip(us, them)


def _cold_shoulder_gen(pairings):
    for me, you in pairings:
        if me.race == 'E' and you.race == 'B' and np.random.random() > epsilon:
            continue
        yield me, you


def cold_shoulder(agents, epsilon):
    pairings = random(agents)
    return _cold_shoulder_gen(pairings)


def _segregated_gen(pairings, epsilon):
    for me, you in pairings:
        if me.race == 'E' and you.race == 'B' and np.random.random() > epsilon:
            # Reselect
            while you.race == 'B':
                you = np.random.choice(us)
        yield me, you


def segregated(agents, epsilon):
    # select random partner that isn't themselves
    pairings = random(agents)
    return _segregated_gen(pairings, epsilon)


# Fastmodel selection mechanisms below
# TODO: make fastmodel and model use the same selection functions
def randomselect(population):
    us = np.arange(population.population_size)
    them = np.random.choice(us, size=us.size, replace=True)
    while np.any(us == them):
        # Madmen are talking to themselves
        madmen_bidx = us == them
        them[madmen_bidx] = np.random.choice(us, size=np.count_nonzero(madmen_bidx), replace=True)
    return us, them

class FastColdShoulder:
    def __init__(self, epsilon: float):
        self.epsilon = epsilon

    def __call__(self, population: fastmodel.FastPopulation):
        us_idx, them_idx = randomselect(population)

        # (white, black) pair
        our_whites = population.races[us_idx] == fastmodel.european
        their_blacks = population.races[them_idx] == fastmodel.black
        random_numbers = np.random.random(size=our_whites.shape)
        cold_idx = np.logical_and(np.logical_and(our_whites, their_blacks), random_numbers > self.epsilon)

        # (black, white) pair
        our_blacks = population.races[us_idx] == fastmodel.black
        their_whites = population.races[them_idx] == fastmodel.european
        random_numbers = np.random.random(size=our_blacks.shape)
        cold_idx2 = np.logical_and(np.logical_and(our_blacks, their_whites), random_numbers > self.epsilon)

        warm_idx = np.logical_not(np.logical_or(cold_idx, cold_idx2))
        return us_idx[warm_idx], them_idx[warm_idx]

    @property
    def __name__(self):
        return f'{self.__class__.__name__}({self.epsilon})'

class FastSegregation:
    def __init__(self, epsilon: float):
        self.epsilon = epsilon

    def __call__(self, population: fastmodel.FastPopulation):
        us_idx, them_idx = randomselect(population)

        # (white, black) pair
        our_whites = population.races[us_idx] == fastmodel.european
        their_blacks = population.races[them_idx] == fastmodel.black
        random_numbers = np.random.random(size=our_whites.shape)
        to_be_replaced = np.logical_and(np.logical_and(our_whites, their_blacks), random_numbers > self.epsilon)
        while np.any(to_be_replaced):
            them_idx[to_be_replaced] = np.random.choice(us_idx, size=np.count_nonzero(to_be_replaced), replace=True)
            their_blacks = population.races[them_idx] == fastmodel.black
            to_be_replaced = np.logical_and(np.logical_and(our_whites, their_blacks), random_numbers > self.epsilon)

        # (black, white) pair
        our_blacks = population.races[us_idx] == fastmodel.black
        their_whites = population.races[them_idx] == fastmodel.european
        random_numbers = np.random.random(size=our_blacks.shape)
        to_be_replaced = np.logical_and(np.logical_and(our_whites, their_blacks), random_numbers > self.epsilon)
        while np.any(to_be_replaced):
            them_idx[to_be_replaced] = np.random.choice(us_idx, size=np.count_nonzero(to_be_replaced), replace=True)
            their_whites = population.races[them_idx] == fastmodel.european
            to_be_replaced = np.logical_and(np.logical_and(our_blacks, their_whites), random_numbers > self.epsilon)

        return us_idx, them_idx

    @property
    def __name__(self):
        return f'{self.__class__.__name__}({self.epsilon})'

