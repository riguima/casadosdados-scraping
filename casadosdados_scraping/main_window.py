from datetime import datetime, date
from pathlib import Path

from PySide6 import QtCore, QtGui, QtWidgets

from casadosdados_scraping.browser import Browser
from casadosdados_scraping.utils import to_excel


class MainWindow(QtWidgets.QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.message_box = QtWidgets.QMessageBox()
        with open(Path('styles.qss').absolute(), 'r') as file:
            self.setStyleSheet(file.read())

        self.browser = Browser(headless=False)

        self.message_box = QtWidgets.QMessageBox()

        self.fantasy_name_label = QtWidgets.QLabel('Nome Fantasia:')
        self.fantasy_name_input = QtWidgets.QLineEdit()
        self.fantasy_name_layout = QtWidgets.QHBoxLayout()
        self.fantasy_name_layout.addWidget(self.fantasy_name_label)
        self.fantasy_name_layout.addWidget(self.fantasy_name_input)

        self.cnae_label = QtWidgets.QLabel('CNAE:')
        self.cnae_combobox = QtWidgets.QComboBox()
        self.cnae_combobox.addItem('Todas')
        self.cnae_combobox.addItems(self.browser.get_cnaes())
        self.cnae_layout = QtWidgets.QHBoxLayout()
        self.cnae_layout.addWidget(self.cnae_label)
        self.cnae_layout.addWidget(self.cnae_combobox)

        self.juridical_nature_label = QtWidgets.QLabel('Natureza Jurídica:')
        self.juridical_nature_combobox = QtWidgets.QComboBox()
        self.juridical_nature_combobox.addItem('Todas')
        self.juridical_nature_combobox.addItems(
            self.browser.get_juridical_nature()
        )
        self.juridical_nature_layout = QtWidgets.QHBoxLayout()
        self.juridical_nature_layout.addWidget(self.juridical_nature_label)
        self.juridical_nature_layout.addWidget(self.juridical_nature_combobox)

        self.registration_status_label = QtWidgets.QLabel('Situação Cadastral')
        self.registration_status_combobox = QtWidgets.QComboBox()
        self.registration_status_combobox.addItems(
            ['Ativa', 'Baixada', 'Inapta', 'Suspensa', 'Nula']
        )
        self.registration_status_layout = QtWidgets.QHBoxLayout()
        self.registration_status_layout.addWidget(
            self.registration_status_label
        )
        self.registration_status_layout.addWidget(
            self.registration_status_combobox
        )

        self.state_label = QtWidgets.QLabel('Estado:')
        self.state_combobox = QtWidgets.QComboBox()
        self.state_combobox.addItem('Todos')
        self.state_combobox.addItems(self.browser.get_states())
        self.state_layout = QtWidgets.QHBoxLayout()
        self.state_layout.addWidget(self.state_label)
        self.state_layout.addWidget(self.state_combobox)

        self.city_label = QtWidgets.QLabel('Cidade:')
        self.city_combobox = QtWidgets.QComboBox()
        self.city_layout = QtWidgets.QHBoxLayout()
        self.city_layout.addWidget(self.city_label)
        self.city_layout.addWidget(self.city_combobox)

        self.state_combobox.currentTextChanged.connect(
            self.update_city_combobox
        )
        self.update_city_combobox()

        self.neighborhood_label = QtWidgets.QLabel('Bairro:')
        self.neighborhood_input = QtWidgets.QLineEdit()
        self.neighborhood_layout = QtWidgets.QHBoxLayout()
        self.neighborhood_layout.addWidget(self.neighborhood_label)
        self.neighborhood_layout.addWidget(self.neighborhood_input)

        self.cep_label = QtWidgets.QLabel('CEP:')
        self.cep_input = QtWidgets.QLineEdit()
        self.cep_layout = QtWidgets.QHBoxLayout()
        self.cep_layout.addWidget(self.cep_label)
        self.cep_layout.addWidget(self.cep_input)

        self.ddd_label = QtWidgets.QLabel('DDD:')
        self.ddd_input = QtWidgets.QLineEdit()
        self.ddd_input.setValidator(
            QtGui.QRegularExpressionValidator(r'\d{2}')
        )
        self.ddd_layout = QtWidgets.QHBoxLayout()
        self.ddd_layout.addWidget(self.ddd_label)
        self.ddd_layout.addWidget(self.ddd_input)

        self.from_opening_date_label = QtWidgets.QLabel('Data de Abertura (De)', alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        self.from_opening_date_calendar = QtWidgets.QCalendarWidget()
        self.from_opening_date_layout = QtWidgets.QVBoxLayout()
        self.from_opening_date_layout.addWidget(self.from_opening_date_label)
        self.from_opening_date_layout.addWidget(self.from_opening_date_calendar)

        self.to_opening_date_label = QtWidgets.QLabel('Data de Abertura (Até)', alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        self.to_opening_date_calendar = QtWidgets.QCalendarWidget()
        self.to_opening_date_layout = QtWidgets.QVBoxLayout()
        self.to_opening_date_layout.addWidget(self.to_opening_date_label)
        self.to_opening_date_layout.addWidget(self.to_opening_date_calendar)

        self.calendars_layout = QtWidgets.QHBoxLayout()
        self.calendars_layout.addLayout(self.from_opening_date_layout)
        self.calendars_layout.addLayout(self.to_opening_date_layout)

        self.from_share_capital_label = QtWidgets.QLabel(
            'Capital Social (De):'
        )
        self.from_share_capital_input = QtWidgets.QLineEdit()
        self.from_share_capital_input.setValidator(
            QtGui.QRegularExpressionValidator(r'\d+,\d{2}')
        )
        self.from_share_capital_layout = QtWidgets.QHBoxLayout()
        self.from_share_capital_layout.addWidget(self.from_share_capital_label)
        self.from_share_capital_layout.addWidget(self.from_share_capital_input)

        self.to_share_capital_label = QtWidgets.QLabel('Capital Social (Até):')
        self.to_share_capital_input = QtWidgets.QLineEdit()
        self.to_share_capital_input.setValidator(
            QtGui.QRegularExpressionValidator(r'\d+,\d{2}')
        )
        self.to_share_capital_layout = QtWidgets.QHBoxLayout()
        self.to_share_capital_layout.addWidget(self.to_share_capital_label)
        self.to_share_capital_layout.addWidget(self.to_share_capital_input)

        self.destination_folder_label = QtWidgets.QLabel('Pasta destino:')
        self.destination_folder_input = QtWidgets.QLineEdit()
        self.destination_folder_button = QtWidgets.QPushButton('Selecionar')
        self.destination_folder_button.clicked.connect(
            self.choose_destination_folder
        )
        self.destination_folder_layout = QtWidgets.QHBoxLayout()
        self.destination_folder_layout.addWidget(self.destination_folder_label)
        self.destination_folder_layout.addWidget(self.destination_folder_input)
        self.destination_folder_layout.addWidget(
            self.destination_folder_button
        )

        self.generate_worksheet_button = QtWidgets.QPushButton(
            'Gerar Planilha'
        )
        self.generate_worksheet_button.clicked.connect(self.generate_worksheet)

        self.inputs_layout = QtWidgets.QVBoxLayout()
        self.inputs_layout.addLayout(self.fantasy_name_layout)
        self.inputs_layout.addLayout(self.cnae_layout)
        self.inputs_layout.addLayout(self.juridical_nature_layout)
        self.inputs_layout.addLayout(self.registration_status_layout)
        self.inputs_layout.addLayout(self.state_layout)
        self.inputs_layout.addLayout(self.city_layout)
        self.inputs_layout.addLayout(self.neighborhood_layout)
        self.inputs_layout.addLayout(self.cep_layout)
        self.inputs_layout.addLayout(self.ddd_layout)
        self.inputs_layout.addLayout(self.calendars_layout)
        self.inputs_layout.addLayout(self.from_share_capital_layout)
        self.inputs_layout.addLayout(self.to_share_capital_layout)
        self.inputs_layout.addLayout(self.destination_folder_layout)
        self.inputs_layout.addWidget(self.generate_worksheet_button)

        self.options_label = QtWidgets.QLabel('Opções', alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        self.includes_secondary_activity = QtWidgets.QCheckBox('Incluir Atividade Secundária')
        self.only_mei_checkbox = QtWidgets.QCheckBox('Somente MEI')
        self.remove_mei_checkbox = QtWidgets.QCheckBox('Excluir MEI')
        self.only_matriz_checkbox = QtWidgets.QCheckBox('Somente Matriz')
        self.only_filial_checkbox = QtWidgets.QCheckBox('Somente Filial')
        self.with_phone_number_checkbox = QtWidgets.QCheckBox('Com Contato de Telefone')
        self.only_phone_checkbox = QtWidgets.QCheckBox('Somente Fixo')
        self.only_smartphone_checkbox = QtWidgets.QCheckBox('Somente Celular')
        self.with_email_checkbox = QtWidgets.QCheckBox('Com E-mail')

        self.options_layout = QtWidgets.QVBoxLayout()
        self.options_layout.addStretch()
        self.options_layout.addWidget(self.options_label)
        self.options_layout.addWidget(self.only_mei_checkbox)
        self.options_layout.addWidget(self.remove_mei_checkbox)
        self.options_layout.addWidget(self.only_matriz_checkbox)
        self.options_layout.addWidget(self.only_filial_checkbox)
        self.options_layout.addWidget(self.with_phone_number_checkbox)
        self.options_layout.addWidget(self.only_phone_checkbox)
        self.options_layout.addWidget(self.only_smartphone_checkbox)
        self.options_layout.addWidget(self.with_email_checkbox)
        self.options_layout.addStretch()

        self.main_layout = QtWidgets.QHBoxLayout(self)
        self.main_layout.addLayout(self.inputs_layout)
        self.main_layout.addLayout(self.options_layout)

    @QtCore.Slot()
    def update_city_combobox(self):
        self.city_combobox.clear()
        self.city_combobox.addItem('Todas')
        if self.state_combobox.currentText() != 'Todos':
            self.city_combobox.addItems(
                self.browser.get_cities(self.state_combobox.currentText())
            )

    @QtCore.Slot()
    def choose_destination_folder(self):
        self.destination_folder_input.setText(
            str(
                QtWidgets.QFileDialog.getExistingDirectory(
                    self, 'Selecione uma pasta'
                )
            )
        )

    @QtCore.Slot()
    def generate_worksheet(self) -> None:
        self.message_box.setText('Gerando planilha...')
        self.message_box.show()
        filename = (
            f'search_result_{datetime.now().strftime("%d/%m/%Y %H:%M:%S")}'
        )
        path = str(
            Path(self.destination_folder_input.text()).absolute() / filename
        )
        from_opening_date = self.from_opening_date_calendar.selectedDate()
        to_opening_date = self.to_opening_date_calendar.selectedDate()
        search_info = {
            'fantasy_name': self.fantasy_name_input.text(),
            'cnae': self.cnae_combobox.currentText(),
            'juridical_nature': self.juridical_nature_combobox.currentText(),
            'registration_status': self.registration_status_combobox.currentText(),
            'state': self.state_combobox.currentText(),
            'city': self.city_combobox.currentText(),
            'neighborhood': self.neighborhood_input.text(),
            'cep': self.cep_input.text(),
            'ddd': self.ddd_input.text(),
            'from_opening_date': date(from_opening_date.year(), from_opening_date.month(), from_opening_date.day()),
            'to_opening_date': date(to_opening_date.year(), to_opening_date.month(), to_opening_date.day()),
            'from_share_capital': self.from_share_capital_input.text(),
            'to_share_capital': self.to_share_capital_input.text(),
            'includes_secondary_activity': self.includes_secondary_activity.isChecked(),
            'only_mei': self.only_mei_checkbox.isChecked(),
            'remove_mei': self.remove_mei_checkbox.isChecked(),
            'only_matriz': self.only_matriz_checkbox.isChecked(),
            'only_filial': self.only_filial_checkbox.isChecked(),
            'with_phone_number': self.with_phone_number_checkbox.isChecked(),
            'only_phone': self.only_phone_checkbox.isChecked(),
            'only_smartphone': self.only_smartphone_checkbox.isChecked(),
            'with_email': self.with_email_checkbox.isChecked(),
        }
        to_excel(path, self.browser.search(search_info))
        self.message_box.setText('Concluido!')
        self.message_box.show()
