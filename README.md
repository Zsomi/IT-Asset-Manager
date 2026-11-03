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

- **Python 3.12** vagy újabb stabil Python 3 verzió – ennél több nem kell.

Minden használt könyvtár a Python standard könyvtárának része, külön csomagot
nem kell telepíteni (a `pip install` sem szükséges):

- `tkinter` (és benne `ttk`, `messagebox`) – grafikus felület
- `sqlite3` – adattárolás
- `logging` – naplózás
- `datetime` – dátumok
- `pathlib` – fájlútvonalak

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

- `tkinter` (beépített) – grafikus felület
- `sqlite3` (beépített) – adattárolás
- `logging` (beépített) – naplózás
- `datetime`, `pathlib` (beépített) – dátumok, fájlútvonalak

### Osztályok és függvények

#### `GZ_modul.py` – az adatréteg

**Modul szintű segédfüggvények:**

| Függvény | Feladat |
|---|---|
| `GZ_validate_date(date_str)` | Megvizsgálja, hogy a kapott szöveg érvényes dátum-e (`YYYY-MM-DD` ISO formátum). |
| `GZ_log_message(message, level="info")` | Üzenet naplózása az `asset_manager.log` fájlba a megadott szinttel (debug, info, warning, error, critical). |
| `GZ_today()` | A mai dátumot adja vissza ISO formátumban. |
| `open_connection(file_path=None)` | Megnyitja az SQLite kapcsolatot és bekapcsolja az idegen kulcsok (`foreign key`) ellenőrzését. |
| `create_tables(connection)` | Létrehozza a négy táblát (`computers`, `users`, `assignments`, `disposals`), ha még nem léteznek. |
| `next_asset_tag(connection)` | A következő szabad leltári számot adja vissza (`PC-001`, `PC-002`, …). |
| `rows_to_dicts(rows, fields)` | A lekérdezési eredménysorokat szótárlistává alakítja. |

**`GZDataManager` osztály** – az adatbázis-műveletek egységes kezelője. A konstruktor megnyitja a kapcsolatot, és automatikusan létrehozza a táblákat. Főbb metódusai:

| Metódus | Feladat |
|---|---|
| `next_asset_tag()` | Következő leltári szám generálása. |
| `get_computer_by_id(computer_id)` | Egy gép összes adatának lekérése ID alapján. |
| `add_computer(computer)` | Új számítógép felvitele (leltári szám és név kötelező, dátum- és státusz-ellenőrzéssel). |
| `update_computer(computer_id, computer)` | Meglévő gép adatainak módosítása. |
| `list_computers(search="", status="")` | Gépek listázása név/leltári szám kereséssel és státuszszűréssel, ID szerint rendezve. |
| `add_user(user)` | Új felhasználó felvitele (név kötelező). |
| `list_users(search="", department="")` | Felhasználók listázása kereséssel és osztályszűréssel, névsorban rendezve. |
| `get_user_by_id(user_id)` | Egy felhasználó adatainak lekérése ID alapján. |
| `update_user(user_id, user)` | Felhasználó adatainak módosítása. |
| `delete_user(user_id)` | Felhasználó törlése – aktív kiadással rendelkező felhasználót nem enged törölni. |
| `assign_computer(computer_id, user_id, assigned_at=None)` | Gép kiadása felhasználói ID alapján: `assignments` sor jön létre, a gép státusza `Használatban` lesz. |
| `assign_computer_by_name(computer_id, user_name, assigned_at=None)` | Gép kiadása név alapján: ha a felhasználó még nem szerepel az adatbázisban, automatikusan létrehozza. |
| `return_computer(assignment_id, returned_at=None)` | Kiadás visszavétele: a `returned_at` dátum kitöltése, a gép újra `Elérhető` státuszú lesz. |
| `list_assignments(computer_id=None, user_id=None, active_only=False)` | Kiadások listázása; `active_only=True` esetén csak a még vissza nem vett (aktív) kiadások. |
| `get_assignment_by_id(assignment_id)` | Egy kiadás sor adatainak lekérése. |
| `add_disposal(computer_id, disposal_date=None, reason="", notes="")` | Selejtezés rögzítése: `disposals` sor létrehozása, a gép státusza `Selejtezett` lesz (kiadott gépet nem enged selejtezni). |
| `list_disposals(computer_id=None, from_date=None, to_date=None)` | Selejtezések listázása dátumintervallum- és gépszűréssel. |
| `close()` | Az adatbázis-kapcsolat rendezett lezárása. |
| `__enter__()` / `__exit__()` | `with` blokkhasználatot tesz lehetővé: a blokk végén automatikusan zárja a kapcsolatot. |

