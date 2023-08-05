from pydgin import serialization, selections, fastmodel


def run_some_model():
    """ Just run any old model and return the distribution.

    For testing purposes."""
    with open('inputs/useful_features_with_mc.txt', 'r') as featurefile:
        all_features = serialization.parse_matrix(featurefile)

    with open('inputs/Demography.txt') as demofile, open('inputs/Time.txt') as timefile:
        popdeltas = serialization.parse_matrix(demofile)
        epochs = serialization.parse_vector(timefile)
    m = fastmodel.FastModel(population_deltas=popdeltas,
                            epoch_lengths=epochs,
                            select=selections.fast_cold_shoulder,
                            lr_coordinated=0.1,
                            lr_uncoordinated=0.097,
                            racists=False,
                            plantation_epoch=365 * 7,
                            verbosity=fastmodel.Verbosity.silent,
                            randomseed='butts',
                            promotion_age=730,
                            )
    return m.run(all_features[-1])


def main():
    dist = run_some_model()
    means = dist.mean_features
    nz_idx = means != 0
    print(means[nz_idx])
    with open('outputs_log', 'a+') as outfile:
        outfile.write(str(means[nz_idx]) + '\n')


main()
