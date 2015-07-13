import numpy as np
import config
from sklearn.dummy import DummyClassifier
from sklearn.preprocessing import OneHotEncoder, MinMaxScaler
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LinearRegression, MultiTaskLasso, LogisticRegression, MultiTaskLassoCV, MultiTaskElasticNet
from sklearn.metrics import classification_report as cf
from sklearn.metrics import r2_score as r2, mean_squared_error as mse
import pandas as pd
from sklearn.cross_validation import ShuffleSplit
from sknn.mlp import Classifier, Layer, Regressor
from sklearn.ensemble import ExtraTreesRegressor


np.set_printoptions(precision=4)
np.set_printoptions(suppress=True)

# stolen from http://stackoverflow.com/questions/15722324/sliding-window-in-numpy
def window_stack(a, stepsize=1, width=3):
    return np.hstack( a[i:1+i-width or None:stepsize] for i in range(0,width) )

def get_clf():
    lr = MultiTaskLasso(normalize=False)


    clf = make_pipeline(  MinMaxScaler(), lr)
    return clf

def get_dummy_clf():
    dummy = DummyClassifier()
    return dummy


def get_tree():
    clf = ExtraTreesRegressor(max_depth=5, n_jobs=2 , n_estimators=10, verbose = 1000)
    return clf



def get_nn_clf(valid_set):
    nn  = Regressor(
        layers=[
            # Convolution("Rectifier", channels=10, pool_shape=(2,2), kernel_shape=(3, 3)),
            Layer('Rectifier', units=50),
            Layer('Rectifier', units=50),

            Layer('Sigmoid')],
        learning_rate=0.001,
        learning_rule='sgd',
        #learning_momentum=0.9,
        batch_size=200,
        #valid_size= 0.1,
        valid_set = valid_set,
        n_iter=30,
        verbose=True)
    clf = make_pipeline( MinMaxScaler(), nn)
    return clf


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
        slided_window = window_stack(positions,width = 10)

        #print positions.values[0:10]
        #print slided_window[0:10]

        hero_X = np.zeros((slided_window.shape[0],slided_window.shape[1]+1))
        hero_X[:,1:] = slided_window
        # diffs
        #hero_X = np.diff(hero_X, n=1, axis=-1)

        hero_X[:,0] = hero_df["hero_id"].values[:len(slided_window)]
        hero_y = hero_X[:,-2:]


        #hero_X = np.delete(hero_X,[hero_X.shape[1]-1,hero_X.shape[1]-2 ], 1)

        #hero_y_new = np.zeros(hero_y.shape)

        # threshold = 0.001
        # hero_y_new[np.where(hero_y>threshold)] = 1
        # hero_y_new[np.where(hero_y<-threshold)] = -1
        # #
        # hero_y = hero_y_new

        #print hero_y

        #print set(hero_y.flatten())
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
    #y_hat = dummy_clf.predict(y)
    #print y_hat
    #print "Dummy MSE", mse(y, y_hat)

    ss = ShuffleSplit(len(y), n_iter=10, random_state=0)

    scores = []
    for i, (train_index, test_index) in enumerate(ss):
        #print "Shuffle", i
        clf = get_clf()
        print X[test_index].shape,y[test_index].shape
        print X[train_index].shape,y[train_index].shape
        #clf = get_nn_clf(valid_set=(X[test_index],y[test_index] ))
        #clf = get_tree()
        clf.fit(X[train_index], y[train_index])
        print clf.steps[-1][1].coef_,clf.steps[-1][1].intercept_

        y_hat = clf.predict(X[test_index])
        print y_hat
        #exit()
        print X[test_index][0], y[test_index][0], y_hat[0]
        score_x = mse(y[test_index], y_hat)



        scores.append(score_x)

        print scores

    print "MSE CV x", np.array(scores).mean()





if __name__=="__main__":
    main()
