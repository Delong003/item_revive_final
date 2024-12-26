import json
from PyQt5.QtWidgets import (
    QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget,
    QTableWidget, QTableWidgetItem, QMessageBox, QInputDialog, QDialog
)
from db import Database


class UserDashboard(QMainWindow):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.db = Database()
        self.setWindowTitle(f"用户界面 - 欢迎 {self.user['username']}")
        self.setGeometry(300, 300, 600, 400)

        layout = QVBoxLayout()

        # 添加物品按钮
        self.add_item_button = QPushButton("添加物品")
        self.add_item_button.clicked.connect(self.add_item)

        # 查看物品按钮
        self.view_items_button = QPushButton("查看我的物品")
        self.view_items_button.clicked.connect(self.view_my_items)

        # 搜索物品按钮
        self.search_items_button = QPushButton("搜索物品")
        self.search_items_button.clicked.connect(self.search_items)

        # 删除物品按钮
        self.delete_item_button = QPushButton("删除物品")
        self.delete_item_button.clicked.connect(self.delete_item)

        # 退出登录按钮
        self.logout_button = QPushButton("退出登录")
        self.logout_button.clicked.connect(self.logout)

        # 添加按钮到布局
        layout.addWidget(self.add_item_button)
        layout.addWidget(self.view_items_button)
        layout.addWidget(self.search_items_button)
        layout.addWidget(self.delete_item_button)
        layout.addWidget(self.logout_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def add_item(self):
        name, ok = QInputDialog.getText(self, "添加物品", "请输入物品名称：")
        if not ok or not name.strip():
            QMessageBox.warning(self, "警告", "物品名称不能为空！")
            return

        description, ok = QInputDialog.getText(self, "添加物品", "请输入物品说明：")
        if not ok or not description.strip():
            QMessageBox.warning(self, "警告", "物品说明不能为空！")
            return

        address, ok = QInputDialog.getText(self, "添加物品", "请输入物品位置：")
        if not ok or not address.strip():
            QMessageBox.warning(self, "警告", "物品位置不能为空！")
            return

        # 获取物品类型和属性
        try:
            item_types = self.db.query("SELECT * FROM item_types")
            if not item_types:
                QMessageBox.warning(self, "警告", "无法加载物品类型！")
                return

            type_names = {item_type['name']
                : item_type for item_type in item_types}
        except Exception as e:
            QMessageBox.critical(self, "错误", f"数据库错误: {e}")
            return

        type_name, ok = QInputDialog.getItem(
            self, "添加物品", "请选择物品类型：", list(type_names.keys()), 0, False
        )
        if not ok or type_name not in type_names:
            QMessageBox.warning(self, "警告", "请选择一个有效的物品类型！")
            return

        phone = self.user.get('phone', '')
        email = self.user.get('email', '')

        try:
            # 插入物品
            self.db.execute(
                """
                INSERT INTO items (name, description, address, phone, email, type_id, created_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (name, description, address, phone, email,
                 type_names[type_name]['id'], self.user['id'])
            )
            item_id = self.db.query("SELECT LAST_INSERT_ID() AS id")[0]['id']

            # 获取类型对应的属性
            attributes = json.loads(type_names[type_name]['attributes'])
            attribute_values = {}

            for attr, attr_type in attributes.items():
                value, ok = QInputDialog.getText(
                    self, f"请输入{attr}", f"请输入{attr} ({attr_type})：")
                if not ok or not value.strip():
                    QMessageBox.warning(self, "警告", f"{attr}不能为空！")
                    return
                attribute_values[attr] = value

            # 将属性插入对应的属性表
            query = """
                INSERT INTO {table} (item_id, {fields})
                VALUES (%s, {placeholders})
            """.format(table=type_name,
                       fields=', '.join(attribute_values.keys()),
                       placeholders=', '.join(['%s'] * len(attribute_values))
                       )
            self.db.execute(query, (item_id, *attribute_values.values()))

            QMessageBox.information(self, "信息", "物品和属性添加成功！")

        except Exception as e:
            QMessageBox.critical(self, "错误", f"数据库错误: {e}")

    def view_my_items(self):
        try:
            # 查询所有由当前用户创建的物品
            items = self.db.query(
                "SELECT * FROM items WHERE created_by = %s", (self.user['id'],)
            )

            if not items:
                QMessageBox.information(self, "信息", "您尚未发布物品。")
                return

            # 用于存储按类别分组后的物品数据
            categorized_items = {}

            for item in items:
                type_name_query = self.db.query(
                    "SELECT name FROM item_types WHERE id = %s", (
                        item['type_id'],)
                )
                type_name = type_name_query[0]['name'] if type_name_query else "未知类别"

                attribute_values = self.db.query(
                    f"SELECT * FROM {type_name} WHERE item_id = %s", (item['id'],)
                )

                if attribute_values:
                    attribute_data = attribute_values[0]
                    del attribute_data['item_id']

                    if type_name not in categorized_items:
                        categorized_items[type_name] = {
                            'headers': ['type_name', 'name', 'description', 'address', 'phone', 'email'],
                            'data': []
                        }

                    headers = categorized_items[type_name]['headers']
                    for attr in attribute_data.keys():
                        if attr not in headers and attr != 'id':
                            headers.append(attr)

                    item_data = [
                        type_name,  # Add type_name as the first column
                        item['name'],
                        item['description'],
                        item['address'],
                        item['phone'],
                        item['email']
                    ] + [str(value) for key, value in attribute_data.items() if key != 'id']

                    categorized_items[type_name]['data'].append(item_data)

            dialog = QDialog(self)
            dialog.setWindowTitle("我的物品")
            layout = QVBoxLayout(dialog)
            dialog.resize(1600, 600)

            for type_name, data in categorized_items.items():
                table = QTableWidget(len(data['data']), len(data['headers']))
                table.setHorizontalHeaderLabels(data['headers'])

                for row, item_data in enumerate(data['data']):
                    for col, value in enumerate(item_data):
                        table.setItem(row, col, QTableWidgetItem(value))

                layout.addWidget(table)

            dialog.setLayout(layout)
            close_button = QPushButton("关闭", dialog)
            close_button.clicked.connect(dialog.accept)
            layout.addWidget(close_button)

            dialog.exec_()

        except Exception as e:
            QMessageBox.critical(self, "错误", f"数据库错误: {e}")

    def search_items(self):
        try:
            # 获取物品类型
            item_types = self.db.query("SELECT * FROM item_types")
            if not item_types:
                QMessageBox.warning(self, "警告", "无法加载物品类型！")
                return

            type_names = {item_type['name']
                : item_type for item_type in item_types}
        except Exception as e:
            QMessageBox.critical(self, "错误", f"数据库错误: {e}")
            return

        type_name, ok = QInputDialog.getItem(
            self, "搜索物品", "请选择品类：", list(type_names.keys()), 0, False
        )
        if not ok or type_name not in type_names:
            QMessageBox.warning(self, "警告", "请选择有效的物品类型！")
            return

        keyword, ok = QInputDialog.getText(self, "搜索物品", "请输入关键字：")
        if not ok or not keyword.strip():
            QMessageBox.warning(self, "警告", "关键字不能为空！")
            return

        type_id = type_names[type_name]['id']

        try:
            items = self.db.query(
                """
                SELECT i.*, t.name AS type_name, u.username AS creator_username
                FROM items i
                JOIN item_types t ON i.type_id = t.id
                JOIN users u ON i.created_by = u.id
                WHERE i.type_id = %s AND (i.name LIKE %s OR i.description LIKE %s OR u.username LIKE %s)
                """, (type_id, f"%{keyword}%", f"%{keyword}%", f"%{keyword}%")
            )

            if not items:
                QMessageBox.information(self, "信息", "未找到匹配的物品。")
                return

            all_item_data = []
            headers = ['物品名称', '描述', '物品类型', '地址', '电话', '邮箱', '创建者用户名']

            for item in items:
                type_name = self.db.query(
                    "SELECT name FROM item_types WHERE id = %s", (
                        item['type_id'],)
                )[0]['name']
                attribute_values = self.db.query(
                    f"SELECT * FROM {type_name} WHERE item_id = %s", (
                        item['id'],)
                )
                if attribute_values:
                    attribute_data = attribute_values[0]
                    # 去除 item_id 列
                    del attribute_data['item_id']
                    # 添加属性键到 headers
                    headers.extend(
                        attr for attr in attribute_data.keys() if attr not in headers)
                    # 添加所有值
                    item_data = [
                        item['name'],
                        item['description'],
                        item['type_name'],
                        item['address'],
                        item['phone'],
                        item['email'],
                        item['creator_username']
                    ] + [str(attribute_data.get(attr, '')) for attr in headers[7:]]
                    all_item_data.append(item_data)

            self.search_results_table = QTableWidget(
                len(all_item_data), len(headers))
            self.search_results_table.setHorizontalHeaderLabels(headers)
            self.search_results_table.resize(1600, 600)

            for row, data in enumerate(all_item_data):
                for col, value in enumerate(data):
                    self.search_results_table.setItem(
                        row, col, QTableWidgetItem(value))

            self.search_results_table.show()

        except Exception as e:
            QMessageBox.critical(self, "错误", f"数据库错误: {e}")

    def delete_item(self):
        try:
            # 获取要删除的物品名称
            name, ok = QInputDialog.getText(self, "删除物品", "请输入要删除的物品名称：")
            if not ok or not name.strip():
                QMessageBox.warning(self, "警告", "物品名称不能为空！")
                return

            # 查询该物品是否存在并由当前用户创建
            item = self.db.query(
                "SELECT * FROM items WHERE name = %s AND created_by = %s", (
                    name, self.user['id'])
            )

            if not item:
                QMessageBox.warning(self, "警告", "您没有权限删除该物品或物品不存在！")
                return

            # 获取该物品的ID和类型ID
            item_id = item[0]['id']
            type_id = item[0]['type_id']

            # 确认删除
            reply = QMessageBox.question(self, "确认删除", f"您确定要删除物品 '{name}' 吗？",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                return

            # 根据物品类型删除对应的属性表中的数据
            type_name_query = self.db.query(
                "SELECT name FROM item_types WHERE id = %s", (type_id,))
            if not type_name_query:
                QMessageBox.warning(self, "警告", "物品类型不存在！")
                return

            type_name = type_name_query[0]['name']

            # 删除物品属性表中的数据
            self.db.execute(
                f"DELETE FROM {type_name} WHERE item_id = {item_id}")

            # 删除物品记录
            self.db.execute("DELETE FROM items WHERE id = %s", (item_id,))

            QMessageBox.information(self, "成功", "物品已成功删除！")

        except Exception as e:
            QMessageBox.critical(self, "错误", f"数据库错误: {e}")

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
