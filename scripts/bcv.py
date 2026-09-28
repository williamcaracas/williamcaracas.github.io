"""Lee la tasa oficial publicada en bcv.org.ve (incluida la del próximo día hábil)
y la guarda en data/bcv.json solo si cambió."""
import json, pathlib, datetime
import requests, urllib3
from bs4 import BeautifulSoup

urllib3.disable_warnings()  # el certificado SSL del BCV suele dar problemas
URL = "https://www.bcv.org.ve/"
OUT = pathlib.Path("data/bcv.json")

html = requests.get(URL, verify=False, timeout=40,
                    headers={"User-Agent": "Mozilla/5.0"}).text
soup = BeautifulSoup(html, "html.parser")

def tasa(div_id):
    txt = soup.select_one(f"#{div_id} strong").get_text(strip=True)
    return round(float(txt.replace(".", "").replace(",", ".")), 4)

nuevo = {
    "usd": tasa("dolar"),
    "eur": tasa("euro"),
    # atributo tipo "2026-09-29T00:00:00-04:00" -> "2026-09-29"
    "fechaValor": soup.select_one("span.date-display-single")["content"][:10],
}

viejo = json.loads(OUT.read_text()) if OUT.exists() else {}
if {k: viejo.get(k) for k in nuevo} == nuevo:
    print("Sin cambios", nuevo)
else:
    nuevo["consultado"] = datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z"
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(nuevo, ensure_ascii=False, indent=2))
    print("Actualizado", nuevo)
