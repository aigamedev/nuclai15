import bz2
import glob
import pickle

import numpy
from sknn.backend import pylearn2
from sknn import mlp


train_none = glob.glob('data/*/placed?/*.png') + glob.glob('data/*/none/*.png')
train_red = glob.glob('data/*/red/*.png')
train_yellow = glob.glob('data/*/yellow/*.png')

print("Found total of %i files:" % len(train_none)+len(train_red)+len(train_yellow))
print("  - %i no trains," % len(train_none))
print("  - %i red trains," % len(train_red))
print("  - %i yellow ones.\n" % len(train_yellow))

ds = Dataset()
ds.store(train_none, 0, times=1)
ds.store(train_yellow, 1, times=4)
ds.store(train_red, 2, times=8)

X, y = ds.toarray()


nn = mlp.Classifier(
		layers=[
			mlp.Layer("Rectifier", units=64, dropout=0.3),
			mlp.Layer("Rectifier", units=48, dropout=0.1),
			mlp.Layer("Rectifier", units=32),
			mlp.Layer("Softmax")],
		learning_rate=0.01,
		learning_rule='rmsprop',
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
