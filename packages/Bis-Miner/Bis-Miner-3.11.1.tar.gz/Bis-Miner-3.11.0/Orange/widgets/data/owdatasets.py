import enum
import json
import logging
import numbers
import os
import shutil
import sys
import tempfile
import traceback

from xml.sax.saxutils import escape
from concurrent.futures import ThreadPoolExecutor, Future

from types import SimpleNamespace as namespace
from typing import Optional, Dict, Tuple

import requests
from AnyQt.QtWidgets import (
    QLabel, QLineEdit, QTextBrowser, QSplitter, QTreeView,
    QStyleOptionViewItem, QStyledItemDelegate, QApplication
)
from AnyQt.QtGui import QStandardItemModel, QStandardItem
from AnyQt.QtCore import (
    Qt, QSize, QObject, QThread, QModelIndex, QSortFilterProxyModel,
    QItemSelectionModel,
    pyqtSlot as Slot, pyqtSignal as Signal
)

import Orange.data
from Orange.misc.environ import data_dir
from Orange.widgets import widget, settings, gui
from Orange.widgets.utils.signals import Output
from Orange.widgets.widget import Msg

log = logging.getLogger(__name__)


def ensure_local(di, url, local_cache_path,
                 force=False, progress_advance=None):
    pathname = os.path.join(os.path.expanduser(local_cache_path), di.id + '_' + di.filename)
    if force:
        download(di, pathname, url, callback=progress_advance)

    if not os.path.exists(pathname):
        download(di, pathname, url, callback=progress_advance)
    return pathname
    # return localfiles.localpath_download(*file_path, callback=progress_advance)


def format_info(n_all, n_cached):
    plural = lambda x: '' if x == 1 else 's'
    return "{} 个数据集{}\n{} 个数据集已缓存".format(
        n_all, plural(n_all), n_cached if n_cached else '0')


def format_exception(error):
    # type: (BaseException) -> str
    return "\n".join(traceback.format_exception_only(type(error), error))


# Model header
class Header(enum.IntEnum):
    Local = 0
    Access = 1
    Name = 2
    Size = 3
    Instances = 4
    Variables = 5
    Target = 6
    Tags = 7


HEADER = ["", "限制", "标题", "大小", "实例", "变量", "目标", "标签"]

TOKEN = ""


class SizeDelegate(QStyledItemDelegate):
    def initStyleOption(self, option, index):
        # type: (QStyleOptionViewItem, QModelIndex) -> None
        super().initStyleOption(option, index)
        value = index.data(Qt.DisplayRole)
        if isinstance(value, numbers.Integral):
            option.text = sizeformat(int(value))
            option.displayAlignment = Qt.AlignRight | Qt.AlignVCenter


class NumericalDelegate(QStyledItemDelegate):
    def initStyleOption(self, option, index):
        # type: (QStyleOptionViewItem, QModelIndex) -> None
        super().initStyleOption(option, index)
        data = index.data(Qt.DisplayRole)
        align = index.data(Qt.TextAlignmentRole)
        if align is None and isinstance(data, numbers.Number):
            # Right align if the model does not specify otherwise
            option.displayAlignment = Qt.AlignRight | Qt.AlignVCenter


