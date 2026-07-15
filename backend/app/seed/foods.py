"""Seed script: populates the database with ~80 common Chinese foods.

Run via: python -m app.seed.foods
"""

from app.database import SessionLocal
from app.models.food import Food

# ~80 common Chinese foods across categories
# Format: (name, category, calories per 100g, protein, carbs, fat)
FOODS_DATA = [
    # 主食 (Staples) - 16 items
    ("白米饭", "主食", 116, 2.6, 25.9, 0.3),
    ("糙米饭", "主食", 111, 2.6, 22.9, 0.9),
    ("白粥", "主食", 30, 0.7, 6.5, 0.1),
    ("小米粥", "主食", 46, 1.4, 8.4, 0.7),
    ("全麦面包", "主食", 247, 8.5, 44.2, 3.5),
    ("白面包", "主食", 265, 9.0, 49.6, 3.2),
    ("馒头", "主食", 223, 7.0, 47.0, 1.1),
    ("花卷", "主食", 217, 6.3, 45.0, 1.0),
    ("包子(猪肉)", "主食", 227, 8.4, 37.0, 4.8),
    ("饺子(猪肉)", "主食", 240, 9.0, 28.0, 10.0),
    ("红薯", "主食", 90, 1.5, 21.2, 0.2),
    ("紫薯", "主食", 82, 1.2, 18.5, 0.2),
    ("土豆", "主食", 81, 2.6, 17.8, 0.2),
    ("玉米", "主食", 112, 4.0, 22.8, 1.2),
    ("燕麦片", "主食", 377, 15.0, 61.0, 7.0),
    ("面条(煮)", "主食", 110, 3.5, 22.0, 0.6),

    # 肉蛋 (Meat & Eggs) - 17 items
    ("生鸡胸肉", "肉蛋", 120, 23.0, 0.0, 2.6),
    ("熟鸡胸肉（无油煎/烤/煮）", "肉蛋", 165, 31.0, 0.0, 3.6),
    ("鸡腿(去皮)", "肉蛋", 181, 24.0, 0.0, 9.0),
    ("鸡蛋白", "肉蛋", 60, 11.0, 1.1, 0.2),
    ("鸡蛋(全)", "肉蛋", 144, 13.3, 2.8, 8.8),
    ("瘦猪肉", "肉蛋", 143, 20.3, 1.5, 6.2),
    ("猪里脊", "肉蛋", 155, 20.2, 0.7, 7.9),
    ("瘦牛肉", "肉蛋", 106, 20.2, 1.2, 2.3),
    ("牛腱子", "肉蛋", 125, 30.0, 0.0, 2.0),
    ("羊肉(瘦)", "肉蛋", 118, 20.5, 0.2, 3.9),
    ("鸭肉(去皮)", "肉蛋", 240, 15.5, 0.0, 19.6),
    ("三文鱼", "肉蛋", 208, 20.0, 0.0, 13.0),
    ("鳕鱼", "肉蛋", 82, 17.8, 0.0, 1.0),
    ("虾仁", "肉蛋", 48, 10.4, 0.1, 0.7),
    ("虾(带壳)", "肉蛋", 87, 16.4, 0.0, 2.4),
    ("鲫鱼", "肉蛋", 108, 17.1, 0.0, 4.5),
    ("带鱼", "肉蛋", 127, 17.7, 0.0, 6.2),

    # 蔬菜 (Vegetables) - 16 items
    ("西兰花", "蔬菜", 36, 4.1, 4.3, 0.6),
    ("菠菜", "蔬菜", 28, 2.6, 4.5, 0.3),
    ("生菜", "蔬菜", 16, 1.4, 2.9, 0.4),
    ("白菜", "蔬菜", 20, 1.5, 3.4, 0.1),
    ("芹菜", "蔬菜", 22, 1.2, 4.5, 0.2),
    ("黄瓜", "蔬菜", 16, 0.8, 2.9, 0.2),
    ("西红柿", "蔬菜", 19, 0.9, 4.0, 0.2),
    ("青椒", "蔬菜", 22, 1.0, 5.4, 0.2),
    ("茄子", "蔬菜", 23, 1.1, 4.9, 0.2),
    ("胡萝卜", "蔬菜", 41, 1.0, 10.2, 0.2),
    ("花菜", "蔬菜", 24, 2.1, 4.6, 0.2),
    ("豆芽", "蔬菜", 18, 1.7, 2.9, 0.1),
    ("空心菜", "蔬菜", 20, 2.2, 3.2, 0.3),
    ("芦笋", "蔬菜", 22, 1.4, 4.9, 0.1),
    ("冬瓜", "蔬菜", 12, 0.4, 2.6, 0.2),
    ("蘑菇(鲜)", "蔬菜", 24, 2.7, 4.1, 0.1),

    # 水果 (Fruits) - 12 items
    ("苹果", "水果", 54, 0.3, 13.8, 0.2),
    ("香蕉", "水果", 93, 1.4, 22.8, 0.2),
    ("橙子", "水果", 48, 0.8, 11.1, 0.2),
    ("葡萄", "水果", 44, 0.5, 10.3, 0.2),
    ("草莓", "水果", 32, 0.7, 7.1, 0.2),
    ("西瓜", "水果", 26, 0.6, 6.8, 0.1),
    ("梨", "水果", 51, 0.3, 13.3, 0.2),
    ("猕猴桃", "水果", 61, 0.8, 14.5, 0.6),
    ("柚子", "水果", 42, 0.8, 9.5, 0.2),
    ("蓝莓", "水果", 57, 0.7, 14.5, 0.3),
    ("火龙果", "水果", 60, 1.1, 13.3, 0.2),
    ("桃子", "水果", 51, 0.9, 12.2, 0.1),

    # 饮品 (Beverages) - 8 items
    ("牛奶(全脂)", "饮品", 61, 3.2, 3.4, 3.5),
    ("牛奶(脱脂)", "饮品", 34, 3.4, 5.0, 0.1),
    ("豆浆(无糖)", "饮品", 30, 3.0, 1.2, 1.6),
    ("酸奶(无糖)", "饮品", 72, 2.5, 9.3, 2.7),
    ("酸奶(加糖)", "饮品", 72, 2.6, 16.0, 2.7),
    ("黑咖啡", "饮品", 2, 0.3, 0.0, 0.0),
    ("绿茶(无糖)", "饮品", 1, 0.1, 0.0, 0.0),
    ("椰子水", "饮品", 46, 1.7, 10.5, 0.2),

    # 零食 (Snacks) - 6 items
    ("黑巧克力(70%)", "零食", 598, 7.8, 45.0, 43.0),
    ("蛋白棒", "零食", 340, 30.0, 30.0, 12.0),
    ("全麦饼干", "零食", 420, 10.0, 68.0, 12.0),
    ("海苔", "零食", 177, 26.7, 22.0, 1.0),
    ("果干(混合)", "零食", 320, 3.0, 76.0, 0.5),
    ("魔芋爽", "零食", 60, 1.0, 13.0, 0.5),

    # 坚果 (Nuts) - 8 items
    ("杏仁", "坚果", 579, 21.0, 21.6, 49.9),
    ("核桃", "坚果", 654, 14.9, 19.1, 58.8),
    ("腰果", "坚果", 553, 18.2, 44.8, 30.2),
    ("花生", "坚果", 563, 25.8, 16.1, 44.3),
    ("开心果", "坚果", 562, 20.6, 27.2, 45.3),
    ("夏威夷果", "坚果", 718, 7.9, 30.7, 75.8),
    ("松子", "坚果", 673, 13.7, 13.1, 68.6),
    ("瓜子(葵花籽)", "坚果", 574, 22.6, 22.0, 49.5),
]


