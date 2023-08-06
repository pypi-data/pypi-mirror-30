import pymssql


class MSDBConnect:
    server = None
    port = None
    user = None
    password = None
    database = None
    conn = None

    def connect(self, connection_info):
        if "port" in connection_info:
            self.conn = pymssql.connect(
                server=connection_info["server"],
                port=connection_info["port"],
                user=connection_info["user"],
                password=connection_info["password"],
                database=connection_info["database"])
        else:
            self.conn = pymssql.connect(
                server=connection_info["server"],
                user=connection_info["user"],
                password=connection_info["password"],
                database=connection_info["database"])

    def disconnect(self):
        self.conn.close()

    def execute(self, query):
        cursor = self.conn.cursor()
        cursor.execute(query)
        return cursor.fetchall()