class OWDataSets(widget.OWWidget):
    name = "数据集"
    description = "从商智通数据空间载入数据集"
    icon = "icons/DataSets.svg"
    priority = 20
    replaces = ["orangecontrib.prototypes.widgets.owdatasets.OWDataSets"]

    # The following constants can be overridden in a subclass
    # to reuse this widget for a different repository
    # Take care when refactoring! (used in e.g. single-cell)
    INDEX_URL = "https://opendata.webvoc.com/api/datasets/orange"
    DATASET_DIR = "datasets"

    class Error(widget.OWWidget.Error):
        no_remote_datasets = Msg("Could not fetch dataset list")

    class Warning(widget.OWWidget.Warning):
        only_local_datasets = Msg("Could not fetch datasets list, only local "
                                  "cached datasets are shown")

    class Outputs:
        data = Output("数据", Orange.data.Table)

    #: Selected dataset id
    selected_id = settings.Setting(None)  # type: Optional[str]

    auto_commit = settings.Setting(False)  # type: bool

    #: main area splitter state
    splitter_state = settings.Setting(b'')  # type: bytes
    header_state = settings.Setting(b'')  # type: bytes

    def __init__(self):
        super().__init__()
        self.local_cache_path = os.path.join(data_dir(), self.DATASET_DIR)

        if not os.path.exists(self.local_cache_path):
            os.makedirs(self.local_cache_path)

        self.__awaiting_state = None  # type: Optional[_FetchState]

        box = gui.widgetBox(self.controlArea, "信息")

        self.infolabel = QLabel(text="初始化...\n\n")
        box.layout().addWidget(self.infolabel)

        token = self.read_token()

        self.splitter_top = QSplitter(orientation=Qt.Vertical)

        box = gui.widgetBox(self.splitter_top, "令牌", addToLayout=False)
        self.tokenLineEdit = QLineEdit(
            textChanged=self.token
        )
        self.tokenlabel = QTextBrowser(
            openExternalLinks=True,
            textInteractionFlags=(Qt.TextSelectableByMouse |
                                  Qt.LinksAccessibleByMouse)
        )

        self.tokenlabel.setFrameStyle(QTextBrowser.NoFrame)
        # no (white) text background
        self.tokenlabel.viewport().setAutoFillBackground(False)
        self.tokenLineEdit.setText(token)
        box.layout().addWidget(self.tokenLineEdit)
        box.layout().addWidget(self.tokenlabel)

        self.splitter_top.addWidget(box)

        # self.splitter_top.setSizes([300, 200])
        self.splitter_top.splitterMoved.connect(
            lambda:
            setattr(self, "splitter_state", bytes(self.splitter_top.saveState()))
        )
        self.mainArea.layout().addWidget(self.splitter_top)

        content = token_html()
        self.tokenlabel.setText(content)

        gui.widgetLabel(self.mainArea, "搜索")
        self.filterLineEdit = QLineEdit(
            textChanged=self.filter
        )

        self.mainArea.layout().addWidget(self.filterLineEdit)

        self.splitter = QSplitter(orientation=Qt.Vertical)

        self.view = QTreeView(
            sortingEnabled=True,
            selectionMode=QTreeView.SingleSelection,
            alternatingRowColors=True,
            rootIsDecorated=False,
            editTriggers=QTreeView.NoEditTriggers,
        )

        box = gui.widgetBox(self.splitter, "描述", addToLayout=False)
        self.descriptionlabel = QLabel(
            wordWrap=True,
            textFormat=Qt.RichText,
        )
        self.descriptionlabel = QTextBrowser(
            openExternalLinks=True,
            textInteractionFlags=(Qt.TextSelectableByMouse |
                                  Qt.LinksAccessibleByMouse)
        )
        self.descriptionlabel.setFrameStyle(QTextBrowser.NoFrame)
        # no (white) text background
        self.descriptionlabel.viewport().setAutoFillBackground(False)

        box.layout().addWidget(self.descriptionlabel)
        self.splitter.addWidget(self.view)
        self.splitter.addWidget(box)

        self.splitter.setSizes([300, 200])
        self.splitter.splitterMoved.connect(
            lambda:
            setattr(self, "splitter_state", bytes(self.splitter.saveState()))
        )
        self.mainArea.layout().addWidget(self.splitter)
        self.controlArea.layout().addStretch(10)
        gui.auto_commit(self.controlArea, self, "auto_commit", "发送数据")

        model = QStandardItemModel(self)
        model.setHorizontalHeaderLabels(HEADER)
        proxy = QSortFilterProxyModel()
        proxy.setSourceModel(model)
        proxy.setFilterKeyColumn(-1)
        proxy.setFilterCaseSensitivity(False)
        self.view.setModel(proxy)

        if self.splitter_state:
            self.splitter.restoreState(self.splitter_state)

        self.view.setItemDelegateForColumn(
            Header.Size, SizeDelegate(self))
        self.view.setItemDelegateForColumn(
            Header.Local, gui.IndicatorItemDelegate(self, role=Qt.DisplayRole))
        self.view.setItemDelegateForColumn(
            Header.Instances, NumericalDelegate(self))
        self.view.setItemDelegateForColumn(
            Header.Variables, NumericalDelegate(self))

        self.view.resizeColumnToContents(Header.Local)

        if self.header_state:
            self.view.header().restoreState(self.header_state)

        self.setBlocking(True)
        self.setStatusMessage("初始化")

        self._executor = ThreadPoolExecutor(max_workers=1)
        f = self._executor.submit(self.list_remote)
        w = FutureWatcher(f, parent=self)
        w.done.connect(self.__set_index)

    @Slot(object)
    def __set_index(self, f):
        # type: (Future) -> None
        # set results from `list_remote` query.
        print(self.local_cache_path)
        assert QThread.currentThread() is self.thread()
        assert f.done()
        self.setBlocking(False)
        self.setStatusMessage("")
        allinfolocal = self.list_local()
        try:
            res = f.result()
        except Exception:
            log.exception("Error while fetching updated index")
            if not allinfolocal:
                self.Error.no_remote_datasets()
            else:
                self.Warning.only_local_datasets()
            res = {}

        allinforemote = res
        allkeys = set(allinfolocal)
        if allinforemote is not None:
            allkeys = allkeys | set(allinforemote)
        allkeys = sorted(allkeys)

        def info(file_path):
            if file_path in allinforemote:
                info = allinforemote[file_path]
            else:
                info = allinfolocal[file_path]
            islocal = file_path in allinfolocal
            isremote = file_path in allinforemote
            outdated = islocal and isremote and (
                allinforemote[file_path].get('version', '') !=
                allinfolocal[file_path].get('version', ''))
            islocal &= not outdated
            prefix = os.path.join('')
            filename = info['filename']
            fileaccess = info['fileaccess']
            id = info['id']
            ispublic = True if (fileaccess == '公开') else False

            return namespace(
                json=info, id=id,
                file_path=file_path,
                fileaccess=fileaccess, ispublic=ispublic,
                prefix=prefix, filename=filename,
                url=info.get("url", None),
                title=info.get("title", filename),
                datetime=info.get("datetime", None),
                description=info.get("description", None),
                references=info.get("references", []),
                seealso=info.get("seealso", []),
                source=info.get("source", None),
                year=info.get("year", None),
                instances=info.get("instances", None),
                variables=info.get("variables", None),
                target=info.get("target", None),
                tags=info.get("tags", []),
                size=info.get("size", None),
                islocal=islocal,
                outdated=outdated
            )

        model = QStandardItemModel(self)
        model.setHorizontalHeaderLabels(HEADER)

        current_index = -1
        for i, file_path in enumerate(allkeys):
            datainfo = info(file_path)
            item0 = QStandardItem(datainfo.fileaccess)
            item1 = QStandardItem()
            item1.setData(" " if datainfo.islocal else "", Qt.DisplayRole)
            item1.setData(datainfo, Qt.UserRole)
            item2 = QStandardItem(datainfo.title)
            item3 = QStandardItem()
            item3.setData(datainfo.size, Qt.DisplayRole)
            item4 = QStandardItem()
            item4.setData(datainfo.instances, Qt.DisplayRole)
            item5 = QStandardItem()
            item5.setData(datainfo.variables, Qt.DisplayRole)
            item6 = QStandardItem()
            item6.setData(datainfo.target, Qt.DisplayRole)
            if datainfo.target:
                item6.setIcon(variable_icon(datainfo.target))
            item7 = QStandardItem()
            item7.setData(", ".join(datainfo.tags) if datainfo.tags else "",
                          Qt.DisplayRole)
            row = [item1, item0, item2, item3, item4, item5, item6, item7]
            model.appendRow(row)

            if os.path.join(*file_path) == self.selected_id:
                current_index = i

        hs = self.view.header().saveState()
        model_ = self.view.model().sourceModel()
        self.view.model().setSourceModel(model)
        self.view.header().restoreState(hs)
        model_.deleteLater()
        model_.setParent(None)
        self.view.selectionModel().selectionChanged.connect(
            self.__on_selection
        )
        # Update the info text
        self.infolabel.setText(format_info(model.rowCount(), len(allinfolocal)))

        if current_index != -1:
            selmodel = self.view.selectionModel()
            selmodel.select(
                self.view.model().mapFromSource(model.index(current_index, 0)),
                QItemSelectionModel.ClearAndSelect | QItemSelectionModel.Rows)

    def __update_cached_state(self):
        model = self.view.model().sourceModel()
        localinfo = self.list_local()
        keys = set(localinfo)
        assert isinstance(model, QStandardItemModel)

        allinfo = []
        for i in range(model.rowCount()):
            item = model.item(i, 0)
            info = item.data(Qt.UserRole)
            info.islocal = info.id in keys
            item.setData(" " if info.islocal else "", Qt.DisplayRole)
            allinfo.append(info)

        self.infolabel.setText(format_info(
            model.rowCount(), sum(info.islocal for info in allinfo)))

    def selected_dataset(self):
        """
        Return the current selected dataset info or None if not selected

        Returns
        -------
        info : Optional[namespace]
        """
        rows = self.view.selectionModel().selectedRows(0)
        assert 0 <= len(rows) <= 1
        current = rows[0] if rows else None  # type: Optional[QModelIndex]
        if current is not None:
            info = current.data(Qt.UserRole)
            assert isinstance(info, namespace)
        else:
            info = None
        return info

    def filter(self):
        filter_string = self.filterLineEdit.text().strip()
        proxyModel = self.view.model()
        if proxyModel:
            proxyModel.setFilterFixedString(filter_string)

    def token(self):
        global TOKEN
        TOKEN = self.tokenLineEdit.text().strip()
        self.save_token(TOKEN)

    def __on_selection(self):
        # Main datasets view selection has changed
        rows = self.view.selectionModel().selectedRows(0)
        assert 0 <= len(rows) <= 1
        current = rows[0] if rows else None  # type: Optional[QModelIndex]
        if current is not None:
            current = self.view.model().mapToSource(current)
            di = current.data(Qt.UserRole)
            text = description_html(di)
            self.descriptionlabel.setText(text)
            self.selected_id = os.path.join(di.prefix, di.filename)
        else:
            self.descriptionlabel.setText("")
            self.tokenlabel.setText("")
            self.selected_id = None

        self.commit()

    def commit(self):
        """
        Commit a dataset to the output immediately (if available locally) or
        schedule download background and an eventual send.

        During the download the widget is in blocking state
        (OWWidget.isBlocking)
        """
        di = self.selected_dataset()
        if di is not None:
            self.Error.clear()

            if self.__awaiting_state is not None:
                # disconnect from the __commit_complete
                self.__awaiting_state.watcher.done.disconnect(
                    self.__commit_complete)
                # .. and connect to update_cached_state
                # self.__awaiting_state.watcher.done.connect(
                #     self.__update_cached_state)
                # TODO: There are possible pending __progress_advance queued
                self.__awaiting_state.pb.advance.disconnect(
                    self.__progress_advance)
                self.progressBarFinished(processEvents=None)
                self.__awaiting_state = None

            if not di.islocal:
                pr = progress()
                callback = lambda pr=pr: pr.advance.emit()
                pr.advance.connect(self.__progress_advance, Qt.QueuedConnection)

                self.progressBarInit(processEvents=None)
                self.setStatusMessage("下载中...")
                self.setBlocking(True)

                f = self._executor.submit(
                    ensure_local, di, di.url,
                    self.local_cache_path, force=di.outdated,
                    progress_advance=callback)
                w = FutureWatcher(f, parent=self)
                w.done.connect(self.__commit_complete)
                self.__awaiting_state = _FetchState(f, w, pr)
            else:
                self.setStatusMessage("")
                self.setBlocking(False)
                self.commit_cached(di.id + '_' + di.filename)
        else:
            self.Outputs.data.send(None)

    @Slot(object)
    def __commit_complete(self, f):
        # complete the commit operation after the required file has been
        # downloaded
        assert QThread.currentThread() is self.thread()
        assert self.__awaiting_state is not None
        assert self.__awaiting_state.future is f

        if self.isBlocking():
            self.progressBarFinished(processEvents=None)
            self.setBlocking(False)
            self.setStatusMessage("")

        self.__awaiting_state = None

        try:
            self.Warning.clear()
            self.setStatusMessage("")
            path = f.result()
        except ForbiddenException:
            self.warning("数据集未授权！")
            self.setStatusMessage("数据集未授权！")
            path = None
        except Exception as ex:
            log.exception("Error:")
            self.error(format_exception(ex))
            path = None

        self.__update_cached_state()

        if path is not None:
            data = self.load_data(path)
        else:
            data = None
        self.Outputs.data.send(data)

    def commit_cached(self, file_path):
        path = os.path.join(os.path.expanduser(self.local_cache_path), file_path)
        self.Outputs.data.send(self.load_data(path))

    @Slot()
    def __progress_advance(self):
        assert QThread.currentThread() is self.thread()
        self.progressBarAdvance(1, processEvents=None)

    def onDeleteWidget(self):
        super().onDeleteWidget()
        if self.__awaiting_state is not None:
            self.__awaiting_state.watcher.done.disconnect(self.__commit_complete)
            self.__awaiting_state.pb.advance.disconnect(self.__progress_advance)
            self.__awaiting_state = None

    def sizeHint(self):
        return QSize(900, 600)

    def closeEvent(self, event):
        self.splitter_state = bytes(self.splitter.saveState())
        self.header_state = bytes(self.view.header().saveState())
        super().closeEvent(event)

    @staticmethod
    def load_data(path):
        return Orange.data.Table(path)

    def list_remote(self):
        files = {}
        r = requests.get(self.INDEX_URL)
        if r.status_code == 200:
            for file in r.json():
                files[file['id']] = file
        return files
        # return client.allinfo()

    def list_local(self):
        localfiles = {}
        for root, dirs, files in os.walk(self.local_cache_path):
            if root == self.local_cache_path:
                for f in files:
                    if f[-5:] == '.info' and os.path.exists(os.path.join(root, f[:-5])):
                        info = _open_file_info(os.path.join(root, f))
                        localfiles[info['id']] = info
                        # if t.status_code == 200:
                        #     return json.loads(t.text)
                        # else:
                        #     return {}

        return localfiles

    def read_token(self):
        path = os.path.join(self.local_cache_path, 'token')
        if os.path.exists(path):
            with open(path, 'rt') as f:
                token = json.load(f, encoding='utf-8')
                return token["token"]
        else:
            return ""

    def save_token(self, token):
        path = os.path.join(self.local_cache_path, 'token')
        with open(path, 'wt') as f:
            json.dump({"token": token}, f, ensure_ascii=False)


