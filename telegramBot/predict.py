import joblib
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings("ignore")

# Импорты для десериализации модели
import sklearn
import xgboost
import lightgbm
import catboost

model = joblib.load("stacking_best.pkl")
assert hasattr(model, "predict"), "Загруженный объект не является моделью с методом predict"

# Порядок признаков, на которых обучалась модель (БЕЗ level!)
FEATURE_ORDER = [
    "area", "rooms", "kitchen_area", "levels",
    "floor_ratio", "building_type", "object_type",
    "id_region", "month", "quarter", "season", "day_of_week"
]

def predict_price(area: float, rooms: int, kitchen_area: float,
                  levels: int, floor_ratio: float,
                  building_type: int, object_type: int, id_region: int,
                  month: int, quarter: int, season: int, day_of_week: int) -> float:
    input_data = pd.DataFrame([[
        area, rooms, kitchen_area, levels,
        floor_ratio, building_type, object_type,
        id_region, month, quarter, season, day_of_week
    ]], columns=FEATURE_ORDER)

    raw_pred = model.predict(input_data)[0]
    return np.exp(raw_pred)