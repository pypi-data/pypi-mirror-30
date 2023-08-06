########################################################################
# File name: __init__.py
# This file is part of: cuteborg
#
# LICENSE
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
########################################################################
import asyncio
import argparse
import logging
import signal
import sys

import quamash

import PyQt5.Qt as Qt

import cuteborg.backend
import cuteborg.config

from .ui_main import Ui_MainWindow


class RepositoriesModel(Qt.QAbstractTableModel):
    COLUMN_ID = 0
    COLUMN_NAME = 1
    COLUMN_TYPE = 2
    COLUMN_ENCRYPTION = 3
    COLUMN_PATH = 4
    COLUMN_DEVICE = 5
    COLUMN_COUNT = 6

    def __init__(self):
        super().__init__()
        self.repositories = []

    def set_repositories(self, repositories):
        self.beginResetModel()
        self.repositories[:] = repositories.values()
        self.endResetModel()

    def rowCount(self, parent):
        if parent.isValid():
            return 0
        return len(self.repositories)

    def columnCount(self, parent):
        return self.COLUMN_COUNT

    def headerData(self, section, orientation, role):
        if orientation != Qt.Qt.Horizontal:
            return
        if role == Qt.Qt.DisplayRole:
            return [
                "ID",
                "Name",
                "Type",
                "Encryption",
                "Path",
                "Device / Host",
            ][section]

    def index(self, row, column, parent):
        if parent.isValid():
            return Qt.QModelIndex()

        return self.createIndex(
            row,
            column,
            self.repositories[row],
        )

    def data(self, index, role):
        if not index.isValid():
            return

        if role != Qt.Qt.DisplayRole:
            return

        repo = index.internalPointer()
        col = index.column()

        if col == self.COLUMN_ID:
            return repo.id_
        elif col == self.COLUMN_NAME:
            return repo.name
        elif col == self.COLUMN_TYPE:
            if isinstance(repo, cuteborg.config.LocalRepositoryConfig):
                return "local"
            else:
                return "remote"
        elif col == self.COLUMN_ENCRYPTION:
            return {
                cuteborg.backend.EncryptionMode.NONE: "no encryption",
                cuteborg.backend.EncryptionMode.KEYFILE: "local keyfile",
                cuteborg.backend.EncryptionMode.REPOKEY: "repository keyfile",
            }[repo.encryption_mode]
        elif col == self.COLUMN_PATH:
            return repo.path
        elif col == self.COLUMN_DEVICE:
            if isinstance(repo, cuteborg.config.LocalRepositoryConfig):
                if repo.removable_device_uuid is not None:
                    return "/dev/disk/by-uuid/"+repo.removable_device_uuid
                else:
                    return ""
            else:
                parts = ["ssh://"]
                if repo.user:
                    parts.append(repo.user)
                    parts.append("@")
                parts.append(repo.host)
                return "".join(parts)


class JobsModel(Qt.QAbstractTableModel):
    COLUMN_NAME = 0
    COLUMN_SCHEDULE = 1
    COLUMN_COMPRESSION = 2
    COLUMN_COUNT = 3

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.jobs = []

    def set_jobs(self, jobs):
        self.beginResetModel()
        self.jobs[:] = jobs.values()
        self.endResetModel()

    def rowCount(self, parent):
        if parent.isValid():
            return 0
        return len(self.jobs)

    def columnCount(self, parent):
        return self.COLUMN_COUNT

    def headerData(self, section, orientation, role):
        if orientation != Qt.Qt.Horizontal:
            return
        if role == Qt.Qt.DisplayRole:
            return [
                "Name",
                "Schedule",
                "Compression",
            ][section]

    def index(self, row, column, parent):
        if parent.isValid():
            return Qt.QModelIndex()

        return self.createIndex(
            row,
            column,
            self.jobs[row],
        )

    def data(self, index, role):
        if not index.isValid():
            return

        if role != Qt.Qt.DisplayRole:
            return

        job = index.internalPointer()
        col = index.column()

        if col == self.COLUMN_NAME:
            return job.name
        elif col == self.COLUMN_SCHEDULE:
            schedule = job.schedule or self.config.schedule
            return "every {} {}(s)".format(
                schedule.interval_step,
                schedule.interval_unit.value,
            )
        elif col == self.COLUMN_COMPRESSION:
            if job.compression_method is None:
                return "uncompressed"
            else:
                return job.compression_method.value


