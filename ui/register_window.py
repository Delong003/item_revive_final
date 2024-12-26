from PyQt5.QtWidgets import QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, QMessageBox
from auth import Auth


class RegisterWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("用户注册")
        self.setGeometry(300, 300, 400, 400)

        self.auth = Auth()

        layout = QVBoxLayout()

        self.username_label = QLabel("用户名：")
        self.username_input = QLineEdit()

        self.password_label = QLabel("密码：")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        self.email_label = QLabel("邮箱：")
        self.email_input = QLineEdit()

        self.phone_label = QLabel("手机：")
        self.phone_input = QLineEdit()

        self.address_label = QLabel("地址：")
        self.address_input = QLineEdit()

        self.register_button = QPushButton("提交注册")

        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.email_label)
        layout.addWidget(self.email_input)
        layout.addWidget(self.phone_label)
        layout.addWidget(self.phone_input)
        layout.addWidget(self.address_label)
        layout.addWidget(self.address_input)
        layout.addWidget(self.register_button)

        self.register_button.clicked.connect(self.register_user)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def register_user(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        email = self.email_input.text().strip()
        phone = self.phone_input.text().strip()
        address = self.address_input.text().strip()

        if not username or not password or not email or not phone or not address:
            QMessageBox.warning(self, "警告", "请完整填写所有字段！")
            return

        message = self.auth.register(username, password, email, phone, address)
        QMessageBox.information(self, "提示", message)
        if "成功" in message:
            self.close()
