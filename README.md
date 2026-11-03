# IT Asset Manager

## Hallgatói adatok

- Név: Gubis Zsombor Dániel
- Neptun-kód: O5JM7I

## A feladat leírása

Az **IT Asset Manager** egy Pythonban készült, grafikus felületű asztali
alkalmazás, amely egy vállalat számítógépeinek nyilvántartását segíti:
a gépek felvételét és listázását, a felhasználókhoz rendelést (kiadás és
visszavétel), valamint a selejtezett gépek jegyzőkönyv-listáját.

Az adatok helyi SQLite adatbázisban tárolódnak.

## Felhasználói útmutató

### Mit kell telepíteni

- **Python 3.12** vagy újabb stabil Python 3 verzió.
- A grafikus felülethez a **Tkinter** csomag:

```powershell
python -m pip install tkinter
```

Az SQLite, a `logging`, a `datetime` és a `pathlib` a Python standard
könyvtárának része, azokat nem kell telepíteni.

### A program indítása

A projektmappában:

```powershell
python main.py
```

## A program felépítése

### Fájlok

- `main.py` – a program belépési pontja, innen indítható.
- `GZ_modul.py` – saját modul (monogram: GZ).
- `README.md` – ez a dokumentáció.

### Felhasznált modulok

- `customtkinter` (külső) – grafikus felület
- `tkinter` (beépített, a CustomTkinteren keresztül)
- `sqlite3` (beépített) – adattárolás
- `logging` (beépített) – naplózás
- `datetime` (beépített) – dátumok
- `pathlib` (beépített) – fájlútvonalak

### Osztályok és függvények
