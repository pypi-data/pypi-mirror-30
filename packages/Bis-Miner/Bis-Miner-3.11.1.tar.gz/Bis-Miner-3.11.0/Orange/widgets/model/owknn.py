from AnyQt.QtCore import Qt

from Orange.data import Table
from Orange.modelling import KNNLearner
from Orange.widgets import gui
from Orange.widgets.settings import Setting
from Orange.widgets.utils.owlearnerwidget import OWBaseLearner


class OWKNNLearner(OWBaseLearner):
    name = "k-最邻近（kNN）"
    description = "根据最邻近的训练个例做预测"
    icon = "icons/KNN.svg"
    replaces = [
        "Orange.widgets.classify.owknn.OWKNNLearner",
        "Orange.widgets.regression.owknnregression.OWKNNRegression",
    ]
    priority = 20

    LEARNER = KNNLearner

    weights = ["uniform", "distance"]
    metrics = ["euclidean", "manhattan", "chebyshev", "mahalanobis"]

    learner_name = Setting("kNN")
    n_neighbors = Setting(5)
    metric_index = Setting(0)
    weight_index = Setting(0)

    def add_main_layout(self):
        box = gui.vBox(self.controlArea, "Neighbors")
        self.n_neighbors_spin = gui.spin(
            box, self, "n_neighbors", 1, 100, label="Number of neighbors:",
            alignment=Qt.AlignRight, callback=self.settings_changed,
            controlWidth=80)
        self.metrics_combo = gui.comboBox(
            box, self, "metric_index", orientation=Qt.Horizontal,
            label="Metric:", items=[i.capitalize() for i in self.metrics],
            callback=self.settings_changed)
        self.weights_combo = gui.comboBox(
            box, self, "weight_index", orientation=Qt.Horizontal,
            label="Weight:", items=[i.capitalize() for i in self.weights],
            callback=self.settings_changed)

    def create_learner(self):
        return self.LEARNER(
            n_neighbors=self.n_neighbors,
            metric=self.metrics[self.metric_index],
            weights=self.weights[self.weight_index],
            preprocessors=self.preprocessors)

    def get_learner_parameters(self):
        return (("Number of neighbours", self.n_neighbors),
                ("Metric", self.metrics[self.metric_index].capitalize()),
                ("Weight", self.weights[self.weight_index].capitalize()))


if __name__ == "__main__":
    import sys
    from AnyQt.QtWidgets import QApplication

    a = QApplication(sys.argv)
    ow = OWKNNLearner()
    d = Table(sys.argv[1] if len(sys.argv) > 1 else 'iris')
    ow.set_data(d)
    ow.show()
    a.exec_()
    ow.saveSettings()
