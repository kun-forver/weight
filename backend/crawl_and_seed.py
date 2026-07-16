import os
import sys
import urllib.request
import json
from sqlalchemy.orm import Session

# Add current path to sys.path to enable app module imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models.food import Food

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
    # Example: merged_干豆类及其制品-大豆.json -> 豆类及制品
    # We strip merged_ and extension
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
    with urllib.request.urlopen(req, timeout=15) as response:
        return json.loads(response.read().decode("utf-8"))

def main():
    print("--------------------------------------------------")
    print("开始爬取《中国食物成分表》标准化数字化数据集...")
    print("--------------------------------------------------")
    url = "https://api.github.com/repos/Sanotsu/china-food-composition-data/contents/json_data_vision_251206_Qwen2-5-VL-72B-Instruct"
    try:
        files = fetch_json(url)
    except Exception as e:
        print(f"❌ 无法获取 GitHub 数据仓库目录: {e}")
        print("请检查网络连接或稍后再试。")
        return

    # Filter out JSON files
    json_files = [f for f in files if f.get("name", "").endswith(".json")]
    print(f"✓ 成功获取文件列表，发现 {len(json_files)} 个 JSON 数据文件。")

    # Filter files to target categories to make it relevant and high quality
    target_categories = [
        "乳类", "干豆", "蔬菜", "水果", "畜肉", "禽肉", "水产", "蛋类", "谷类", "坚果", "小吃", "速食"
    ]
    
    filtered_files = []
    for jf in json_files:
        name = jf["name"]
        if any(tc in name for tc in target_categories):
            filtered_files.append(jf)
            
    print(f"✓ 筛选出 {len(filtered_files)} 个相关的常用食材数据分类文件。")

    db = SessionLocal()
    try:
        total_inserted = 0
        total_processed_files = 0

        for idx, jf in enumerate(filtered_files):
            file_name = jf["name"]
            download_url = jf["download_url"]
            category = map_category(file_name)
            
            print(f"\n[{idx+1}/{len(filtered_files)}] 正在下载并导入: {file_name}")
            print(f"  映射分类 -> {category}")
            try:
                food_list = fetch_json(download_url)
            except Exception as e:
                print(f"  ⚠️ 下载文件 {file_name} 失败: {e}")
                continue

            inserted_in_file = 0
            for item in food_list:
                food_name = item.get("foodName")
                if not food_name:
                    continue
                
                food_name = food_name.strip()
                # Clean up names like "* 小麦（整粒煮）" -> "小麦（整粒煮）"
                if food_name.startswith("*"):
                    food_name = food_name.lstrip("*").strip()
                
                # Check if it already exists in our database
                existing = db.query(Food).filter(Food.name == food_name).first()
                if existing:
                    continue
                
                # Parse nutrients per 100g
                calories = clean_int(item.get("energyKCal", "0"))
                protein = clean_float(item.get("protein", "0"))
                fat = clean_float(item.get("fat", "0"))
                carbs = clean_float(item.get("CHO", "0"))
                
                # Ignore items that have 0 nutritional values
                if calories == 0 and protein == 0 and fat == 0 and carbs == 0:
                    continue
                
                # Create the food instance
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
            total_processed_files += 1
            print(f"  ✓ 成功从该文件导入 {inserted_in_file} 条新食物数据")

        print("--------------------------------------------------")
        print(f"🎉 爬取与增量导入完成！")
        print(f"  成功处理文件: {total_processed_files}/{len(filtered_files)}")
        print(f"  新增导入食物数: {total_inserted} 条")
        print("--------------------------------------------------")

    except Exception as e:
        print(f"❌ 运行中出现未预料的错误: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
