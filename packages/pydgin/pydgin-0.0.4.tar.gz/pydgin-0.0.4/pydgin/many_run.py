import datetime
import itertools
import time
import typing
import pickle

import numpy as np

from pydgin import multiprocess, selections, serialization


def timestr():
    return datetime.datetime.now().strftime('%c')


def build_tee_print(fd: typing.TextIO):
    def tee_print(msg: str, *, end='\n'):
        print(msg, end=end)
        fd.write(msg + end)

    return tee_print


def similarity(lang_a, lang_b):
    return np.mean(lang_a == lang_b)


default_all = {
    'lcs': [0.01, 0.02, 0.03, 0.1, 0.2, 0.3, 0.4, 0.5],
    'lu_diffs': np.arange(0.003, 0.01, 0.001),
    'racisms': [True, False],
    'selections': [selections.randomselect, selections.FastSegregation(0.1), selections.FastColdShoulder(0.1)],
    'plantation_epochs': [2874, 3058, 3122, 3213, None],
    'promotion_ages': list(np.asarray([2, 3, 4, 8, 10]) * 365) + [None],
}


class MultiRunner:
    """ Runs the simulation against a full feature set with every possible combination of given inputs. """

    @classmethod
    def from_paths(cls, population_deltas_path, epochs_path, all_features_path, **kwargs):
        with open(population_deltas_path, 'r') as population_deltas_fd, \
                open(epochs_path, 'r') as epochs_fd, \
                open(all_features_path, 'r') as all_features_fd:
            return cls.from_files(population_deltas_fd, epochs_fd, all_features_fd, **kwargs)

    @classmethod
    def from_files(cls, population_deltas_fd, epochs_fd, all_features_fd, **kwargs):
        return cls(serialization.parse_matrix(population_deltas_fd),
                   serialization.parse_vector(epochs_fd),
                   serialization.parse_matrix(all_features_fd),
                   **kwargs)

    def __init__(self, population_deltas, epochs, all_features, log_func=None, n_processes=6):
        self.population_deltas = population_deltas
        self.epochs = epochs
        self.all_features = all_features
        self.mauritian_creole = all_features[:, 0]
        self.french = all_features[:, 1]
        self.log = log_func or print
        self.n_processes = n_processes

    def _distribution_one(self, lc, lu, racism, select_func, plantation_epoch, promotion_age):
        distributions_promise = multiprocess.run_all_features(
            self.all_features,
            self.population_deltas,
            self.epochs,
            lc, lu, select_func, racism,
            plantation_epoch, promotion_age,
            n_processes=self.n_processes,
        )
        return distributions_promise.wait()

    def simulate_all_combinations(self, *, lcs, lu_diffs, racisms, selections, plantation_epochs, promotion_ages):
        remaining_iterations = len(list(itertools.product(
            racisms, selections, plantation_epochs, lcs, lu_diffs, promotion_ages
        )))
        outputs = {}
        tooks = []

        for racism, select_func, plantation_epoch, promotion_age in itertools.product(racisms, selections,
                                                                                      plantation_epochs,
                                                                                      promotion_ages):
            predictions = {}
            for lc in lcs:
                for lu_d in lu_diffs:
                    lu = lc - lu_d

                    # Log some stuff
                    header = (f'Learning: {lc:8.2f} | {lu:8.3f}    '
                              f'Europeans learn: {"no " if racism else "yes"}    '
                              f'Selection function: {select_func.__name__}')
                    self.log('=' * len(header))
                    self.log(header)
                    self.log('-' * len(header))
                    self.log(f'{timestr()}\tRunning simulation...')

                    # Track time
                    start_time = time.time()

                    # Actually calculate the thing
                    distributions = self._distribution_one(
                        lc, lu, racism, select_func, plantation_epoch, promotion_age
                    )

                    # Put it in the output
                    predicted_language = [dist.winning_feature_index for dist in distributions]
                    predictions.setdefault(lc, {})[lu] = predicted_language

                    # Continue tracking time
                    end_time = time.time()
                    tooks.append(end_time - start_time)
                    eta = remaining_iterations * np.mean(
                        tooks) * 1.5  # 1.5 seems to make it more accurate for now
                    remaining_string = f'{eta // 3600} hours and {eta // 60 % 60} minutes'

                    # Log time
                    self.log(
                        f'{timestr()}\tDone simulating, took {tooks[-1]:.2f}s, '
                        f'{remaining_iterations} runs remain, estimate finished in {remaining_string}'
                    )
                    remaining_iterations -= 1
                outputs[(racism, select_func.__name__, plantation_epoch, promotion_age)] = predictions
        return outputs


def main():
    runner = MultiRunner.from_paths('inputs/Demography.txt', 'inputs/Time.txt', 'inputs/useful_features_with_mc.txt')
    outputs = runner.simulate_all_combinations(
        lcs=[0.01],
        lu_diffs=[0.001],
        racisms=[False],
        selections=[selections.FastColdShoulder(0.1)],
        plantation_epochs=[None],
        promotion_ages=[None],
    )
    serialization.save_many_run(outputs, 'outputs/db.pkl')

if __name__ == '__main__':
    main()