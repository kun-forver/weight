"""清空数据库所有数据（保留表结构），然后重新初始化种子数据。

用法：在服务器上，cd 到 backend 目录，运行：
    python clear_db.py

这会：
1. 清空所有 6 张表的数据
2. 重新导入食物种子数据
3. 重建管理员账号 yoyo / yoyo
"""

from sqlalchemy import text
from app.database import engine, SessionLocal
from app.models import User, Food, FoodLog, WeightLog, Friendship, PKBattle
from app.init_db import init_db


def clear_all_data():
    """按外键依赖顺序清空所有表。"""
    db = SessionLocal()
    try:
        # 禁用外键检查，避免删除顺序问题
        db.execute(text("SET FOREIGN_KEY_CHECKS = 0"))

        tables = [
            "food_logs",
            "weight_logs",
            "friendships",
            "pk_battles",
            "foods",
            "users",
        ]
        for table in tables:
            db.execute(text(f"TRUNCATE TABLE {table}"))
            print(f"  ✅ 清空 {table}")

        db.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
        db.commit()
        print("\n所有表已清空。")
    finally:
        db.close()


if __name__ == "__main__":
    print("⚠️  即将清空数据库 fatloss_pk 的所有数据！")
    confirm = input("确认清空？(输入 yes 继续): ")
    if confirm.strip().lower() != "yes":
        print("已取消。")
        exit(0)

    print("\n正在清空数据...")
    clear_all_data()

    print("\n正在重新初始化（种子数据 + 管理员账号）...")
    init_db()

    print("\n✅ 完成！数据库已重置。")
