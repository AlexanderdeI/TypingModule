from PyQt5.QtWidgets import (QComboBox, QDesktopWidget, QFormLayout, QGridLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QVBoxLayout, QWidget)

from .photo_viewer import PhotoViewer
from .usefull_func import *
from .settings import *


class TypingMenu(QWidget):

    def __init__(self, iface):
        QWidget.__init__(self)

        self.iface = iface
        self.grid = QGridLayout()
        self.screen = QDesktopWidget().screenGeometry()

        self.layers = QComboBox()
        self.ok_button = QPushButton('OK')
        self.change_button = QPushButton('Изменить')

        self.count = QLabel('fid: 0 из 0')
        self.fid_input = QLineEdit()
        self.go_to_fid_button = QPushButton('OK')

        # form features
        self.surname = QLineEdit()
        self.name = QLineEdit()
        self.middlename = QLineEdit()
        self.birth = QLineEdit()
        self.death = QLineEdit()
        self.gravetype = QLineEdit()
        self.condition = QLineEdit()

        self.viewer = PhotoViewer()
        self.photo_number = QLineEdit()
        self.change_photo_button = QPushButton('Изменить фотографию')
        self.photo2_button = QPushButton('Вторая фотография')

        self.next = QPushButton('Следующее >')
        self.previous = QPushButton('< Предыдущее')

        self.age = QLineEdit()
        self.comment = QLineEdit()

        self.initUI()

    def initUI(self):
        if PHOTO_POSITION == 'LEFT':
            self.grid.addLayout(self._create_viwer_layout(), 1, 1)
            self.grid.addLayout(self._create_form_layout(), 1, 2)
        elif PHOTO_POSITION == 'RIGHT':
            self.grid.addLayout(self._create_form_layout(), 1, 1)
            self.grid.addLayout(self._create_viwer_layout(), 1, 2)
        self.setMinimumWidth(int(self.screen.width() * 0.9))
        self._connect_buttons()
        self.setLayout(self.grid)

        disable_widget(
            self.change_button,
            self.count, self.fid_input, self.go_to_fid_button,
            self.surname, self.name, self.middlename,
            self.birth, self.death, self.gravetype, self.condition,
            self.photo_number, self.change_photo_button, self.photo2_button,
            self.next, self.previous, self.age, self.comment
        )

    def _create_viwer_layout(self):
        hbox = QHBoxLayout()
        vbox = QVBoxLayout()
        hbox.addWidget(self.photo_number, 3)
        hbox.addWidget(self.change_photo_button, 2)
        hbox.addWidget(self.photo2_button, 2)
        hbox.addStretch(1)
        vbox.addLayout(hbox)
        vbox.addWidget(self.viewer)
        return vbox

    def _create_form_layout(self):
        grid = QGridLayout()

        layers_menu = QGridLayout()
        fid_menu = QGridLayout()

        layers_menu.addWidget(self.layers, 1, 1, 1, 2)
        layers_menu.addWidget(self.ok_button, 1, 3)
        layers_menu.addWidget(self.change_button, 1, 4)

        fid_menu.addWidget(self.fid_input, 1, 1)
        fid_menu.addWidget(self.go_to_fid_button, 1, 2)

        fid_label = QHBoxLayout()
        fid_label.addStretch(1)
        fid_label.addWidget(self.count)
        fid_label.addStretch(1)

        fio_form = QFormLayout()
        fio_form.addRow(QLabel('Фамилия'), self.surname)
        fio_form.addRow(QLabel('Имя'), self.name)
        fio_form.addRow(QLabel('Отчество'), self.middlename)

        dtc_grid = QGridLayout()
        # first row
        dtc_grid.addWidget(QLabel('Дата рождения'), 1, 1)
        dtc_grid.addWidget(self.birth, 1, 2)
        dtc_grid.addWidget(QLabel('Дата смерти'), 1, 3)
        dtc_grid.addWidget(self.death, 1, 4)
        # second row
        dtc_grid.addWidget(QLabel('Тип захоронения'), 2, 1)
        dtc_grid.addWidget(self.gravetype, 2, 2)
        dtc_grid.addWidget(QLabel('Состояние'), 2, 3)
        dtc_grid.addWidget(self.condition, 2, 4)

        buttons = QHBoxLayout()
        buttons.addStretch(1)
        buttons.addWidget(self.previous, 2)
        buttons.addStretch(1)
        buttons.addWidget(self.next, 2)
        buttons.addStretch(1)

        stat_grid = QGridLayout()
        stat_grid.addWidget(QLabel('Возраст'), 1, 1)
        stat_grid.addWidget(self.age, 1, 2)
        stat_grid.addWidget(QLabel('Примечания'), 2, 1)
        stat_grid.addWidget(self.comment, 2, 2)

        grid.addLayout(layers_menu, 1, 1)
        grid.addLayout(fid_menu, 2, 1)
        grid.addLayout(fid_label, 3 ,1)
        grid.addLayout(fio_form, 4, 1)
        grid.addWidget(QLabel(), 5, 1)
        grid.addLayout(dtc_grid, 6, 1)
        grid.addWidget(QLabel(), 7, 1)
        grid.addWidget(QLabel(), 8, 1)
        grid.addLayout(buttons, 9, 1)
        grid.addWidget(QLabel(), 10, 1)
        grid.addLayout(stat_grid, 11, 1)
        set_spacing(fio_form, dtc_grid, stat_grid, h=25, v=30)
        grid.setContentsMargins(int(self.width() * 0.05), 0, int(self.width() * 0.05), 10)
        return grid

    def _connect_buttons(self):
        self.ok_button.clicked.connect(self.on_ok_button)
        self.change_button.clicked.connect(self.on_change_button)

    def on_ok_button(self):
        enable_widget(
            self.change_button,
            self.count, self.fid_input, self.go_to_fid_button,
            self.surname, self.name, self.middlename,
            self.birth, self.death, self.gravetype, self.condition,
            self.photo_number, self.change_photo_button, self.photo2_button,
            self.next, self.previous, self.age, self.comment
        )
        disable_widget(self.layers, self.ok_button)

    def on_change_button(self):
        disable_widget(
            self.change_button,
            self.count, self.fid_input, self.go_to_fid_button,
            self.surname, self.name, self.middlename,
            self.birth, self.death, self.gravetype, self.condition,
            self.photo_number, self.change_photo_button, self.photo2_button,
            self.next, self.previous, self.age, self.comment
        )
        enable_widget(self.layers, self.ok_button)