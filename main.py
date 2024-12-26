import sys
from PyQt5.QtWidgets import QApplication
from ui.login_window import LoginWindow


def main():
    # 创建 PyQt 应用程序
    app = QApplication(sys.argv)

    # 初始化登录窗口
    login_window = LoginWindow()
    login_window.show()

    # 运行主事件循环
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
