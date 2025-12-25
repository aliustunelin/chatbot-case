from typing import Dict, List
from pydantic import BaseModel


class KeywordCategory(BaseModel):
    name: str
    description: str
    keywords: List[str]
    max_score: float = 20.0


# Healthy Eating keyword kategorileri
KEYWORD_CATEGORIES: Dict[str, KeywordCategory] = {
    "fruits_vegetables": KeywordCategory(
        name="Fruits & Vegetables",
        description="Daily intake, variety, and nutritional benefits",
        keywords=[
            "fruit", "fruits", "vegetable", "vegetables", "meyve", "sebze",
            "vitamin", "vitamins", "daily intake", "günlük tüketim",
            "apple", "elma", "banana", "muz", "orange", "portakal",
            "broccoli", "brokoli", "spinach", "ıspanak", "carrot", "havuç",
            "salad", "salata", "greens", "yeşillik", "fiber", "lif",
            "antioxidant", "antioksidan", "nutritional", "besin değeri"
        ]
    ),
    "hydration": KeywordCategory(
        name="Hydration",
        description="Importance of drinking enough water throughout the day",
        keywords=[
            "water", "su", "hydration", "hidrasyon", "drink", "içmek",
            "fluid", "sıvı", "daily water", "günlük su",
            "8 glasses", "8 bardak", "dehydration", "susuzluk",
            "thirst", "susama", "liquid", "sıvı tüketimi",
            "hydrated", "water intake", "su tüketimi"
        ]
    ),
    "balanced_meals": KeywordCategory(
        name="Balanced Meals",
        description="Combining proteins, carbs, and fats in proper proportions",
        keywords=[
            "protein", "proteins", "carb", "carbs", "carbohydrate", "karbonhidrat",
            "fat", "fats", "yağ", "balanced", "dengeli", "proportion", "oran",
            "macros", "macronutrients", "makro besin", "meal plan", "öğün planı",
            "portion", "porsiyon", "healthy fats", "sağlıklı yağlar",
            "whole grains", "tam tahıl", "lean protein", "yağsız protein",
            "omega", "complex carbs", "kompleks karbonhidrat"
        ]
    ),
    "processed_foods": KeywordCategory(
        name="Processed Foods",
        description="Awareness of additives, sugar, salt, and unhealthy fats",
        keywords=[
            "processed", "işlenmiş", "additive", "katkı maddesi",
            "sugar", "şeker", "salt", "tuz", "unhealthy fat", "sağlıksız yağ",
            "junk food", "abur cubur", "fast food", "preservative", "koruyucu",
            "artificial", "yapay", "refined", "rafine",
            "trans fat", "trans yağ", "saturated", "doymuş yağ",
            "packaged", "paketli", "label", "etiket", "ingredients", "içindekiler"
        ]
    ),
    "meal_timing": KeywordCategory(
        name="Meal Timing",
        description="Regular eating patterns and avoiding long gaps without food",
        keywords=[
            "meal timing", "öğün zamanı", "breakfast", "kahvaltı",
            "lunch", "öğle yemeği", "dinner", "akşam yemeği",
            "snack", "ara öğün", "regular", "düzenli",
            "schedule", "program", "interval", "aralık",
            "skip meals", "öğün atlamak", "eating pattern", "yeme düzeni",
            "metabolism", "metabolizma", "blood sugar", "kan şekeri",
            "fasting", "açlık", "meal frequency", "öğün sıklığı"
        ]
    )
}


def get_all_keywords() -> List[str]:
    """Tüm kategorilerdeki keyword'leri döndürür"""
    all_keywords = []
    for category in KEYWORD_CATEGORIES.values():
        all_keywords.extend(category.keywords)
    return all_keywords


def get_category_names() -> List[str]:
    """Kategori isimlerini döndürür"""
    return [cat.name for cat in KEYWORD_CATEGORIES.values()]

