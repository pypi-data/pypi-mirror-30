#!/usr/bin/env python
# coding: utf-8

# # Implemented Expanstions:
#
# * Returns winning feature index
#
# ### Planned expansions:
# * Numpy
# * return actual winning feature

import numpy as np
import logging
import random

from pydgin import selections, serialization
from pydgin.analysis import Distribution

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class Agent(object):
    @classmethod
    def get_factory(cls, lr_coordinated, lr_uncoordinated, n_langs):
        def inner(race, native_lang):
            return cls(race=race,
                       lr_coordinated=lr_coordinated,
                       lr_uncoordinated=lr_uncoordinated,
                       native_lang=native_lang,
                       n_langs=n_langs)

        return inner

    def __init__(self, *, race, lr_coordinated, lr_uncoordinated, native_lang, n_langs):
        self.race = race
        self.lc = lr_coordinated
        self.lu = lr_uncoordinated
        self.set_native_language(native_lang, n_langs)

    def set_native_language(self, native_lang, n_langs):
        # initialises the langs array with the correct numer of
        # languages while setting their probabilities to 0.
        # Sets the probability of the native language to 1.
        self.langs = np.zeros(n_langs)
        self.langs[native_lang] = 1

    def speak(self):
        # returns a random language based on language probability array
        r = random.random()
        return np.argmax(self.langs.cumsum() > r)

    def update(self, my_lang, your_lang):
        # updates language probability array depending on language heard
        learning = self.lc if my_lang == your_lang else self.lu
        self.langs[your_lang] += learning * (1 - self.langs[your_lang])

        # Update languages I didn't hear
        # equivalent to old code:
        # -----------------------
        # for i in range(len(self.langs)):
        #     if i != your_lang:
        #         self.langs[i] -= learning * self.langs[i]
        # -----------------------

        unspoken_idx = np.arange(self.langs.size) != your_lang
        self.langs[unspoken_idx] -= learning * self.langs[unspoken_idx]


class Model(object):
    def __init__(self, population_deltas, epoch_lengths, select):
        self.population_deltas = population_deltas
        self.epoch_lengths = epoch_lengths
        self.select_partners = select

    def run(self, *, lr_coordinated, lr_uncoordinated, racists, verbose=False):
        # Initialisation
        agents = []
        groups = []
        n_langs = len(self.population_deltas[0])
        make_agent = Agent.get_factory(lr_coordinated, lr_uncoordinated, n_langs)
        for _ in range(n_langs):  # creates a new group for each demographic
            groups.append([])

        # Iteration
        n_days = np.sum(self.epoch_lengths)
        current_day = 1
        for time_index, t in enumerate(self.epoch_lengths):
            # Update population
            for lang_index, (group, group_delta) in enumerate(zip(groups, self.population_deltas[time_index])):
                if group_delta > 0:  # population growth
                    for _ in range(group_delta):
                        immigrant = make_agent(None, lang_index)
                        agents.append(immigrant)
                        group.append(immigrant)  # added to both population and group
                elif group_delta < 0:  # population decline
                    random.shuffle(group)
                    # group_delta is negative
                    for agent in group[group_delta:]:
                        agents.remove(agent)
                    del group[group_delta:]

            # Communicate
            for l in range(t):  # every agent communicates once a day
                if verbose:
                    print(f'\rDay {current_day} / {n_days}', end='', flush=True)
                current_day += 1
                if len(agents) == 1:
                    continue

                random.shuffle(agents)
                pairings = self.select_partners(agents)

                for me, you in pairings:
                    myLang = me.speak()
                    yourLang = you.speak()
                    if me.race != 'E':
                        me.update(myLang, yourLang)
                    if you.race != 'E':
                        you.update(yourLang, myLang)
            print(len(agents))

        if verbose:
            print()
        return Distribution(agents)


test_times = [10, 20, 30, 20, 10]
test_popdeltas = [[10, 0, 0],
                  [-5, 1, 3],
                  [5, 9, 7],
                  [-1, -1, -1],
                  [0, 0, 0]]

if __name__ == '__main__':
    pass
