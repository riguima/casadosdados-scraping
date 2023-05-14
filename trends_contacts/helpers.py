from PySide6 import QtWidgets


class Button(QtWidgets.QPushButton):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.setStyleSheet('background-color: #187bcd; color: white')


def create_layout_directory_dialog(widget: QtWidgets.QWidget
                                   ) -> QtWidgets.QHBoxLayout:
    line_edit = QtWidgets.QLineEdit(widget)
    button = Button('Selecionar')
    button.clicked.connect(lambda: open_directory_dialog(widget, line_edit))
    layout = QtWidgets.QHBoxLayout()
    layout.addWidget(line_edit)
    layout.addWidget(button)
    return layout


def open_directory_dialog(widget: QtWidgets.QWidget,
                          target_input: QtWidgets.QLineEdit) -> None:
    result = str(QtWidgets.QFileDialog.getExistingDirectory(
        widget, 'Selecione uma pasta'))
    target_input.setText(result)
