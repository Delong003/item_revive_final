from PyQt5.QtWidgets import (
    QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget,
    QTableWidget, QTableWidgetItem, QMessageBox, QInputDialog, QHBoxLayout
)
import json
from db import Database


class AdminDashboard(QMainWindow):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.db = Database()
        self.setWindowTitle(f"管理员界面 - 欢迎 {self.user['username']}")
        self.setGeometry(300, 300, 600, 400)

        layout = QVBoxLayout()

        self.view_users_button = QPushButton("查看待审批用户")
        self.view_users_button.clicked.connect(self.view_pending_users)

        self.create_type_button = QPushButton("创建物品类型")
        self.create_type_button.clicked.connect(self.create_item_type)

        self.modify_type_button = QPushButton("修改物品类型")
        self.modify_type_button.clicked.connect(self.modify_item_type)

        # 退出登录按钮
        self.logout_button = QPushButton("退出登录")
        self.logout_button.clicked.connect(self.logout)

        layout.addWidget(self.view_users_button)
        layout.addWidget(self.create_type_button)
        layout.addWidget(self.modify_type_button)
        layout.addWidget(self.logout_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def view_pending_users(self):
        users = self.db.query(
            "SELECT * FROM users WHERE is_approved = FALSE AND is_admin = FALSE")
        if not users:
            QMessageBox.information(self, "信息", "没有待审批用户。")
            return

        # 创建一个主窗口小部件来容纳布局
        self.pending_users_widget = QWidget()

        # 创建垂直布局
        main_layout = QVBoxLayout()

        # 为每个用户创建水平布局
        for user in users:
            user_layout = QHBoxLayout()

            # 添加用户名和邮箱标签
            username_label = QLabel(user['username'])
            email_label = QLabel(user['email'])
            user_layout.addWidget(username_label)
            user_layout.addWidget(email_label)

            # 添加批准按钮
            approve_button = QPushButton("批准")
            approve_button.clicked.connect(
                lambda: self.approve_user(user['id']))
            user_layout.addWidget(approve_button)
            # 添加拒绝按钮
            reject_button = QPushButton("拒绝")
            reject_button.clicked.connect(
                lambda checked, user_id=user['id']: self.reject_user(user_id))
            user_layout.addWidget(reject_button)

            # 将每个用户的布局添加到主垂直布局
            main_layout.addLayout(user_layout)

        # 设置窗口小部件的布局
        self.pending_users_widget.setLayout(main_layout)
        self.pending_users_widget.show()

    def approve_user(self, user_id):
        self.db.execute(
            "UPDATE users SET is_approved = TRUE WHERE id = %s", (user_id,))
        QMessageBox.information(self, "信息", f"用户 {user_id} 已批准！")
        self.pending_users_widget.close()  # 关闭待审批用户列表窗口
        self.view_pending_users()  # 刷新待审批用户列表

    def reject_user(self, user_id):
        self.db.execute("DELETE FROM users WHERE id = %s", (user_id,))
        QMessageBox.information(self, "信息", f"用户 {user_id} 已拒绝！")
        self.pending_users_widget.close()  # 关闭待审批用户列表窗口
        self.view_pending_users()  # 刷新待审批用户列表

    def create_item_type(self):
        # 获取物品类型名称
        name, ok = QInputDialog.getText(self, "创建物品类型", "请输入物品类型名称：")
        if not ok or not name.strip():
            QMessageBox.warning(self, "警告", "物品类型名称不能为空！")
            return

        # 获取物品类型的属性和类型
        attributes, ok = QInputDialog.getText(self, "创建物品类型",
                                              "请输入此类型的属性名和类型（逗号分隔，格式：name:type）：")
        if not ok or not attributes.strip():
            QMessageBox.warning(self, "警告", "物品类型必须有属性！")
            return

        # 解析属性和类型
        attributes_dict = {}
        attributes_list = attributes.split(',')
        for attr in attributes_list:
            attr = attr.strip()
            if ':' not in attr:
                QMessageBox.warning(
                    self, "警告", f"无效的属性格式: {attr}. 格式应为 'name:type'")
                return
            attr_name, attr_type = attr.split(':')
            attributes_dict[attr_name.strip()] = attr_type.strip()

        # 将属性字典转换为 JSON 格式存储
        attributes_json = json.dumps(attributes_dict)

        try:
            # 插入物品类型
            self.db.execute(
                "INSERT INTO item_types (name, attributes) VALUES (%s, %s)", (name, attributes_json))
            breakpoint()
            # 获取物品类型的ID
            type_id = self.db.query("SELECT LAST_INSERT_ID() AS id")[0]['id']

            # 动态创建物品类型的属性表
            table_name = name  # 用物品类型名称作为表名（首字母大写）

            # Construct the column definitions properly, including spaces between column names and types
            columns = [f"item_id INT NOT NULL"]
            for attr, attr_type in attributes_dict.items():
                columns.append(f"{attr} {self.convert_type(attr_type)}")

            # Create the table with a dynamically constructed SQL query
            create_table_query = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id INT AUTO_INCREMENT PRIMARY KEY,
                {', '.join(columns)},
                FOREIGN KEY (item_id) REFERENCES items(id)
            );
            """
            # Execute the create table query
            self.db.execute(create_table_query)

            QMessageBox.information(self, "信息", f"物品类型 {name} 已创建，且对应的表格已生成！")

        except Exception as e:
            QMessageBox.critical(self, "错误", f"数据库错误: {e}")

    def modify_item_type(self):
        # 获取所有物品类型
        item_types = self.db.query("SELECT * FROM item_types")
        if not item_types:
            QMessageBox.information(self, "信息", "没有物品类型可供修改。")
            return

        # 展示所有物品类型供选择
        type_names = [item_type['name'] for item_type in item_types]
        type_name, ok = QInputDialog.getItem(
            self, "选择物品类型", "请选择要修改的物品类型：", type_names, 0, False)
        if not ok or not type_name:
            return

        # 获取该物品类型的当前属性
        type_data = next(
            item_type for item_type in item_types if item_type['name'] == type_name)
        attributes = json.loads(type_data['attributes'])

        # 显示当前属性
        attributes_str = ", ".join(
            f"{key}: {value}" for key, value in attributes.items())
        new_attributes, ok = QInputDialog.getText(self, "修改物品类型属性",
                                                  f"当前属性: {attributes_str}\n请输入新的属性名和类型（逗号分隔，格式：name:type）：")
        if not ok or not new_attributes.strip():
            return

        # 解析新的属性列表
        new_attributes_dict = {}
        new_attributes_list = new_attributes.split(',')
        for attr in new_attributes_list:
            attr = attr.strip()
            if ':' not in attr:
                QMessageBox.warning(
                    self, "警告", f"无效的属性格式: {attr}. 格式应为 'name:type'")
                return
            attr_name, attr_type = attr.split(':')
            new_attributes_dict[attr_name.strip()] = attr_type.strip()

        # 将新的属性字典转换为 JSON 格式
        new_attributes_json = json.dumps(new_attributes_dict)

        try:
            # 更新物品类型的属性
            self.db.execute(
                "UPDATE item_types SET attributes = %s WHERE name = %s", (new_attributes_json, type_name))

            # 动态修改物品类型的属性表
            table_name = type_name.capitalize()  # 用物品类型名称作为表名（首字母大写）

            # 获取现有表的属性列
            current_columns = self.db.query(f"SHOW COLUMNS FROM {table_name}")
            existing_columns = {column['Field'] for column in current_columns}

            # 1. 删除不在新属性列表中的旧列
            for column in existing_columns:
                if column not in new_attributes_dict and column != 'item_id':
                    drop_column_query = f"ALTER TABLE {table_name} DROP COLUMN {column}"
                    self.db.execute(drop_column_query)

            # 2. 添加新的属性列（如果不存在的话）
            for attr, attr_type in new_attributes_dict.items():
                if attr not in existing_columns:
                    # 动态添加新列
                    add_column_query = f"ALTER TABLE {table_name} ADD COLUMN {attr} {self.convert_type(attr_type)}"
                    self.db.execute(add_column_query)

            QMessageBox.information(
                self, "信息", f"物品类型 {type_name} 的属性已修改，且表格已更新！")

        except Exception as e:
            QMessageBox.critical(self, "错误", f"数据库错误: {e}")

    def convert_type(self, attr_type):
        if attr_type.lower() == 'string':
            return 'VARCHAR(255)'
        elif attr_type.lower() == 'int':
            return 'INT'
        elif attr_type.lower() == 'float':
            return 'FLOAT'
        elif attr_type.lower() == 'boolean':
            return 'BOOLEAN'
        else:
            return 'VARCHAR(255)'

    def logout(self):
        # 处理退出登录的逻辑
        reply = QMessageBox.question(self, "确认退出", "您确定要退出登录吗？",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            # 在这里处理注销逻辑，如转到登录界面或关闭应用程序
            QMessageBox.information(self, "信息", "您已退出登录。")
            self.close()  # 关闭当前窗口
            from ui.login_window import LoginWindow
            # 切换到登录窗口
            self.login_window = LoginWindow()
            self.login_window.show()
