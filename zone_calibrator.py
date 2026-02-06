import cv2
import numpy as np
from pdf2image import convert_from_path
import json
import os

# ================= CONFIG =================
DOWNLOAD_FOLDER = "downloads"
ZONES_DIR = "zones"
ZONES_FILE = os.path.join(ZONES_DIR, "single_page.json")
DPI = 300
WINDOW_NAME = "Zone Calibrator - Decedent Domicile"

os.makedirs(ZONES_DIR, exist_ok=True)

# ================= SELECT PDF =================
pdfs = [f for f in os.listdir(DOWNLOAD_FOLDER) if f.lower().endswith(".pdf")]
if not pdfs:
    raise FileNotFoundError("No PDFs found in downloads/")

print("Select PDF to map:")
for i, p in enumerate(pdfs):
    print(f"[{i}] {p}")

choice = int(input("Enter number: "))
PDF_FILE = os.path.join(DOWNLOAD_FOLDER, pdfs[choice])

# ================= LOAD PAGE 1 =================
pages = convert_from_path(PDF_FILE, dpi=DPI)
page1 = cv2.cvtColor(np.array(pages[0]), cv2.COLOR_RGB2BGR)

display = page1.copy()
start = None
drawing = False
zones = {}

# ================= MOUSE =================
def mouse(event, x, y, flags, param):
    global start, drawing, display, zones

    if event == cv2.EVENT_LBUTTONDOWN:
        start = (x, y)
        drawing = True

    elif event == cv2.EVENT_MOUSEMOVE and drawing:
        temp = page1.copy()
        cv2.rectangle(temp, start, (x, y), (0, 255, 0), 2)
        display = temp

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        x1, y1 = start
        x2, y2 = x, y

        zones["decedent_domicile"] = [x1, y1, x2, y2]

        with open(ZONES_FILE, "w") as f:
            json.dump(zones, f, indent=2)

        cv2.rectangle(display, (x1, y1), (x2, y2), (0, 255, 0), 2)
        print(f"✅ Decedent domicile saved: {x1, y1, x2, y2}")

# ================= UI =================
cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
cv2.resizeWindow(WINDOW_NAME, 1400, 900)
cv2.setMouseCallback(WINDOW_NAME, mouse)

print("🖱️ Draw ONE BOX around DECEDENT DOMICILE")
print("❌ Press Q to quit")

while True:
    cv2.imshow(WINDOW_NAME, display)
    if cv2.waitKey(20) & 0xFF == ord("q"):
        break

cv2.destroyAllWindows()
print(f"✅ Zone saved to {ZONES_FILE}")
