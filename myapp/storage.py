from django.core.files.storage import Storage
from django.db import connection

class DatabaseStorage(Storage):
    """
    データベースにファイルを保存するカスタムストレージクラス
    """
    def _save(self, name, content):
        with connection.cursor() as cursor:
            # バイナリデータを取得
            file_data = content.read()

            # SQLでデータを挿入
            cursor.execute(
                """
                INSERT INTO upload_pic (file_name, file_data)
                VALUES (%s, %s)
                """,
                [name, file_data]
            )
        return name

    def _open(self, name, mode='rb'):
        with connection.cursor() as cursor:
            # ファイルを取得
            cursor.execute(
                """
                SELECT file_data FROM upload_pic
                WHERE file_name = %s
                """,
                [name]
            )
            row = cursor.fetchone()
            if row:
                from io import BytesIO
                return BytesIO(row[0])  # バイナリデータを返す
        return None

    def exists(self, name):
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT COUNT(*) FROM upload_pic
                WHERE file_name = %s
                """,
                [name]
            )
            return cursor.fetchone()[0] > 0

    def url(self, name):
        # 必要に応じてURL生成ロジックを実装
        return f"/media/{name}"
