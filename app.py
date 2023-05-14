from PySide6 import QtWidgets, QtCore
import sys
from pathlib import Path

from trends_contacts.domain import SearchInfo
from trends_contacts.use_cases import search, create_driver, to_excel
from trends_contacts.helpers import create_layout_directory_dialog, Button


class Main(QtWidgets.QWidget):

    def __init__(self) -> None:
        super().__init__()
        self.message_box = QtWidgets.QMessageBox()
        self.setStyleSheet('font-size: 20px')
        self.setFixedSize(400, 250)

        self.driver = create_driver(visible=True)

        self.message_box = QtWidgets.QMessageBox()

        self.label_cnae = QtWidgets.QLabel('CNAE: ')
        self.input_cnae = QtWidgets.QLineEdit()
        self.layout_cnae = QtWidgets.QHBoxLayout()
        self.layout_cnae.addWidget(self.label_cnae)
        self.layout_cnae.addWidget(self.input_cnae)

        self.label_state = QtWidgets.QLabel('Estado: ')
        self.input_state = QtWidgets.QLineEdit()
        self.layout_state = QtWidgets.QHBoxLayout()
        self.layout_state.addWidget(self.label_state)
        self.layout_state.addWidget(self.input_state)

        self.label_city = QtWidgets.QLabel('Cidade: ')
        self.input_city = QtWidgets.QLineEdit()
        self.layout_city = QtWidgets.QHBoxLayout()
        self.layout_city.addWidget(self.label_city)
        self.layout_city.addWidget(self.input_city)

        self.label_directory = QtWidgets.QLabel('Pasta destino:')
        self.layout_directory_dialog = create_layout_directory_dialog(self)

        self.button = Button('Gerar Planilha')
        self.button.clicked.connect(self.main)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addLayout(self.layout_cnae)
        self.layout.addLayout(self.layout_state)
        self.layout.addLayout(self.layout_city)
        self.layout.addWidget(self.label_directory)
        self.layout.addLayout(self.layout_directory_dialog)
        self.layout.addWidget(self.button)

    @QtCore.Slot()
    def main(self) -> None:
        self.message_box.show()
        self.message_box.setText('Gerando planilha...')
        cnaes, state, city = (
            self.input_cnae.text(),
            self.input_state.text(),
            self.input_city.text(),
        )
        filename = f'{state}_{city}.xlsx'
        path = str(Path(self.findChild(QtWidgets.QLineEdit).text()) / filename)
        contacts = []
        for cnae in cnaes.split():
            search_info = SearchInfo(cnae=cnae, state=state, city=city)
            self.driver.delete_all_cookies()
            contacts.extend(search(self.driver, search_info))
        to_excel(path, contacts)
        self.message_box.setText('Concluido!')


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    widget = Main()
    widget.show()
    sys.exit(app.exec())
