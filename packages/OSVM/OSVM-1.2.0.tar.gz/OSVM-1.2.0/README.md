OSVM
==========

OSVM plots for python. Inspired by (https://pythonprogramming.net/soft-margin-kernel-cvxopt-svm-machine-learning-tutorial/)

## Install ##
The easiest way to install OSVM is using pip:

```
sudo pip install OSVM
```

To install the latest version on github, simply do:
```
git clone https://github.com/ChristelJunco/OSVM.git
cd OSVM
sudo python setup.py install
```

To test that it worked, open up python and check that ```import osvm``` doesn't give you any errors.

## Requirements ##

This package requires:

* matplotlib
* numpy
* pandas
* CVXOPT

## Basic usage ##

There is two class, ```IS_BFFA```,```OPT_SVM```:


```
from osvm import *
help(osvm)

Help on class osvm in module osvm.IS_BFFA:

IS_BFFA(dataset)
         
     Inputs:
        *Raw Dataset
    
     Returns:
         * best_training_subset: instances that are selected for training in SVM

OPT_SVM(kernel,C)
    Inputs:
        *kernel: Chosen Kernel
        *C: C parameter 

    fit(X,Y)
        Inputs:
            *Dataset from Instance Selection
                X: Row Dataset from features
                Y: Labels/Targets
    predict(X)
        Inputs:
            *Dataset for Test
                X:Row Dataset from features


View more examples [here](https://pythonprogramming.net/soft-margin-kernel-cvxopt-svm-machine-learning-tutorial/).