class FutureWatcher(QObject):
    done = Signal(object)
    _p_done_notify = Signal(object)

    def __init__(self, future, parent=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.__future = future
        self._p_done_notify.connect(self.__on_done, Qt.QueuedConnection)
        future.add_done_callback(self._p_done_notify.emit)

    @Slot(object)
    def __on_done(self, f):
        assert f is self.__future
        self.done.emit(self.__future)


class progress(QObject):
    advance = Signal()


class _FetchState(object):
    def __init__(self, future, watcher, pb):
        self.future = future
        self.watcher = watcher
        self.pb = pb


def variable_icon(name):
    if name == "categorical":
        return gui.attributeIconDict[Orange.data.DiscreteVariable()]
    elif name == "numeric":  # ??
        return gui.attributeIconDict[Orange.data.ContinuousVariable()]
    else:
        return gui.attributeIconDict[-1]


def make_html_list(items):
    if items is None:
        return ''
    style = '"margin: 5px; text-indent: -40px; margin-left: 40px;"'

    def format_item(i):
        return '<p style={}><small>{}</small></p>'.format(style, i)

    return '\n'.join([format_item(i) for i in items])


def description_html(datainfo):
    # type: (namespace) -> str
    """
    Summarize a data info as a html fragment.
    """
    html = []
    year = " ({})".format(str(datainfo.year)) if datainfo.year else ""
    source = ", 来自 {}".format(datainfo.source) if datainfo.source else ""
    html.append("<b>{}</b>{}{}".format(escape(datainfo.title), year, source))
    if datainfo.ispublic is not True:
        html.append('<span style="color: #ff0000;">（此数据集需要购买！）</span>\n')
    html.append("<p>{}</p>".format(datainfo.description))
    seealso = make_html_list(datainfo.seealso)
    if seealso:
        html.append("<small><b>请参阅：</b>\n" + seealso + "</small>")
    refs = make_html_list(datainfo.references)
    if refs:
        html.append("<small><b>引用：</b>\n" + refs + "</small>")
    return "\n".join(html)


def token_html():
    content = '<strong>如何获取<span style="color: #ff0000;">令牌</span>？</strong><p>1.<a ' \
              'href="https://opendata.webvoc.com/loginpage.xhtml?redirectPage=/dataverseuser.xhtml?selectTab' \
              '=apiTokenTab">登录商智通数据空间</a></p><p>2.第一次获取<span style="color: #ff0000;">令牌</span>？请先<a ' \
              'href="https://opendata.webvoc.com/dataverseuser.xhtml?selectTab=apiTokenTab">创建令牌</a></p><p><a ' \
              'href="https://opendata.webvoc.com/dataverseuser.xhtml?selectTab=apiTokenTab">查看令牌</a></p> '
    return content


def _open_file_info(fname):
    with open(fname, 'rt') as f:
        return json.load(f, encoding='utf-8')


def _save_file_info(fname, info):
    with open(fname, 'wt') as f:
        json.dump(info, f, ensure_ascii=False)


def sizeformat(size):
    for unit in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            if unit == "bytes":
                return "%1.0f %s" % (size, unit)
            else:
                return "%3.1f %s" % (size, unit)
        size /= 1024.0
    return "%.1f PB" % size


def download(di, path, url, **kwargs):
    callback = kwargs.get("callback", None)
    r = requests.get(url + "?key=" + TOKEN, stream=True)
    if r.status_code == 404:
        raise FileNotFoundError
    elif r.status_code == 403:
        raise ForbiddenException("数据集未授权！")
    elif r.status_code != 200:
        raise IOError

    size = r.headers.get('content-length')
    if size:
        size = int(size)

    f = tempfile.TemporaryFile()

    chunksize = 1024 * 8
    lastchunkreport = 0.0001

    readb = 0

    for buf in r.iter_content(chunksize):
        readb += len(buf)
        while size and float(readb) / size > lastchunkreport + 0.01:
            lastchunkreport += 0.01
            if callback:
                callback()
        f.write(buf)

    f.seek(0)

    with open(path, "wb") as fo:
        shutil.copyfileobj(f, fo)

    if callback and not size:
        for i in range(99):
            callback()

    if callback:
        callback()

    _save_file_info(path + '.info', di.json)


class ForbiddenException(Exception):
    pass


def main(args=None):
    if args is None:
        args = sys.argv

    app = QApplication(list(args))
    w = OWDataSets()
    w.show()
    w.raise_()
    rv = app.exec_()
    w.saveSettings()
    w.onDeleteWidget()
    return rv


if __name__ == "__main__":
    sys.exit(main())
