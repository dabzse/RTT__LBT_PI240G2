# Fejlesztési beállítások

0. **Fedora GNU/Linux** a rendszerem: + python3.13.x! a parancsok eltérhetnek. nézz utána, ha szükséges...
1. klónozás: mindegy, hogy a legalább 3 módszer közül melyikkel
2. belépsz a klónozott mappába
3. legjobb, ha virtuális környezetet használsz
   1. ezt a virtális környezetet létrehozhatod a: `python -m venv venv` parancssal
4. elindítod a virtuális környezetet: `source venv/bin/activate`
   - windows alatt: `venv\Scripts\activate`
     - cmd-vel: `venv\Scripts\activate.bat`
     - powershell-lel: `venv\Scripts\Activate.ps1`
5. telepíted a szükséges csomagokat: `pip install -r requirements.txt`
6. majd kipróbálod: `python manage.py runserver`
7. böngészőt nyitsz és: `http://127.0.0.1:8000/` vagy `http://localhost:8000/`

## DEBUG

jelenleg a `DEBUF=True` érték lesz beállítva, hiába látod, hogy `DEBUG=False` van a settings.py beállításban. ennek végtelenül egyszerű az oka, csak nézz utána, hogy miért van így, ha érdekel. megtalálod...

ebből kifolyólag, ha élesbe kerül a rendszer és kizárólag csak a szükséges dolgok lesznek benne, akkor több sebből fog vérezni.
azaz a `DEBUG=False` értékkel nem fog működni a rendszer.
mit lehet tenni?

- `python manage.py collectstatic` parancsot kell futtatni, hogy a statikus fájlok legyenek a helyükön
  - `assets` mappát fog létrehozni a rendszer, és a `static` mappát ki kell zárni, mert teljesen feleslegessé válik. ez csak a fejlesztési állapotban kell, akkor nem használja az `assets` mappát... remélem érted, hogy a `static` mappát fel kell venni a `.gitignore`-ra...
  - de most még marad, ez még a fejlesztési ág...

## Ágak

minden "mérföldkő" módosításnál jó lenne új ágat létrehozni, és lehetőleg nem használni a `master` ágat. \
ne felejtsétek el, hogy létezik **`git rebase`** parancs! ezzel több **git conflict** kerülhető el...
