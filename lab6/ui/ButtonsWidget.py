import PyQt6.QtWidgets
import PyQt6.QtGui
import PyQt6.QtCore


class ButtonsWidget(PyQt6.QtWidgets.QWidget):
    def __init__(self, parent: PyQt6.QtWidgets.QWidget | None = None):
        super().__init__(parent=parent)
        self.setFixedWidth(300)
        self.populate()
        self.apply_styles()

    def apply_styles(self):
        self.setStyleSheet("""
            QPushButton {
                background-color: #5A9BD5;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                color: white;
                font-weight: bold;
                font-size: 14px;
                margin-bottom: 10px;
                transition: background-color 0.3s ease;
            }
            QPushButton:hover {
                background-color: #4178BE;
            }
            QPushButton:pressed {
                background-color: #2D5A8A;
            }
            QSpinBox, QComboBox {
                font-size: 13px;
                padding: 5px;
                border: 1px solid #999;
                border-radius: 4px;
                min-width: 50px;
            }
            QLabel {
                font-weight: bold;
                font-size: 12px;
            }
            QWidget#groupBox {
                border: 1px solid #DDD;
                border-radius: 6px;
                margin-top: 10px;
                padding: 10px;
                background-color: #F3F6FB;
            }
        """)

    def populate(self):
        self.__main_layout = PyQt6.QtWidgets.QVBoxLayout(self)
        self.__main_layout.setContentsMargins(15, 15, 15, 15)
        self.__main_layout.setSpacing(12)

        # Open Images button
        self.open_images_button = PyQt6.QtWidgets.QPushButton(
            text="Open Images", parent=self
        )

        # RS Spinboxes with labels in a group box
        self.rs_group = PyQt6.QtWidgets.QGroupBox("RS Parameters", self)
        self.rs_group.setObjectName("groupBox")
        rs_layout = PyQt6.QtWidgets.QHBoxLayout(self.rs_group)
        rs_layout.setSpacing(10)

        self.rs_m_spinbox = PyQt6.QtWidgets.QSpinBox(self)
        self.rs_m_spinbox.setToolTip("RS m")
        self.rs_m_spinbox.setValue(2)
        rs_m_label = PyQt6.QtWidgets.QLabel("RS m:", self)
        rs_layout.addWidget(rs_m_label)
        rs_layout.addWidget(self.rs_m_spinbox)

        self.rs_n_spinbox = PyQt6.QtWidgets.QSpinBox(self)
        self.rs_n_spinbox.setToolTip("RS n")
        self.rs_n_spinbox.setValue(2)
        rs_n_label = PyQt6.QtWidgets.QLabel("RS n:", self)
        rs_layout.addWidget(rs_n_label)
        rs_layout.addWidget(self.rs_n_spinbox)

        # AUMP Spinboxes with labels in a group box
        self.aump_group = PyQt6.QtWidgets.QGroupBox("AUMP Parameters", self)
        self.aump_group.setObjectName("groupBox")
        aump_layout = PyQt6.QtWidgets.QHBoxLayout(self.aump_group)
        aump_layout.setSpacing(10)

        self.aump_block_size_spinbox = PyQt6.QtWidgets.QSpinBox(self)
        self.aump_block_size_spinbox.setToolTip("AUMP block size")
        self.aump_block_size_spinbox.setValue(16)
        aump_block_label = PyQt6.QtWidgets.QLabel("Block size:", self)
        aump_layout.addWidget(aump_block_label)
        aump_layout.addWidget(self.aump_block_size_spinbox)

        self.aump_parameter_spinbox = PyQt6.QtWidgets.QSpinBox(self)
        self.aump_parameter_spinbox.setToolTip("AUMP parameters")
        self.aump_parameter_spinbox.setValue(5)
        aump_param_label = PyQt6.QtWidgets.QLabel("Param:", self)
        aump_layout.addWidget(aump_param_label)
        aump_layout.addWidget(self.aump_parameter_spinbox)

        # Method dropdown with label
        method_layout = PyQt6.QtWidgets.QHBoxLayout()
        method_label = PyQt6.QtWidgets.QLabel("Method:", self)
        self.method_dropdown = PyQt6.QtWidgets.QComboBox(self)
        method_layout.addWidget(method_label)
        method_layout.addWidget(self.method_dropdown)

        # Buttons
        self.analyze_images_button = PyQt6.QtWidgets.QPushButton(
            text="Start Analyze", parent=self
        )
        self.save_resuts_button = PyQt6.QtWidgets.QPushButton(
            text="Save Results", parent=self
        )

        # Add widgets to main layout
        self.__main_layout.addWidget(self.open_images_button)
        self.__main_layout.addWidget(self.rs_group)
        self.__main_layout.addWidget(self.aump_group)
        self.__main_layout.addLayout(method_layout)
        self.__main_layout.addWidget(self.analyze_images_button)
        self.__main_layout.addWidget(self.save_resuts_button)
        self.__main_layout.addStretch()