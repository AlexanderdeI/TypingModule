import os
import threading
import traceback

from osgeo import ogr
from PyQt5.QtCore import QDate, QObject, Qt, pyqtSignal
from PyQt5.QtWidgets import (QBoxLayout, QComboBox, QDesktopWidget, QFileDialog, QFormLayout, QGridLayout,
                             QHBoxLayout, QLabel, QLineEdit, QMessageBox, QPushButton, QVBoxLayout, QWidget)

from .photo_viewer import PhotoViewer
from .useful_func import *
from .settings import *


class SignalSender(QObject):
    birth_update = pyqtSignal()
    death_update = pyqtSignal()


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

        self.current_layer = None
        self.gpkg_layer = None
        self.current_index = None
        self.graves = list()
        self.source = None

        self.auto_saver = None
        self.signal_sender = SignalSender()

        self.widget_fields_dict = {
            self.surname: {'field': SURNAME},
            self.name: {'field': NAME},
            self.middlename: {'field': MIDDLENAME},
            self.birth: {'field': BIRTH},
            self.death: {'field': DEATH},
            self.gravetype: {'field': GRAVETYPE},
            self.condition: {'field': CONDITION},
            self.comment: {'field': COMMENT}
        }

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Модуль набора')
        if PHOTO_POSITION == 'LEFT':
            self.grid.addLayout(self._create_viwer_layout(), 1, 1)
            self.grid.addLayout(self._create_form_layout(), 1, 2)
        elif PHOTO_POSITION == 'RIGHT':
            self.grid.addLayout(self._create_form_layout(), 1, 1)
            self.grid.addLayout(self._create_viwer_layout(), 1, 2)
        self.setMinimumWidth(int(self.screen.width() * 0.9))
        self._connect_buttons()
        self.setLayout(self.grid)
        self.update_layers()
        self.layers.setDisabled(True)
        self.ok_button.setDisabled(True)
        self.switch_widgets()

    def closeEvent(self, event):
        close = QMessageBox()
        close.setText("Вы уверены?")
        close.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        close = close.exec()

        if close == QMessageBox.Yes:
            self.end_transaction()
            event.accept()
        else:
            event.ignore()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Up:
            self.previous_record()
        if event.key() == Qt.Key_Down:
            self.next_record()
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            if self.next.hasFocus():
                self.next_record()
            else:
                self.focusNextChild()
        if event.key() == Qt.Key_Escape:
            self.close()

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
        buttons.setDirection(QBoxLayout.RightToLeft)
        buttons.addStretch(1)
        buttons.addWidget(self.next, 2)
        buttons.addStretch(1)
        buttons.addWidget(self.previous, 2)
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

    def switch_widgets(self):
        widgets1 = [self.layers, self.ok_button, self.change_button,
            self.count, self.fid_input, self.go_to_fid_button,
            self.surname, self.name, self.middlename,
            self.birth, self.death, self.gravetype, self.condition,
            self.photo_number, self.change_photo_button, self.photo2_button,
            self.next, self.previous, self.age, self.comment]
        for w in widgets1:
            if w.isEnabled():
                w.setDisabled(True)
                continue
            w.setDisabled(False)

    def _connect_buttons(self):
        self.ok_button.clicked.connect(self.on_ok_button)
        self.change_button.clicked.connect(self.on_change_button)
        self.next.clicked.connect(self.next_record)
        self.previous.clicked.connect(self.previous_record)
        self.go_to_fid_button.clicked.connect(self.on_go_to_fid_button)
        self.photo2_button.clicked.connect(self.on_photo2_button)
        self.change_photo_button.clicked.connect(self.on_change_photo_button)

    def on_ok_button(self):
        self.switch_widgets()
        self.current_layer = self.iface.mapCanvas().layers()[self.layers.currentIndex()]
        if self.current_layer.dataProvider().dataSourceUri().split('|')[0].split('.')[-1] == 'gpkg':
            self.open_geopackage()
            self.start_transaction()
            self._connect_edit_funcs()
            self._connect_signals()

    def start_transaction(self):
        if self.gpkg_layer:
            self.gpkg_layer.StartTransaction()
            self.save_transaction()
            self.auto_saver = threading.Timer(AUTOSAVE_TIME, self.save_transaction)
            self.auto_saver.start()

    def save_transaction(self):
        if self.gpkg_layer:
            self.gpkg_layer.CommitTransaction()

    def end_transaction(self):
        self.switch_widgets()
        if self.gpkg_layer:
            self.gpkg_layer.CommitTransaction()
        if self.source:
            self.auto_saver.cancel()
            self.auto_saver = None
            self.gpkg_layer = None
            self.source.Destroy()

    def _connect_edit_funcs(self):
        self.surname.textChanged.connect(lambda: title_text(self.surname))
        self.name.textChanged.connect(lambda: title_text(self.name))
        self.middlename.textChanged.connect(lambda: title_text(self.middlename))

        self.surname.editingFinished.connect(self.save_edit_for_surname)
        self.name.editingFinished.connect(self.save_edit_for_name)
        self.middlename.editingFinished.connect(self.save_edit_for_middlename)
        self.birth.editingFinished.connect(lambda: self.save_edit_for_dates(self.birth, BIRTH))
        self.death.editingFinished.connect(lambda: self.save_edit_for_dates(self.death, DEATH))
        self.gravetype.editingFinished.connect(lambda: self.save_edit_for_tc(self.gravetype, GRAVETYPE))
        self.condition.editingFinished.connect(lambda: self.save_edit_for_tc(self.condition, CONDITION))
        self.comment.editingFinished.connect(self.save_edit_for_comment)

    def _connect_signals(self):
        self.signal_sender.birth_update.connect(lambda: self.save_edit_for_dates(self.birth, BIRTH))
        self.signal_sender.death_update.connect(lambda: self.save_edit_for_dates(self.death, DEATH))

    def on_change_button(self):
        self.end_transaction()

    def next_record(self):
        if self.current_index == len(self.graves) - 1:
            self.current_index = 0
        else:
            self.current_index += 1
        self.get_grave_data()

    def previous_record(self):
        if self.current_index == 0:
            self.current_index = len(self.graves) - 1
        else:
            self.current_index -= 1
        self.get_grave_data()

    def on_go_to_fid_button(self):
        fid = int(self.fid_input.text())
        if len(str(fid)) >= 1 and (0 < fid <= int(self.get_max_fid())):
            grave = [grave for grave in self.graves if grave.GetFID() == fid][0]
            self.current_index = self.graves.index(grave) + 1
            self.previous_record()
        else:
            reply = QMessageBox.question(
                self, '', 'Недопустимый fid',
                QMessageBox.Ok
            )
            if reply == QMessageBox.Ok:
                self.fid_input.setText('')

    def on_photo2_button(self):
        grave = self.graves[self.current_index]
        photo1 = grave.GetField(PHOTO)
        photo2 = grave.GetField(PHOTO2)
        if photo1 == self.viewer.current_photo:
            self.viewer.open_photo(photo2)
            self.photo_number.setText(get_photo_number(photo1))
            self.photo2_button.setText('Первая фотография')
        elif photo2 == self.viewer.current_photo:
            self.viewer.open_photo(photo1)
            self.photo_number.setText(get_photo_number(photo2))
            self.photo2_button.setText('Вторая фотография')

    def on_change_photo_button(self):
        grave = self.graves[self.current_index]
        photo_path = QFileDialog().getOpenFileName(self, 'Выбрать фотографию')[0]
        if not photo_path.endswith(('.jpg', '.png', '.jpeg', '.gif')):
            return None
        if photo_path.rfind('DCIM') != -1:
            relative_path = photo_path[photo_path.rfind('DCIM'):]
        elif photo_path.rfind('Photos') != -1:
            relative_path = photo_path[photo_path.rfind('Photos'):]
        else:
            relative_path = photo_path
        current_photo = self.photo_number.text()
        if current_photo == get_photo_number(grave.GetField(PHOTO)):
            self.save_photo_change(grave, PHOTO, relative_path)
        elif current_photo == get_photo_number(grave.GetField(PHOTO2)):
            self.save_photo_change(grave, PHOTO2, relative_path)

    def save_photo_change(self, grave, field, path):
        grave.SetField(field, path)
        self.photo_number.setText(get_photo_number(path))
        self.save_to_gpkg(field, path)
        self.get_grave_data()

    def update_layers(self):
        self.layers.clear()
        layers = [layer.name() for layer in self.iface.mapCanvas().layers()]
        self.layers.addItems(layers)

    def open_geopackage(self):
        gpkg_path = self.current_layer.dataProvider().dataSourceUri().split('|')[0]
        if os.path.isfile(gpkg_path):
            self.source = ogr.Open(gpkg_path, update=True)
            self.gpkg_layer = self.source.GetLayerByName(GPKG_LAYER_NAME)
            self.current_index = 0
            self.viewer.photo_base_dir = gpkg_path[:gpkg_path.find('GIS')]
            self.get_graves()
            self.get_grave_data()

    def get_graves(self):
        if self.gpkg_layer:
            self.graves.clear()
            feature = self.gpkg_layer.GetNextFeature()
            while feature:
                self.graves.append(feature)
                feature = self.gpkg_layer.GetNextFeature()

    def get_grave_data(self):
        grave = self.graves[self.current_index]
        for widget in self.widget_fields_dict.keys():
            field = self.widget_fields_dict.get(widget)['field']
            if not grave.GetField(field):
                widget.setText('')
                continue
            try:
                if grave.GetFieldType(field) == 4: # String
                    widget.setText(grave.GetField(field))
                elif grave.GetFieldType(field) == 9: # Date
                    date = grave.GetField(field).split('/')
                    date.reverse()
                    widget.setText('.'.join(date))
                elif grave.GetFieldType(field) == 12: # Integer64
                    widget.setText(str(grave.GetField(field)))
            except (TypeError, AttributeError):
                traceback.print_exc()
                widget.setText('')
        self.viewer.open_photo(grave.GetField(PHOTO))
        self.photo_number.setText(get_photo_number(grave.GetField(PHOTO)))
        self.check_photo2(grave)
        self.update_age_widget()
        self.count.setText('fid: {0} из {1}'.format(grave.GetFID(), self.get_max_fid()))
        self.surname.setFocus()

    def check_photo2(self, grave):
        try:
            if grave.GetField(PHOTO2):
                self.photo2_button.setVisible(True)
            else:
                self.photo2_button.setVisible(False)
        except KeyError:
            self.photo2_button.setVisible(False)

    def update_age_widget(self):
        grave = self.graves[self.current_index]
        try:
            if len(grave.GetField(BIRTH)) and len(grave.GetField(DEATH)):
                birth = str_to_date(grave.GetField(BIRTH))
                death = str_to_date(grave.GetField(DEATH))
                age = round((death - birth).days / 365.24, 1)
                self.age.setText(str(age))
        except TypeError:
            self.age.setText('')

    def get_max_fid(self):
        graves = self.graves.copy()
        return sorted(graves, key=lambda i: i.GetFID())[-1].GetFID()

    def save_to_gpkg(self, field, value):
        grave = self.graves[self.current_index]
        feature = self.gpkg_layer.GetFeature(grave.GetFID())
        feature.SetField(field, value)
        self.gpkg_layer.SetFeature(feature)

    def save_null_value_to_date(self, field):
        grave = self.graves[self.current_index]
        index = grave.GetFieldIndex(field) + 1
        self.current_layer.dataProvider().changeAttributeValues(
            {grave.GetFID(): {index: QDate()}}
        )
        grave.SetField(field, self.gpkg_layer.GetFeature(grave.GetFID()).GetField(field))

    def save_edit_for_surname(self):
        new_surname = self.surname.text().title()
        if new_surname.lower() == 'не опознано':
            new_surname = 'Не опознано'
        self.surname.setText(new_surname)
        self.graves[self.current_index].SetField(SURNAME, new_surname)
        self.save_to_gpkg(SURNAME, new_surname)
        # self.update_surname_list()

    def save_edit_for_name(self):
        new_name = self.name.text().title()
        self.name.setText(new_name)
        self.graves[self.current_index].SetField(SURNAME, new_name)
        self.save_to_gpkg(NAME, new_name)

    def save_edit_for_middlename(self):
        new_middlename = self.middlename.text().title()
        self.middlename.setText(new_middlename)
        self.graves[self.current_index].SetField(MIDDLENAME, new_middlename)
        self.save_to_gpkg(MIDDLENAME, new_middlename)

    def save_edit_for_dates(self, line_edit, field):
        str_date = line_edit.text()
        autocomplete_value = (AUTOCOMPLETE_CENTURY -1) * 100
        if len(str_date) == 0:
            self.save_null_value_to_date(field)
            return None
        try:
            day, month, year = None, None, None
            if '.' in str_date:
                int_date = [int(s) for s in str_date.split('.')]
                day, month, year = int_date
                if len(str(year)) <= 2:
                    year += autocomplete_value
            elif '.' not in str_date:
                if len(str_date) == 4:
                    day = 1
                    month = 1
                    year = int(str_date)
                if len(str_date) == 8:
                    day = int(str_date[:2])
                    month = int(str_date[2:4])
                    year = int(str_date[4:])
            date = datetime.date(year, month, day).isoformat()
            self.save_to_gpkg(field, date)
            self.graves[self.current_index].SetField(field, date)
            line_edit.setText(format_date(date))
        except (ValueError, TypeError):
            line_edit.setText('')
        self.check_date()
        self.update_age_widget()

    def check_date(self):
        grave = self.graves[self.current_index]
        birth = grave.GetField(BIRTH)
        death = grave.GetField(DEATH)

        if not death and not birth:
            return None
        elif birth:
            self.check_if_lt_min_year(birth, BIRTH, self.birth)
            self.check_if_gt_today(birth, BIRTH, self.birth)
        elif death:
            self.check_if_lt_min_year(death, DEATH, self.death)
            self.check_if_gt_today(death, DEATH, self.death)

        if not death or not birth:
            return None

        self.check_negative_age(birth, death)
        self.check_if_age_gt_max(birth, death)

    def check_if_lt_min_year(self, str_date, field, widget):
        date = str_to_date(str_date)
        if date.year < MIN_YEAR:
            self.push_message('Год меньше чем {}'.format(MIN_YEAR))
            self.save_null_value_to_date(field)
            widget.setText('')

    def check_if_gt_today(self, str_date, field, widget):
        date = str_to_date(str_date)
        if date > TODAY:
            self.push_message('Больше чем текущая дата {}'.format(TODAY))
            self.save_null_value_to_date(field)
            widget.setText('')

    def check_negative_age(self, str_birth, str_death):
        birth, death = str_to_date(str_birth), str_to_date(str_death)
        if birth > death:
            self.save_null_value_to_date(BIRTH)
            self.save_null_value_to_date(DEATH)
            self.birth.setText('')
            self.death.setText('')
            self.push_message('Возраст не может быть отрицательным')

    def check_if_age_gt_max(self, str_birth, str_death):
        birth, death = str_to_date(str_birth), str_to_date(str_death)
        if death.year - birth.year > MAX_AGE:
            self.save_null_value_to_date(BIRTH)
            self.save_null_value_to_date(DEATH)
            self.birth.setText('')
            self.death.setText('')
            self.push_message('Жил/жила: {}'.format(death.year - birth.year))

    def push_message(self, msg):
        reply = QMessageBox.question(
            self, '', msg, QMessageBox.Ok
        )
        if reply == QMessageBox.Ok:
            pass

    def update_dates_on_age_edit(self):
        if len(self.age.text()) == 0:
            return None
        age = int(float(self.age.text()))
        if len(self.birth.text()) == 0 and len(self.death.text()) == 10:
            birth_year = int(self.death.text()[-4:]) - age
            self.birth.setText(str(birth_year))
            self.signal_sender.birth_update.emit()
        elif len(self.death.text()) == 0 and len(self.birth.text()) == 10:
            death_year = int(self.birth.text()[-4:]) + age
            self.death.setText(str(death_year))
            self.signal_sender.death_update.emit()

    def save_edit_for_tc(self, lineedit, field):
        if lineedit.text():
            value = int(lineedit.text())
            self.graves[self.current_index].SetField(field, value)
            self.save_to_gpkg(field, value)

    def save_edit_for_comment(self):
        comment = self.comment.text()
        self.graves[self.current_index].SetField(COMMENT, comment)
        self.save_to_gpkg(COMMENT, comment)
