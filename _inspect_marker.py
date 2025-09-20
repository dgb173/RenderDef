# -*- coding: utf-8 -*-
from pathlib import Path
text = Path('modules/estudio_scraper.py').read_text(encoding='utf-8')
marker = 'return {"status": "error", "resultado": "N/A (Enfrentamiento no encontrado)"}'
idx = text.index(marker)
print(repr(text[idx:idx+120]))
