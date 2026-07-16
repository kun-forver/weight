"""Seed script: populates the database with ~130 common Chinese foods, dishes, and fast foods.

Run via: python -m app.seed.foods
"""

import urllib.request
import json
from app.database import SessionLocal
from app.models.food import Food


# Expanded Chinese foods across categories, popular dishes, and chain restaurants
# Format: (name, category, calories per 100g, protein, carbs, fat)
FOODS_DATA = [
    # --- 主食 (Staples) ---
    ("白米饭", "主食", 116, 2.6, 25.9, 0.3),
    ("糙米饭", "主食", 111, 2.6, 22.9, 0.9),
    ("白粥", "主食", 30, 0.7, 6.5, 0.1),
    ("小米粥", "主食", 46, 1.4, 8.4, 0.7),
    ("全麦面包", "主食", 247, 8.5, 44.2, 3.5),
    ("白面包", "主食", 265, 9.0, 49.6, 3.2),
    ("馒头", "主食", 223, 7.0, 47.0, 1.1),
    ("花卷", "主食", 217, 6.3, 45.0, 1.0),
    ("包子(猪肉)", "主食", 227, 8.4, 37.0, 4.8),
    ("包子(素菜)", "主食", 160, 5.0, 31.0, 2.0),
    ("饺子(猪肉)", "主食", 240, 9.0, 28.0, 10.0),
    ("饺子(三鲜)", "主食", 195, 8.2, 26.0, 6.5),
    ("红薯", "主食", 90, 1.5, 21.2, 0.2),
    ("紫薯", "主食", 82, 1.2, 18.5, 0.2),
    ("土豆", "主食", 81, 2.6, 17.8, 0.2),
    ("玉米", "主食", 112, 4.0, 22.8, 1.2),
    ("燕麦片", "主食", 377, 15.0, 61.0, 7.0),
    ("面条(煮)", "主食", 110, 3.5, 22.0, 0.6),
    ("意大利面", "主食", 157, 5.8, 30.7, 0.9),
    ("荞麦面", "主食", 99, 4.4, 21.3, 0.7),
    ("水饺(去汤)", "主食", 210, 8.0, 25.0, 8.0),
    ("南瓜", "主食", 23, 0.7, 5.3, 0.1),

    # --- 肉蛋 (Meat & Eggs) ---
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
    ("生蚝", "肉蛋", 57, 5.0, 4.2, 2.1),
    ("扇贝", "肉蛋", 69, 11.1, 3.2, 0.6),

    # --- 蔬菜 (Vegetables) ---
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
    ("木耳(水发)", "蔬菜", 21, 1.5, 5.8, 0.2),
    ("洋葱", "蔬菜", 40, 1.1, 9.3, 0.1),
    ("金针菇", "蔬菜", 32, 2.4, 6.0, 0.4),
    ("海带", "蔬菜", 15, 0.8, 4.2, 0.1),

    # --- 水果 (Fruits) ---
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
    ("哈密瓜", "水果", 34, 0.5, 7.9, 0.1),
    ("小番茄", "水果", 22, 0.9, 4.8, 0.2),
    ("芒果", "水果", 60, 0.8, 15.0, 0.4),
    ("牛油果", "水果", 160, 2.0, 8.5, 14.7),

    # --- 饮品 (Beverages) ---
    ("牛奶(全脂)", "饮品", 61, 3.2, 3.4, 3.5),
    ("牛奶(脱脂)", "饮品", 34, 3.4, 5.0, 0.1),
    ("豆浆(无糖)", "饮品", 30, 3.0, 1.2, 1.6),
    ("酸奶(无糖)", "饮品", 72, 2.5, 9.3, 2.7),
    ("酸奶(加糖)", "饮品", 72, 2.6, 16.0, 2.7),
    ("黑咖啡", "饮品", 2, 0.3, 0.0, 0.0),
    ("绿茶(无糖)", "饮品", 1, 0.1, 0.0, 0.0),
    ("椰子水", "饮品", 46, 1.7, 10.5, 0.2),
    ("无糖气泡水", "饮品", 0, 0.0, 0.0, 0.0),
    ("零度可乐", "饮品", 0, 0.0, 0.0, 0.0),
    ("可口可乐(经典)", "饮品", 43, 0.0, 10.6, 0.0),
    ("无糖豆浆", "饮品", 31, 3.0, 1.5, 1.5),

    # --- 家常菜 (Chinese Dishes) ---
    ("西红柿炒鸡蛋", "蔬菜", 98, 4.2, 5.0, 7.1),
    ("宫保鸡丁", "肉蛋", 165, 12.0, 7.5, 9.8),
    ("鱼香肉丝", "肉蛋", 185, 10.5, 8.2, 12.5),
    ("麻婆豆腐", "肉蛋", 125, 6.8, 4.5, 9.0),
    ("红烧肉", "肉蛋", 420, 12.5, 6.0, 38.5),
    ("蒜蓉西兰花", "蔬菜", 58, 2.5, 4.5, 3.6),
    ("清蒸鱼", "肉蛋", 95, 15.0, 1.2, 3.5),
    ("青椒炒肉丝", "肉蛋", 145, 9.5, 4.8, 10.2),
    ("酸辣土豆丝", "蔬菜", 95, 1.5, 16.0, 3.0),
    ("地三鲜", "蔬菜", 135, 1.8, 18.0, 6.5),
    ("小炒黄牛肉", "肉蛋", 160, 18.5, 2.5, 8.5),
    ("清炒时蔬", "蔬菜", 45, 1.2, 3.5, 3.0),
    ("番茄牛肉汤", "肉蛋", 65, 5.5, 2.8, 3.2),
    ("回锅肉", "肉蛋", 350, 11.2, 4.5, 32.0),
    ("家常豆腐", "蔬菜", 115, 6.5, 5.0, 7.5),
    ("酸菜鱼", "肉蛋", 110, 12.8, 2.5, 5.5),

    # --- 连锁快餐餐饮 (Fast Foods & Chains) ---
    ("板烧鸡腿堡(麦当劳)", "主食", 230, 16.8, 24.3, 7.3),
    ("双层吉士汉堡(麦当劳)", "主食", 265, 19.5, 25.0, 11.5),
    ("麦辣鸡腿堡(麦当劳)", "主食", 280, 15.0, 32.0, 12.0),
    ("薯条中包(麦当劳)", "零食", 310, 3.4, 40.5, 15.0),
    ("麦乐鸡5块(麦当劳)", "肉蛋", 270, 14.5, 16.0, 15.0),
    ("香辣鸡腿堡(肯德基)", "主食", 290, 14.5, 35.0, 11.8),
    ("新奥尔良烤翅2只(肯德基)", "肉蛋", 210, 15.2, 2.0, 16.0),
    ("葡式蛋挞1个(肯德基)", "零食", 330, 5.0, 38.0, 18.0),
    ("美式咖啡(星巴克)", "饮品", 2, 0.2, 0.3, 0.0),
    ("拿铁大杯(星巴克)", "饮品", 42, 2.8, 3.8, 1.8),
    ("焦糖玛奇朵大杯(星巴克)", "饮品", 68, 2.5, 10.5, 1.8),
    ("无糖燕麦拿铁", "饮品", 35, 1.2, 4.5, 1.5),
    ("珍珠奶茶(标准糖)", "饮品", 85, 0.8, 15.0, 2.5),
    ("珍珠奶茶(微糖)", "饮品", 55, 0.8, 9.0, 1.8),
    ("柠檬水(微糖)", "饮品", 15, 0.1, 3.8, 0.0),

    # --- 零食 (Snacks) ---
    ("黑巧克力(70%)", "零食", 598, 7.8, 45.0, 43.0),
    ("蛋白棒", "零食", 340, 30.0, 30.0, 12.0),
    ("全麦饼干", "零食", 420, 10.0, 68.0, 12.0),
    ("海苔", "零食", 177, 26.7, 22.0, 1.0),
    ("果干(混合)", "零食", 320, 3.0, 76.0, 0.5),
    ("魔芋爽", "零食", 60, 1.0, 13.0, 0.5),
    ("薯片", "零食", 536, 5.0, 52.0, 34.0),
    ("话梅", "零食", 200, 1.0, 50.0, 0.0),
    ("苏打饼干", "零食", 430, 8.5, 68.0, 13.5),

    # --- 坚架 (Nuts) ---
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
    """Seed the foods table incrementally so existing DB isn't wiped and new foods are added."""
    db = SessionLocal()
    try:
        inserted_count = 0
        for name, category, calories, protein, carbs, fat in FOODS_DATA:
            existing = db.query(Food).filter(Food.name == name, Food.is_custom == False).first()
            if not existing:
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
                db.add(food)
                inserted_count += 1

        if inserted_count > 0:
            db.commit()
            print(f"Successfully seeded {inserted_count} new common Chinese foods/dishes.")
        else:
            print("All default Chinese foods are already present in the database.")

        # Call GitHub crawler for expanded datasets
        try:
            crawl_and_seed_from_github(db)
        except Exception as e:
            print(f"[Seed Warning] GitHub crawler failed: {e}")

    except Exception as e:
        db.rollback()
        print(f"Error seeding foods: {e}")
        raise
    finally:
        db.close()


def clean_float(val) -> float:
    if val is None:
        return 0.0
    if not isinstance(val, str):
        try:
            return float(val)
        except Exception:
            return 0.0
    val = val.strip().replace("克", "").replace("千卡", "")
    if val in ("—", "Tr", "tr", "N/A", "n/a", "trace", "Trace", "", "-"):
        return 0.0
    try:
        return float(val)
    except ValueError:
        return 0.0


def clean_int(val) -> int:
    if val is None:
        return 0
    if not isinstance(val, str):
        try:
            return int(float(val))
        except Exception:
            return 0
    val = val.strip().replace("千卡", "")
    if val in ("—", "Tr", "tr", "N/A", "n/a", "trace", "Trace", "", "-"):
        return 0
    try:
        return int(float(val))
    except ValueError:
        return 0


def map_category(filename: str) -> str:
    name = filename.replace("merged_", "").split("-")[0]
    mapping = {
        "乳类及其制品": "乳制品",
        "干豆类及其制品": "豆类及制品",
        "蔬菜类及其制品": "蔬菜类",
        "蔬菜及其制品": "蔬菜类",
        "水果类及其制品": "水果类",
        "水果及其制品": "水果类",
        "畜肉类及其制品": "肉类",
        "禽肉类及其制品": "肉类",
        "水产类及其制品": "水产类",
        "蛋类及其制品": "蛋制品",
        "谷类及其制品": "谷物主食",
        "坚果种子类": "坚果类",
        "其他类": "其他"
    }
    for k, v in mapping.items():
        if k in name:
            return v
    return "其他"


def fetch_json(url: str):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


def crawl_and_seed_from_github(db) -> None:
    """Download digitized China Food Composition data from GitHub and import incrementally."""
    print("Fetching China Food Composition data from GitHub...")
    url = "https://api.github.com/repos/Sanotsu/china-food-composition-data/contents/json_data_vision_251206_Qwen2-5-VL-72B-Instruct"
    try:
        files = fetch_json(url)
    except Exception as e:
        print(f"[Seed Warning] Could not reach GitHub API for food list: {e}")
        return

    json_files = [f for f in files if f.get("name", "").endswith(".json")]
    
    # Filter to main category groups
    target_categories = [
        "乳类", "干豆", "蔬菜", "水果", "畜肉", "禽肉", "水产", "蛋类", "谷类", "坚果", "小吃", "速食"
    ]
    
    filtered_files = []
    for jf in json_files:
        name = jf["name"]
        if any(tc in name for tc in target_categories):
            filtered_files.append(jf)

    # Limit to first 12 categories to keep startup latency reasonable while importing hundreds of foods
    selected_files = filtered_files[:12]
    
    total_inserted = 0
    for jf in selected_files:
        file_name = jf["name"]
        download_url = jf["download_url"]
        category = map_category(file_name)
        
        try:
            food_list = fetch_json(download_url)
            inserted_in_file = 0
            for item in food_list:
                food_name = item.get("foodName")
                if not food_name:
                    continue
                food_name = food_name.strip()
                if food_name.startswith("*"):
                    food_name = food_name.lstrip("*").strip()
                
                # Check duplication
                existing = db.query(Food).filter(Food.name == food_name).first()
                if existing:
                    continue
                
                calories = clean_int(item.get("energyKCal", "0"))
                protein = clean_float(item.get("protein", "0"))
                fat = clean_float(item.get("fat", "0"))
                carbs = clean_float(item.get("CHO", "0"))
                
                if calories == 0 and protein == 0 and fat == 0 and carbs == 0:
                    continue
                
                food = Food(
                    name=food_name,
                    category=category,
                    calories=calories,
                    protein=protein,
                    carbs=carbs,
                    fat=fat,
                    is_custom=False,
                    creator_id=None
                )
                db.add(food)
                inserted_in_file += 1
                total_inserted += 1
            
            db.commit()
            if inserted_in_file > 0:
                print(f"Imported {inserted_in_file} items from {file_name}")
        except Exception as e:
            print(f"[Seed Warning] Failed to import from {file_name}: {e}")
            continue

    if total_inserted > 0:
        print(f"Successfully crawled and imported {total_inserted} new foods from GitHub.")


if __name__ == "__main__":
    main()

