import numpy as np
import config
from sklearn.dummy import DummyRegressor
from sklearn.preprocessing import OneHotEncoder, MinMaxScaler
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LinearRegression, Lasso
from sklearn.metrics import mean_squared_error as mse
from sklearn.metrics import r2_score as r2_score
import pandas as pd
from sklearn.cross_validation import ShuffleSplit
from sknn.mlp import Regressor, Layer


np.set_printoptions(precision=4)
np.set_printoptions(suppress=True)

# stolen from http://stackoverflow.com/questions/15722324/sliding-window-in-numpy
def window_stack(a, stepsize=1, width=3):
    return np.hstack( a[i:1+i-width or None:stepsize] for i in range(0,width) )

def get_linear_clf():
    lr = LinearRegression(n_jobs=2);
    #lr = Lasso()
    clf = make_pipeline(OneHotEncoder(categorical_features = [0],  sparse = False), MinMaxScaler(feature_range=(-0.5,0.5)), lr)
    return clf

def get_nn_clf():
    nn  = Regressor(
        layers=[
            # Convolution("Rectifier", channels=10, pool_shape=(2,2), kernel_shape=(3, 3)),
           Layer('Maxout', units=300, pieces=2),
           Layer('Maxout', units=300, pieces=2),
            Layer('Linear')],
        learning_rate=0.01,
        learning_rule='adagrad',
        learning_momentum=0.9,
        batch_size=20,
        valid_size= 0.1,
        n_iter=20,
        verbose=True)
    clf = make_pipeline(OneHotEncoder(categorical_features = [0],  sparse = False), MinMaxScaler(), nn)
    return clf

def get_dummy_clf():
    dummy = DummyRegressor()
    return dummy


def preprocess_data():
    df = pd.read_csv(config.data_file, index_col = None)
    print "Read data file with shape", df.values.shape
    hero_ids =  df.hero_id.unique()
    print "Creating sliding windows... "
    Xs = []
    ys = []
    for hero_id in hero_ids:
        print "Processing hero_id", hero_id
        # find all the hero movement
        hero_df = df[(df.hero_id == hero_id)].sort("timestamp")
        positions = hero_df[["timestamp","position_x","position_y"]].values
        width = 10
        #print positions
        slided_window = window_stack(positions[:,1:],width = width)
        timestamps = window_stack(positions[:,0:1],width = width)
        opp_pos_time =  timestamps[:,-1]

        opps_df = df[(df.timestamp.isin( opp_pos_time))]
        opps_df = opps_df[(opps_df.hero_id != hero_id)].sort(["timestamp", "hero_id"])

        opps_positions = opps_df[["position_x","position_y"]].values
        other_coords_shape = 9 * 2
        slided_positions = opps_positions.reshape(len(opp_pos_time),other_coords_shape)

        hero_X = np.ones((slided_window.shape[0],slided_window.shape[1]+other_coords_shape + 1))
        hero_X[:,1:19] = slided_positions
        hero_X[:,19:] = slided_window
        # diffs
        #hero_X = np.diff(hero_X, n=1, axis=-1)


        hero_X[:,0] = hero_df["hero_id"].values[:len(slided_window)]
        hero_y = hero_X[:,-2:]
        hero_y = MinMaxScaler(feature_range=(-1,1)).fit_transform(hero_y)
        print hero_y

        hero_X = np.delete(hero_X,[hero_X.shape[1]-1,hero_X.shape[1]-2 ], 1)


        # for x in hero_X:
        #     for p in range(1, len(x)-2):
        #         x[p] = x[p] - x[p+2]

        #hero_X = np.delete(hero_X,[hero_X.shape[1]-1,hero_X.shape[1]-2 ], 1)

        #
        # h_x_new = []
        # h_y_new = []
        # for i in range(len(hero_X)):
        #     if((hero_y[i]) == [0,0]).all():
        #         #print hero_X[i]
        #         pass
        #     else:
        #         h_x_new.append(hero_X[i])
        #         h_y_new.append(hero_y[i])
        #
        # #print hero_id
        # Xs.append(np.array(h_x_new))
        # ys.append(np.array(h_y_new))

        Xs.append(hero_X)
        ys.append(hero_y)

    X = np.concatenate(Xs)
    y = np.concatenate(ys)
    print X.shape, y.shape
    return X, y




def main():
    X,y = preprocess_data()
    dummy_clf = get_dummy_clf()
    dummy_clf.fit(X, y)
    y_hat = dummy_clf.predict(y)

    print "Dummy MSE x", mse(y[:,0], y_hat[:,0])
    print "Dummy MSE y", mse(y[:,1], y_hat[:,1])


    ss = ShuffleSplit(len(y), n_iter=5, random_state=0)

    scores_x = []
    scores_y = []
    for i, (train_index, test_index) in enumerate(ss):
        #print "Shuffle", i
        clf = get_linear_clf()
        #clf = get_nn_clf()
        clf.fit(X[train_index], y[train_index])
        y_hat = clf.predict(X[test_index])

        score_x = mse(y[test_index,0], y_hat[:,0])
        score_y = mse(y[test_index,1], y_hat[:,1])

        print clf.steps[-1][1].coef_,clf.steps[-1][1].intercept_

        scores_x.append(score_x)
        scores_y.append(score_y)
        print scores_x,scores_y

    print "MSE CV x", np.array(scores_x).mean()
    print "MSE CV y", np.array(scores_y).mean()




if __name__=="__main__":
    main()