class MainWindow(Qt.QMainWindow):
    def __init__(self, loop, logger):
        super().__init__()
        self.loop = loop
        self.logger = logger

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.config = cuteborg.config.Config.from_raw(
            cuteborg.config.load_config()
        )

        self.repositories_model = RepositoriesModel()
        self.repositories_model.set_repositories(
            self.config.repositories
        )
        proxy_model = Qt.QSortFilterProxyModel(self.ui.repositories_view)
        proxy_model.setSourceModel(self.repositories_model)
        proxy_model.setSortCaseSensitivity(Qt.Qt.CaseInsensitive)
        proxy_model.setSortLocaleAware(True)
        proxy_model.setSortRole(Qt.Qt.DisplayRole)
        proxy_model.sort(
            RepositoriesModel.COLUMN_NAME,
            Qt.Qt.AscendingOrder,
        )
        self.ui.repositories_view.setModel(
            proxy_model,
        )
        self.ui.repositories_view.horizontalHeader().setSectionResizeMode(
            Qt.QHeaderView.ResizeToContents
        )
        self.ui.repositories_view.horizontalHeader().setSortIndicator(
            RepositoriesModel.COLUMN_NAME,
            Qt.Qt.AscendingOrder,
        )

        self.jobs_model = JobsModel(self.config)
        self.jobs_model.set_jobs(
            self.config.jobs
        )
        proxy_model = Qt.QSortFilterProxyModel(self.ui.jobs_view)
        proxy_model.setSourceModel(self.jobs_model)
        proxy_model.setSortCaseSensitivity(Qt.Qt.CaseInsensitive)
        proxy_model.setSortLocaleAware(True)
        proxy_model.setSortRole(Qt.Qt.DisplayRole)
        proxy_model.sort(
            JobsModel.COLUMN_NAME,
            Qt.Qt.AscendingOrder,
        )
        self.ui.jobs_view.setModel(
            proxy_model,
        )
        self.ui.jobs_view.horizontalHeader().setSectionResizeMode(
            Qt.QHeaderView.ResizeToContents
        )
        self.ui.jobs_view.horizontalHeader().setSortIndicator(
            JobsModel.COLUMN_NAME,
            Qt.Qt.AscendingOrder,
        )


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-v",
        dest="verbosity",
        action="count",
        default=0,
        help="Increase verbosity (up to -vvv)"
    )

    args = parser.parse_args()

    logging.basicConfig(
        level={
            0: logging.ERROR,
            1: logging.WARNING,
            2: logging.INFO,
        }.get(args.verbosity, logging.DEBUG),
    )

    logger = logging.getLogger("qtborg.manager")

    logging.getLogger("quamash").setLevel(logging.INFO)

    Qt.QApplication.setAttribute(Qt.Qt.AA_UseHighDpiPixmaps)
    app = Qt.QApplication(sys.argv[:1])
    asyncio.set_event_loop(quamash.QEventLoop(app=app))

    signal.signal(
        signal.SIGINT,
        signal.SIG_DFL,
    )

    signal.signal(
        signal.SIGTERM,
        signal.SIG_DFL,
    )

    loop = asyncio.get_event_loop()
    try:
        main = MainWindow(loop, logger)
        main.show()
        rc = loop.run_forever()
        del main
        del app
        import gc
        gc.collect()
        sys.exit(rc)
    finally:
        loop.close()
