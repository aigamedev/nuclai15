# -*- coding: utf-8 -*-
"""\
Learning from DOTA2 data
=================================================
"""

print(__doc__)

import numpy as np
import config
from sklearn.dummy import DummyRegressor
from sklearn.preprocessing import OneHotEncoder, MinMaxScaler
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error as mse
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
    clf = make_pipeline(OneHotEncoder(categorical_features = [0],  sparse = False), MinMaxScaler(), lr)
    return clf

def get_nn_clf():
    nn  = Regressor(
        layers=[
          # Layer('Maxout', units=300, pieces=2),
          # Layer('Maxout', units=300, pieces=2),
            Layer('Rectifier', units=500),
            Layer('Rectifier', units=500),
            Layer('Linear')],
        learning_rate=0.1,
        learning_rule='adagrad',
        learning_momentum=0.9,
        batch_size=40,
        valid_size= 0.1,
        n_iter=200,
        verbose=True)
    clf = make_pipeline(OneHotEncoder(categorical_features = [0],  sparse = False), MinMaxScaler(feature_range=(-0.5,0.5)), nn)
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
        # find all the hero movement and sort in time
        hero_df = df[(df.hero_id == hero_id)].sort("timestamp")
        positions = hero_df[["timestamp","position_x","position_y"]].values
        width = 10
        # get a slide window of width 10 for the hero movements
        slided_window = window_stack(positions[:,1:],width = width)
        # we also need to find the last timestamp
        timestamps = window_stack(positions[:,0:1],width = width)
        # get only the relevant timestamps
        opp_pos_time =  timestamps[:,-1]

        # find all the here positions for the relevant timestamps
        opps_df = df[(df.timestamp.isin( opp_pos_time))]
        # remove the current hero from the lisd and sort
        opps_df = opps_df[(opps_df.hero_id != hero_id)].sort(["timestamp", "hero_id"])


        # get the positions of all other players
        opps_positions = opps_df[["position_x","position_y"]].values

        other_coords_shape = 9 * 2

        # reshape the numpy array
        slided_positions = opps_positions.reshape(len(opp_pos_time),other_coords_shape)

        # prepare the numpy array with the X data
        hero_X = np.ones((slided_window.shape[0],slided_window.shape[1]+other_coords_shape + 1))

        # 18 elements are the other hero positions (x,y)
        hero_X[:,1:19] = slided_positions
        # rest are our "width" last steps
        hero_X[:,19:] = slided_window


        # first element is the id our hero
        hero_X[:,0] = hero_df["hero_id"].values[:len(slided_window)]

        # create what is to be predicted, i.e. the difference between current position other positions
        hero_y = hero_X[:,-2:] - hero_X[:,-4:-2]

        # delete the last two columns (i.e. our last position) from Xas this is what we are trying to predict
        hero_X = np.delete(hero_X,[hero_X.shape[1]-1,hero_X.shape[1]-2 ], 1)


        # Convert all past coordinates to differences, with the exception of the last one
        for x in hero_X:
            for p in range(19, len(x)-2):
                x[p] = x[p] - x[p+2]

        # descritise the output
        hero_y_desc = np.zeros(hero_y.shape)
        # threshold is what we consider as "no movement"
        threshold = 0.001
        hero_y_desc[np.where(hero_y>threshold)] = 1
        hero_y_desc[np.where(hero_y<-threshold)] = -1
        hero_y = hero_y_desc




        Xs.append(hero_X)
        ys.append(hero_y)

    X = np.concatenate(Xs).astype(np.float32,copy = False)
    y = np.concatenate(ys).astype(np.float32,copy = False)

    #p = 0.2
    #sample = np.random.choice([True, False], size=(len(X),), p=[p, 1-p])
    #X = X[sample]
    #y = y[sample]

    print "Data converted with shape", X.shape, y.shape
    return X, y




def main():
    # get the processed data
    X,y = preprocess_data()

    # get the dummy clf: Very important, it creates a baseline!
    dummy_clf = get_dummy_clf()
    dummy_clf.fit(X, y)
    y_hat = dummy_clf.predict(y)

    # Get the baseline predictions for x and y
    print "Dummy MSE x", mse(y[:,0], y_hat[:,0])
    print "Dummy MSE y", mse(y[:,1], y_hat[:,1])

    # create 5 different crossvalidation folds
    ss = ShuffleSplit(len(y), n_iter=5, random_state=0)

    scores_x = []
    scores_y = []
    for i, (train_index, test_index) in enumerate(ss):
        # Choose a classifier
        #clf = get_linear_clf()
        clf = get_nn_clf()
        clf.fit(X[train_index], y[train_index])
        y_hat = clf.predict(X[test_index])

        # Save the score for each fold
        score_x = mse(y[test_index,0], y_hat[:,0])
        score_y = mse(y[test_index,1], y_hat[:,1])


        # You can print the coefficients/intercept for the linear classifier
        #print clf.steps[-1][1].coef_,clf.steps[-1][1].intercept_

        scores_x.append(score_x)
        scores_y.append(score_y)
        print scores_x,scores_y


    print "MSE CV x", np.array(scores_x).mean()
    print "MSE CV y", np.array(scores_y).mean()




if __name__=="__main__":
    main()
