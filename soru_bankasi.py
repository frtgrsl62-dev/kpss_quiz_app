import json
import os

DOSYA = "soru_bankasi.json"

def soru_bankasini_yukle():
    if not os.path.exists(DOSYA):
        with open(DOSYA, "w", encoding="utf-8") as f:
            json.dump({}, f, ensure_ascii=False, indent=2)
        return {}

    with open(DOSYA, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            # ⚠️ JSON bozuksa sıfırdan başlat
            return {}