def main() -> None:
    """Seed the foods table if it is empty, or incrementally add raw/cooked chicken breasts."""
    db = SessionLocal()
    try:
        existing_count = db.query(Food).filter(Food.is_custom == False).count()
        if existing_count > 0:
            # Check and incrementally add new chicken breast options if missing
            raw_chicken = db.query(Food).filter(Food.name == "生鸡胸肉", Food.is_custom == False).first()
            if not raw_chicken:
                print("Adding '生鸡胸肉' to existing database...")
                db.add(Food(name="生鸡胸肉", category="肉蛋", calories=120, protein=23.0, carbs=0.0, fat=2.6, is_custom=False))
            
            cooked_chicken = db.query(Food).filter(Food.name == "熟鸡胸肉（无油煎/烤/煮）", Food.is_custom == False).first()
            if not cooked_chicken:
                print("Adding '熟鸡胸肉（无油煎/烤/煮）' to existing database...")
                db.add(Food(name="熟鸡胸肉（无油煎/烤/煮）", category="肉蛋", calories=165, protein=31.0, carbs=0.0, fat=3.6, is_custom=False))
            
            db.commit()
            print(f"Foods table already has {existing_count} non-custom foods. Incremental checks complete.")
            return

        foods_to_insert = []
        for name, category, calories, protein, carbs, fat in FOODS_DATA:
            food = Food(
                name=name,
                category=category,
                calories=calories,
                protein=protein,
                carbs=carbs,
                fat=fat,
                is_custom=False,
                creator_id=None,
            )
            foods_to_insert.append(food)

        db.add_all(foods_to_insert)
        db.commit()
        print(f"Successfully seeded {len(foods_to_insert)} common Chinese foods.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding foods: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
