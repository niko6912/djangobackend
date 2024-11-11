# utils/export.py

import os
import json
import pandas as pd
from pathlib import Path
from django.conf import settings
from datetime import datetime
from django.db.models import Model, QuerySet
from typing import Union, List, Dict

# Directories for exports
EXCEL_EXPORT_DIR = Path(settings.BASE_DIR) / "exports/excel/investorsv1"
JSON_EXPORT_DIR = Path(settings.BASE_DIR) / "exports/json/investorsv1"
EXCEL_EXPORT_DIR.mkdir(parents=True, exist_ok=True)
JSON_EXPORT_DIR.mkdir(parents=True, exist_ok=True)


def export_to_json(queryset: Union[QuerySet, List[Model]], filename: str) -> str:
    """
    Exports model data to JSON format.
    """
    data = [serialize_investor(obj) for obj in queryset]
    file_path = JSON_EXPORT_DIR / f"{filename}.json"
    with open(file_path, "w") as json_file:
        json.dump(data, json_file, indent=4, default=str)
    return str(file_path)


def export_to_excel(queryset: Union[QuerySet, List[Model]], filename: str) -> str:
    """
    Exports model data to Excel format.
    """
    data = [serialize_investor(obj) for obj in queryset]
    df = pd.DataFrame(data)
    file_path = EXCEL_EXPORT_DIR / f"{filename}.xlsx"
    df.to_excel(file_path, index=False)
    return str(file_path)


def serialize_investor(obj: Model) -> Dict:
    """
    Serializes InvestorProfile model instance to a dictionary with specific handling.
    """
    return {
        "id": str(obj.id),
        "index": obj.index,
        "name": obj.name,
        "surname": obj.surname,
        "phone": f"{obj.phone_prefix} {obj.phone_number}",
        "email": obj.email,
        "amount_lost": obj.amount_lost,
        "agree_to_be_called": obj.agree_to_be_called,
        "created_at": (
            obj.created_at.strftime("%Y-%m-%d %H:%M:%S") if obj.created_at else None
        ),
        "updated_at": (
            obj.updated_at.strftime("%Y-%m-%d %H:%M:%S") if obj.updated_at else None
        ),
        "deleted_at": (
            obj.deleted_at.strftime("%Y-%m-%d %H:%M:%S") if obj.deleted_at else None
        ),
    }
