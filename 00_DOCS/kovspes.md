# Követelményspecifikáció – Jelöltkövető rendszer (ATS) – ADMIN MVP

## 1. Projekt áttekintés

- 1.1 Projekt neve
  - Jelöltkövető rendszer (Applicant Tracking System – ATS)

- 1.2 Projekt célja
  - Egy olyan adminisztrátori felület (ADMIN oldal) kialakítása, amely képes:
    - álláshirdetések megjelenítésére
    - a beérkező önéletrajzok automatikus feldolgozására
    - a pályázatok rendszerezésére, minősítésére és kimutatására
  - A projekt MVP szintű megvalósítása a tantárgyi elvárások teljesítéséhez elegendő

- 1.3 Projekt hatóköre
  - csak az ADMIN oldal készül el
  - ebben jelöltek nem tudnak felhasználói felületen keresztül jelentkezni
  - a mintak önéletrajzok kézileg kerülnek be a feldolgozási folyamatba (uploads mappa)

- 1.4 Háttér és indoklás
  - a rendszer célja az önéletrajzok automatikus vizsgálata a `state-of-the-art` ATS logikák mintájára:
    - tartalmi megfelelőség vizsgálata
    - relevanciaértékelés
    - formai ellenőrzés
    - automatikus kategorizálás

A feldolgozott adatok JSON formában kerülnek mentésre, mivel Python alatt ez egyszerűen, gyorsan feldolgozható.

---
---

## 2. Funkcionális követelmények

- 2.1 Főoldal
  - a főoldal betöltésekor megjelenik:
    - egy rejtett bejelentkezési lehetőség, amely kizárólag adminoknak szól
    - egy snippet blokk, amely az álláshirdetésekhez tartozó követelményeket tartalmazza
    - cél: félrevezetés arra az esetre, ha valaki véletlenül rátalál az admin felületre

- 2.2 Bejelentkezés
  - a rejtett belépési elemre kattintva Bootstrap modal jelenik meg:
    - bejelentkezési azonosítók megadására
    - rejtett „jelszó felfedése” elem jobb oldalt elhelyezve
  - sikeres bejelentkezés után:
    - megjelennek az admin menüpontok

- 2.3 Álláshirdetések kezelése
  - bejelentkezés után:
    - megjelenik az összes meghirdetett állás
    - egy állásra kattintva megjelenik annak teljes szövege

- 2.4 Jelentkezések megtekintése
  - a kezelőfelületen megtekinthetők:
    - az összes álláshirdetésre érkezett jelentkezések
    - az automatikusan osztályozott, értékelt önéletrajzok csoportosítva

---
---

## 3. Automatikus feldolgozási és értékelési logika (ATS motor)

A rendszer a beérkezett önéletrajzokat automatikusan feldolgozza az alábbi lépések szerint:

- 3.1 Önéletrajz áthelyezése és archiválása
  - a rendszer az önéletrajzot áthelyezi a megfelelő mappába:
    - a mappa neve az álláshirdetés azonosítója (ID)
    - ha a mappa nem létezik, automatikusan létrehozza
  - a fájl végére hozzáfűz:
    - dátum + időbélyeg, hogy elkerülje a felülírásokat

- 3.2 Formai ellenőrzés
  - az olvasható formátumú önéletrajzok feldolgozásra kerülnek
  - a PDF formátumú önéletrajzok a „választóvonal fölé” kerülnek, prioritást élvezve
  - a nem PDF, de olvasható fájlok a „választóvonal alá” kerülnek
  - a nem olvasható vagy problémás fájlokat piros X jelöli, és a legaljára kerülnek.

- 3.3 Tartalmi ellenőrzés és szabályok
  - a rendszer a snippet-ben található követelmények alapján ellenőrzi a megfelelést
  - automatikusan elemzi:
    - releváns kulcsszavak meglétét
    - releváns kulcsszavak hiányosságokat
    - pontszámokat és súlyozást

- 3.4 Eredmények mentése és kimutatás
  - minden feldolgozási adat JSON formátumban kerül elmentésre
  - a kimutatások a JSON állományból kerülnek előállításra:
    - relevancia pontszámok
    - megfelelőségek és hiányosságok
    - nem megfelelő jelentkezések száma és listája

---
---

## 4. Nem funkcionális követelmények

- 4.1 Teljesítmény
  - a rendszer gyorsan és zökkenőmentesen jelenítse meg a JSON alapján generált adatokat
  - az önéletrajzok feldolgozása lehetőség szerint valós időben történjen

- 4.2 Biztonság
  - a bejelentkezés legyen védett, a belépési modal ne legyen könnyen feltérképezhető
  - a rejtett bejelentkezési opció javítja a biztonságot

- 4.3 Megbízhatóság
  - a rendszernek biztosítania kell, hogy semmilyen önéletrajz ne íródjon felül
  - hibás vagy sérült fájl esetén megfelelő jelölést kell alkalmazni

- 4.4 Bővíthetőség
  - a JSON alapú adatkezelés lehetővé teszi az ATS motor továbbfejlesztését
  - a projekt skálázható több állásra és nagy mennyiségű jelentkezésre

---
---

## 5. Projektműködés, menedzsment és kockázatok

- 5.1 Fejlesztési módszertan
  - a csapat SCRUM módszertan szerint dolgozik
  - heti megbeszélések:
    - minden hétfőn 20:00
    - Discord (rejtett RTT csatorna)
    - jegyzőkönyvet a csapatvezető készíti

- 5.2 Kockázatok
  - a csapat nagy része korábban még nem dolgozott együtt → összeszokási idő
  - korlátozott projektidő (kb. 2 hónap)
  - technikai ismerethiányok → ATS logika megvalósítása kihívás lehet

- 5.3 Mérföldkövek
  - 2025\. 11. 28. – az MVP bemutatása az egyetemen

---

Készült: 2025\. 09. 27., @dabzse
