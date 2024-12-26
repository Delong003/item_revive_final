import mysql.connector


class Database:
    def __init__(self):
        try:
            self.conn = mysql.connector.connect(
                host="localhost",  # 修改为您的数据库主机
                user="root",  # 修改为数据库用户名
                password="Delong666",  # 修改为用户密码
                database="revive_system"  # 修改为数据库名称
            )
            self.cursor = self.conn.cursor(dictionary=True)
            print("数据库已经成功连接！")
        except mysql.connector.Error as err:
            print(f"数据库连接错误: {err}")
            self.cursor = None  # 在连接失败时设置为 None
            self.conn = None  # 数据库连接也设置为 None

    def query(self, query, params=None):
        if self.cursor is None:
            raise Exception("数据库未正确连接。")
        self.cursor.execute(query, params or ())
        return self.cursor.fetchall()

    def execute(self, query, params=None):
        if self.cursor is None:
            raise Exception("数据库未正确连接。")
        self.cursor.execute(query, params or ())
        self.conn.commit()

    def __del__(self):
        if self.cursor is not None:  # 确保 cursor 存在后再关闭
            self.cursor.close()
        if self.conn is not None:  # 确保 conn 存在后再关闭
            self.conn.close()
