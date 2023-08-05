"""Naive Bayes Learner
"""

from Orange.data import Table
from Orange.classification.naive_bayes import NaiveBayesLearner
from Orange.widgets.utils.owlearnerwidget import OWBaseLearner


class OWNaiveBayes(OWBaseLearner):
    name = "朴素贝叶斯"
    description = "一个在假设特征是独立的前提下，基于贝叶斯定理的快速简单的概率分类器"
    icon = "icons/NaiveBayes.svg"
    replaces = [
        "Orange.widgets.classify.ownaivebayes.OWNaiveBayes",
    ]
    priority = 70

    LEARNER = NaiveBayesLearner


if __name__ == "__main__":
    import sys
    from AnyQt.QtWidgets import QApplication

    a = QApplication(sys.argv)
    ow = OWNaiveBayes()
    d = Table('iris')
    ow.set_data(d)
    ow.show()
    a.exec_()
    ow.saveSettings()
