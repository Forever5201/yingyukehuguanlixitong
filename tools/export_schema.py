import os
import sqlite3


def export_schema(sqlite_path: str, output_path: str) -> int:
    """导出 SQLite 的表结构到 schema.sql（不包含任何数据）。

    返回导出的对象数量（表/索引/触发器）。
    """
    if not os.path.exists(sqlite_path):
        raise FileNotFoundError(f"SQLite 文件不存在: {sqlite_path}")

    connection = sqlite3.connect(sqlite_path)
    try:
        cursor = connection.cursor()
        rows = cursor.execute(
            """
            SELECT type, name, sql
            FROM sqlite_master
            WHERE type IN ('table','index','trigger')
              AND sql IS NOT NULL
            ORDER BY type, name
            """
        ).fetchall()

        statements = [str(row[2]).strip().rstrip(";") for row in rows if row[2]]

        content_parts = [
            "-- SQLite schema (no data)",
            "PRAGMA foreign_keys=OFF;",
            "BEGIN TRANSACTION;",
        ]

        if statements:
            content_parts.append(";\n".join(statements) + ";")

        content_parts.append("COMMIT;")

        content = "\n".join(content_parts) + "\n"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)

        return len(statements)
    finally:
        connection.close()


if __name__ == "__main__":
    db_path = os.path.join("instance", "database.sqlite")
    out_path = os.path.join("schema.sql")
    count = export_schema(db_path, out_path)
    print(f"WROTE {out_path} with {count} objects")




