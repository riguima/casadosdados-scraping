from pathlib import Path

from PySide6 import QtCore, QtWidgets

from casadosdados_scraping.browser import Browser
from casadosdados_scraping.utils import to_excel


class MainWindow(QtWidgets.QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.message_box = QtWidgets.QMessageBox()
        with open(Path('styles.qss').absolute(), 'r') as file:
            self.setStyleSheet(file.read())
        self.setFixedSize(400, 250)

        self.browser = Browser(headless=False)

        self.message_box = QtWidgets.QMessageBox()

        self.cnae_label = QtWidgets.QLabel('CNAE: ')
        self.cnae_combobox = QtWidgets.QComboBox()
        self.cnae_combobox.addItems(self.browser.get_cnaes())
        self.cnae_layout = QtWidgets.QHBoxLayout()
        self.cnae_layout.addWidget(self.cnae_label)
        self.cnae_layout.addWidget(self.cnae_combobox)

        self.state_label = QtWidgets.QLabel('Estado: ')
        self.state_combobox = QtWidgets.QComboBox()
        self.state_combobox.addItems(self.browser.get_states())
        self.state_layout = QtWidgets.QHBoxLayout()
        self.state_layout.addWidget(self.state_label)
        self.state_layout.addWidget(self.state_combobox)

        self.city_label = QtWidgets.QLabel('Cidade: ')
        self.city_combobox = QtWidgets.QComboBox()
        self.city_layout = QtWidgets.QHBoxLayout()
        self.city_layout.addWidget(self.city_label)
        self.city_layout.addWidget(self.city_combobox)

        self.state_combobox.currentTextChanged.connect(self.update_cities)
        self.update_cities()

        self.destination_folder_label = QtWidgets.QLabel('Pasta destino:')
        self.destination_folder_input = QtWidgets.QLineEdit()
        self.destination_folder_button = QtWidgets.QPushButton('Selecionar')
        self.destination_folder_button.clicked.connect(
            self.choose_destination_folder
        )
        self.destination_folder_layout = QtWidgets.QHBoxLayout()
        self.destination_folder_layout.addWidget(self.destination_folder_input)
        self.destination_folder_layout.addWidget(
            self.destination_folder_button
        )

        self.generate_worksheet_button = QtWidgets.QPushButton(
            'Gerar Planilha'
        )
        self.generate_worksheet_button.clicked.connect(self.generate_worksheet)

        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.addLayout(self.cnae_layout)
        self.main_layout.addLayout(self.state_layout)
        self.main_layout.addLayout(self.city_layout)
        self.main_layout.addWidget(self.destination_folder_label)
        self.main_layout.addLayout(self.destination_folder_layout)
        self.main_layout.addWidget(self.generate_worksheet_button)

    def update_cities(self):
        self.city_combobox.clear()
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
        cnae, state, city = (
            self.cnae_combobox.currentText().split(' - ')[0],
            self.state_combobox.currentText(),
            self.city_combobox.currentText(),
        )
        filename = f'{state}_{city}.xlsx'
        path = str(
            Path(self.destination_folder_input.text()).absolute() / filename
        )
        search_info = {'cnae': cnae, 'state': state, 'city': city}
        to_excel(path, self.browser.search(search_info))
        self.message_box.setText('Concluido!')
        self.message_box.show()
