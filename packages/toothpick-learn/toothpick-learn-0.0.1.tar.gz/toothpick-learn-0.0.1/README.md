# toothpick

Toothpick is a mini "library" which contains some implementation of machine learning algorithms in Python3.6. These algorithm 
are built on NumPy. **This "library" is just a toy**, the reason why I create it is to share my ideas and codes. 
All algorithms have `fit` and `predict` interface like `scikit-learn`. When I implemented these algorithms, I referenced
some books as follows: _Machine Learning_ writen by ZhiHua Zhou, _Statistical Learning Method_ writen by Hang Li and 
_Machine Learning in Action_ writen by Peter Harrington.

By the way, I am a novice in python and machine learning field, so you can put forward issues if you find some bugs or questions.

## Why named toothpick?

A toothpick is a small stick of wood, plastic, bamboo, or other substance used to remove detritus from the teeth, usually
after a meal(from wikipedia). This library is similarly small and you can "take" it after meal :P.

## How to guarantee the correctness?

I compared my implementation with scikit-learn's when I was implementing these algorithms, which you can find in every single python file
and these performance were approximate on some very simple data set.

## Algorithms implemented

 - Logistic Regression
 - Naive Bayes
 - K Nearest Neighbours
 - KMeans
 - Learning Vector Quantization
 - Ensemble Learning Algorithms
    - AdaBoost(only support binary classification)
    - Bagging
    - Stacking

## Todo List

 - Decision Tree
 - SVM
 - Regression
    - Linear Regressiong
    - Ridge Regression
    - Lasso Regression
 - Neural Network