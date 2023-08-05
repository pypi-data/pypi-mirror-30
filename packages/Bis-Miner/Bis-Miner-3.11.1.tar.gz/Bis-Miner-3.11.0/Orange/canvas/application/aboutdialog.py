"""
Orange canvas about dialog
"""

import sys
import pkg_resources

from AnyQt.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QLabel
from AnyQt.QtCore import Qt

from .. import config

ABOUT_TEMPLATE = """\
<center>
<h4>BIS-Miner“雅典娜”数据挖掘系统</h4>
<p>版本： {version}</p>
</center>

"""


class AboutDialog(QDialog):
    def __init__(self, parent=None, **kwargs):
        QDialog.__init__(self, parent, **kwargs)

        if sys.platform == "darwin":
            self.setAttribute(Qt.WA_MacSmallSize, True)

        self.__setupUi()

    def __setupUi(self):
        layout = QVBoxLayout()
        label = QLabel(self)

        pixmap, _ = config.splash_screen()

        label.setPixmap(pixmap)

        layout.addWidget(label, Qt.AlignCenter)

        try:
            from Orange.version import version
        except ImportError:
            dist = pkg_resources.get_distribution("Orange3")
            version = dist.version

        text = ABOUT_TEMPLATE.format(version=version)
        # TODO: Also list all known add-on versions.

        text_label = QLabel(text)
        layout.addWidget(text_label, Qt.AlignCenter)

        buttons = QDialogButtonBox(QDialogButtonBox.Close,
                                   Qt.Horizontal,
                                   self)
        layout.addWidget(buttons)
        buttons.rejected.connect(self.accept)
        layout.setSizeConstraint(QVBoxLayout.SetFixedSize)
        self.setLayout(layout)
