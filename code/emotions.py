""" The aim of this file is to contain all the function
and the main which have to do with emotion recognition, especially
with the Kanade database."""

import glob
import argparse
import DimensionalityReduction
import cPickle as pickle
from sklearn import cross_validation

import deepbelief as db
from common import *

parser = argparse.ArgumentParser(description='digit recognition')
parser.add_argument('--save',dest='save',action='store_true', default=False,
                    help="if true, the network is serialized and saved")
parser.add_argument('--train',dest='train',action='store_true', default=False,
                    help=("if true, the network is trained from scratch from the"
                          "traning data"))
parser.add_argument('--rbm', dest='rbm',action='store_true', default=False,
                    help=("if true, the code for traning an rbm on the data is run"))
parser.add_argument('--db', dest='db',action='store_true', default=False,
                    help=("if true, the code for traning a deepbelief net on the"
                          "data is run"))
parser.add_argument('--trainSize', type=int, default=10000,
                    help='the number of tranining cases to be considered')
parser.add_argument('--testSize', type=int, default=1000,
                    help='the number of testing cases to be considered')
parser.add_argument('netFile', help="file where the serialized network should be saved")
parser.add_argument('--nesterov', dest='nesterov',action='store_true', default=False,
                    help=("if true, the deep belief net is trained using nesterov momentum"))
parser.add_argument('--rmsprop', dest='rmsprop',action='store_true', default=False,
                    help=("if true, rmsprop is used when training the deep belief net."))


# DEBUG mode?
parser.add_argument('--debug', dest='debug',action='store_false', default=False,
                    help=("if true, the deep belief net is ran in DEBUG mode"))

# Get the arguments of the program
args = parser.parse_args()

# Set the debug mode in the deep belief net
db.DEBUG = args.debug

"""
  Arguments:
    big: should the big or small images be used?
    folds: which folds should be used (1,..5) (a list). If None is passed all
    folds are used
"""
def deepBeliefKanade(big=False, folds=None):
  if big:
    files = glob.glob('kanade_150*.pickle')
  else:
    files = glob.glob('kanade_f*.pickle')

  if not folds:
    folds = range(1, 6)

  # Read the data from them. Sort out the files that do not have
  # the folds that we want
  # TODO: do this better (with regex in the file name)
  # DO not reply on the order returned
  print len(files)
  print len(folds)

  files = [ files[x -1] for x in folds]

  data = []
  labels = []
  # TODO: do LDA on the training data

  # TODO: do proper CV in which you use 4 folds for training and one for testing
  # at that time
  for filename in files:
    with open(filename, "rb") as  f:
      # Sort out the labels from the data
      dataAndLabels = pickle.load(f)
      foldData = dataAndLabels[0:-1 ,:]
      foldLabels = dataAndLabels[-1,:]
      data.append(foldData)
      labels.append(foldLabels)


  kf = cross_validation.KFold(n=len(data), n_folds=len(folds))

  for train, test in kf:
    trainData = train[0]
    labels=train[1]
    vectorLabels = labelsToVectors(labels, 6)

    # TODO: this might require more thought
    net = db.DBN(5, [784, 1000, 1000, 1000, 10],
               unsupervisedLearningRate=0.01,
               supervisedLearningRate=0.05,
               nesterovMomentum=args.nesterov,
               rmsprop=args.rmsprop,
               hiddenDropout=0.5, rbmHiddenDropout=0.5, visibleDropout=0.8,
               rbmVisibleDropout=1)
    net.train(trainData, vectorLabels)

    probs, predicted = net.classify(test[0])

    actualLabels = test[1]
    correct = 0
    errorCases = []
    for i in xrange(len(test[0])):
      print "predicted"
      print "probs"
      print probs[i]
      print predicted[i]
      print "actual"
      actual = actualLabels[i]
      print actual
      if predicted[i] == actual:
        correct += 1
      else:
        errorCases.append(i)

    print "correct"
    print correct


def main():
  deepBeliefKanade()

# You can also group the emotions into positive and negative to see
# if you can get better results (probably yes)
if __name__ == '__main__':
  main()