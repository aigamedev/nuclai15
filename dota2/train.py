import numpy as np
import config
from sklearn.dummy import DummyRegressor
from sklearn.preprocessing import OneHotEncoder, MinMaxScaler
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error as mse
from sklearn.metrics import r2_score as r2
import pandas as pd
from sklearn.cross_validation import ShuffleSplit



np.set_printoptions(precision=4)
np.set_printoptions(suppress=True)

# stolen from http://stackoverflow.com/questions/15722324/sliding-window-in-numpy
def window_stack(a, stepsize=1, width=3):
    return np.hstack( a[i:1+i-width or None:stepsize] for i in range(0,width) )

def get_clf():
    lr = LinearRegression(n_jobs=2);
    clf = make_pipeline(OneHotEncoder(categorical_features = [0],  sparse = False), MinMaxScaler(), lr)
    return clf

def get_dummy_clf():
    dummy = DummyRegressor()
    return dummy


def get_data():
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
        positions = hero_df[["position_x","position_y"]]
        slided_window = window_stack(positions,width = 11)
        hero_X = np.zeros((slided_window.shape[0],slided_window.shape[1]+1))
        hero_X[:,1:] = slided_window
        # diffs
        #hero_X = np.diff(hero_X, n=1, axis=-1)

        hero_X[:,0] = hero_df["hero_id"].values[:len(slided_window)]
        hero_y = hero_X[:,-2:] - hero_X[:,-4:-2]


        hero_X = np.delete(hero_X,[hero_X.shape[1]-1,hero_X.shape[1]-2 ], 1)

        Xs.append(hero_X)
        ys.append(hero_y)

    X = np.concatenate(Xs)
    y = np.concatenate(ys)
    print X.shape, y.shape
    return X, y

def main():
    X,y = get_data()
    dummy_clf = get_dummy_clf()
    dummy_clf.fit(X, y)
    y_hat = dummy_clf.predict(y)

    print "Dummy R^2 x", r2(y[:,0], y_hat[:,0])
    print "Dummy R^2 y", r2(y[:,1], y_hat[:,1])


    ss = ShuffleSplit(len(y), n_iter=10, random_state=0)

    scores_x = []
    scores_y = []
    for i, (train_index, test_index) in enumerate(ss):
        print "Shuffle", i
        clf = get_clf()
        clf.fit(X[train_index], y[train_index])
        y_hat = clf.predict(X[test_index])

        score_x = r2(y[test_index,0], y_hat[:,0])
        score_y = r2(y[test_index,1], y_hat[:,1])


        scores_x.append(score_x)
        scores_y.append(score_y)
        #print scores_x,scores_y

    print "LinearRegression R^2 CV x", np.array(scores_x).mean()
    print "LinearRegression R^2 CV y", np.array(scores_y).mean()




if __name__=="__main__":
    main()