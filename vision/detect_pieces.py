import bz2
import glob
import pickle

import numpy
from sknn.backend import pylearn2
from sknn import mlp

from dataset import Dataset


positive = glob.glob('data/*/placed?/*.png')
negative = glob.glob('data/*/missing?/*.png')
unknown =  glob.glob('data/*/unsure?/*.png')

print("Found total of %i files:" % len(positive+negative+unknown))
print("  - %i placed pieces," % len(positive))
print("  - %i missing pieces," % len(negative))
print("  - %i unsure images.\n" % len(unknown))


ds = Dataset()
ds.store(negative, 0, times=1)
ds.store(positive, 1, times=1)
ds.store(unknown, 2, times=2)

X, y = ds.toarray()


nn = mlp.Classifier(
		layers=[
			mlp.Layer("Rectifier", units=48, dropout=0.3),
			mlp.Layer("Rectifier", units=32, dropout=0.1),
			mlp.Layer("Rectifier", units=24),
			mlp.Layer("Softmax")],
		learning_rate=0.01,
		learning_rule='adagrad',
		n_iter=10,
		n_stable=10,
		batch_size=50,
		valid_set=(X,y),
		verbose=1)

try:
	nn.fit(X, y)
except KeyboardInterrupt:
	pass

score = nn.score(X, y)
print('SCORE:', score * 100.0)


print('MISMATCHES:')
yp = nn.predict(X)
y = y.reshape(yp.shape)
for a in numpy.where(y != yp)[0]:
	print(ds.filenames[a], 'was', int(yp[a]), 'not', int(y[a]))


with bz2.open('detector_train.pkl.bz2', 'wb') as f:
	pickle.dump(nn, f)
