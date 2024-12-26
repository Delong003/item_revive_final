import hashlib
from db import Database


class Auth:
    def __init__(self):
        self.db = Database()

    def register(self, username, password, email, phone, address):
        query = """
            INSERT INTO users (username, password, email, phone, address, is_admin, is_approved) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        try:
            self.db.execute(query, (username, password,
                            email, phone, address, False, False))
            return "注册成功！请等待管理员审核。"
        except Exception as e:
            return f"注册失败：{e}"

    def login(self, username, password):
        query = "SELECT * FROM users WHERE username = %s AND password = %s"
        user = self.db.query(query, (username, password))

        if not user:
            return "用户名或密码错误", None
        user = user[0]
        if not user['is_approved']:
            return "您的账号尚未通过管理员审核。", None
        return "登录成功。", user