#### `main.py` – a grafikus felület

**Konstansok:** a téma színpalettája (`BG_PRIMARY`, `BG_SECONDARY`, `ACCENT_COLOR`, a négy státusz színe: `STATUS_AVAILABLE/IN_USE/REPAIR/DISPOSED`, `DANGER_COLOR`), a betűtípusok (`FONT_NORMAL`, `FONT_BOLD`, `FONT_TITLE`), a padding értékek (`PAD_SMALL`, `PAD_MEDIUM`) és az üzenetidőzítés (`STATUS_MSG_DURATION`). A `LIGHT_THEME` konstans `True`/`False` értékkel világos, illetve sötét témát vált.

| Osztály | Feladat |
|---|---|
| `CustomCombobox(tk.Frame)` | Saját kinézetű lenyíló lista (beviteli mező + „▼" gomb). A lista egy keret nélküli `Toplevel` ablakban jelenik meg a mező alatt; gépelésre részszűrő lista nyílik. Ha az ablakot mozgatják vagy átméretezik, a lista az ablakkal együtt követi az anchort. Kiválasztáskor meghívható `on_select` visszahívást is támogat. |
| `CustomButton(tk.Button)` | Saját stílusú gomb: `is_primary=True` kék kiemelt, `is_danger=True` piros veszélyes, egyéb esetben semleges gomb; hover- és aktívállapot-kezeléssel. |
| `CustomMenuBar(tk.Frame)` | Saját menüsor a natív menü helyett: a menügombra kattintva `Toplevel`-alapú lenyíló menü jelenik meg. A menü az ablakkal együtt mozog, kattintáson kívül és `TclError` esetén bezárul. |
| `StatusBar(tk.Frame)` | Futás közbeni visszajelzés: rövid üzenetek megjelenítése az ablak alján (hiba pirossal), amelyek automatikusan eltűnnek. |
| `GZApp(tk.Tk)` | A főalkalmazás: az ablak, a téma, a menü, a nézetek és a műveleti dialógusok vezérlése. |

**`GZApp` főbb metódusai:**

| Metódus | Feladat |
|---|---|
| `configure_theme()` | ttk stílusok beállítása (táblázat, fejlécek, görgetők) úgy, hogy hover/aktív állapotban se váljon világosra semmi. |
| `create_menu_bar()` | A két menü felépítése: **Számítógépek** (lista, új gép, selejtezések) és **Kiadások** (aktív, összes). |
| `show_computers_view()` | A fő nézet: keresőmező, „Összes" alapértelmezésű státuszszűrő, géptáblázat színes Státusz oszloppal és görgetőkkel, valamint a műveleti gombok (Random adatok, Új számítógép, Szerkesztés, Kiadás, Selejtezés). |
| `generate_random_data(tree)` | 10 véletlenszerű tesztgép felvitele az adatbázisba. |
| `load_computers_table(tree, search, status_filter)` | A táblázat feltöltése ID sorrendben: zebra csíkozás és a sor státusza szerinti színezés (`STATUS_TAGS`). |
| `refresh_computers_view()` | A táblázat újratöltése a jelenlegi szűrőkkel (dialógus bezárása, visszavétel után). |
| `show_add_computer_dialog()` | Új gép felvételi űrlapja (leltári szám és név kötelező, dátumformátum-ellenőrzéssel). |
| `edit_computer(tree)` | A kijelölt gép szerkesztése. |
| `assign_computer_from_table(tree)` / `show_assign_dialog(computer_id)` | Elérhető gép kiadása felhasználónév és dátum megadásával (csak `Elérhető` gépet enged kiadni). |
| `dispose_computer_from_table(tree)` / `show_dispose_dialog(computer_id)` | Elérhető gép selejtezése: ok (kötelező), dátum és megjegyzés megadásával. |
| `show_assignments_view(active_only=False)` | Kiadások táblázata (aktív vagy mind); aktív nézetben **Visszavétel** gomb is helyet kap. |
| `load_assignments_table(tree, active_only)` | Kiadások betöltése a leltári szám és a felhasználónév feloldásával. |
| `return_computer_from_table(tree)` | Kijelölt kiadás visszavétele megerősítés után, majd a táblázat és a géplista frissítése. |
| `clear_placeholder(entry, placeholder)` / `restore_placeholder(entry, placeholder)` | A keresőmezőben és a kiadás dialógusban megjelenő kitöltő (placeholder) szöveg kezelése. |
