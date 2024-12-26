from PyQt5.QtWidgets import QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, QMessageBox
from auth import Auth
from ui.register_window import RegisterWindow
from ui.admin_dashboard import AdminDashboard
from ui.user_dashboard import UserDashboard


class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("物品复活系统 - 登录")
        self.setGeometry(300, 300, 400, 250)

        self.auth = Auth()

        # Login layout
        layout = QVBoxLayout()

        self.username_label = QLabel("用户名：")
        self.username_input = QLineEdit()
        self.password_label = QLabel("密码：")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        self.login_button = QPushButton("登录")
        self.register_button = QPushButton("注册账号")

        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)
        layout.addWidget(self.register_button)

        # Connect buttons
        self.login_button.clicked.connect(self.login)
        self.register_button.clicked.connect(self.open_register_window)

        # Set layout
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "警告", "请输入用户名和密码！")
            return

        message, user = self.auth.login(username, password)
        if user:
            QMessageBox.information(self, "提示", message)
            if user['is_admin']:
                self.admin_dashboard = AdminDashboard(user)
                self.admin_dashboard.show()
            else:
                self.user_dashboard = UserDashboard(user)
                self.user_dashboard.show()
            self.close()
        else:
            QMessageBox.critical(self, "错误", message)

    def open_register_window(self):
        self.register_window = RegisterWindow()
        self.register_window.show()
