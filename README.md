# 🎮 Tic-Tac-Toe vs AI

<p align="center">
  <strong>Pythonis loodud Tic-Tac-Toe mäng tehisintellektiga</strong>
</p>

<p align="center">
  Tkinter · Minimax · Alpha-Beta Pruning · Heuristiline hindamine
</p>

---

## 🖥️ Rakenduse vaade

<p align="center">
  <img src="images/screenshot.png" alt="Tic-Tac-Toe vs AI" width="700">
</p>

<p align="center">
  <em>Tic-Tac-Toe mängu kasutajaliides AI vastase, raskusastmete, skoori ja võiduvõimaluse näiduga.</em>
</p>

---

## 📌 Projekti kirjeldus

Projekt on Pythonis loodud **Tic-Tac-Toe mäng**, kus mängija saab mängida
tehisintellekti vastu.

Rakendus sisaldab:

- 🤖 AI vastast
- 🎚️ kolme raskusastet
- 📊 võidu-/viigi-/kaotuste statistikat
- 📈 hinnangulist võiduvõimalust
- 💾 mängude ajaloo salvestamist
- 🧠 AI mälukasutuse näitu
- 🕹️ 3×3, 4×4 ja 5×5 mängulaudu

---

# 1. Prompt-põhine arenduskäik

| # | Prompt / ülesanne | Tehtud muudatus |
|---|---|---|
| **1** | Genereeri Python Tic-Tac-Toe, vastaseks AI, eraldi aken, võiduprotsent + skooriala | Lõin `tic_tac_toe.py` – Tkinteri GUI, minimax-põhine AI, kolm raskusastet erineva juhuslikkuse määraga, võidu/kaotuse tulemus koos protsendiribaga ning skoor (võidud/viigid/kaotused). |
| **2** | Lisa AI mälukasutus MB-des + salvesta mängutulemused | Lisasin `get_memory_mb()` funktsiooni, mis kasutab Pythoni `resource`-moodulit ja mõõdab protsessi tipp-RSS-i. Mängutulemused salvestatakse `game_history.json` faili. |
| **3** | Näita koodifaili | Kuvati kogu `tic_tac_toe.py` sisu koos programmi struktuuri selgitusega. |
| **4** | Kuhu andmed salvestatakse? | Selgitati andmefailide asukohta ning näidati nende hetkesisu. |
| **5** | Kerge = 3×3, Keskmine = 4×4, Raske = 5×5 | Mänguloogika muudeti üldistatuks. `generate_lines()` genereerib võiduread dünaamiliselt vastavalt laua suurusele ja võidupikkusele. |
| **6** | Näita iga käigu järel oma võiduvõimalust | Lisasin `win_probability_pct()` funktsiooni, mis kasutab rea-põhist heuristikat ja teisendab tulemuse sigmoidfunktsiooni abil 2–98% vahemikku. |

---

# 2. 🧠 Tehniline arhitektuur

## Algoritm

AI kasutab:

**Minimax + Alpha-Beta Pruning**

Põhiline otsinguloogika asub failis:

```text
tic_tac_toe.py
```

ligikaudu ridadel `96–135`.

### Raskusastmed

| Raskusaste | Laud | Otsingusügavus | Meetod |
|---|---:|---:|---|
| 🟢 **Kerge** | 3×3 | 9 | Täielik minimax |
| 🟡 **Keskmine** | 4×4 | 5 | Minimax + alpha-beta + heuristika |
| 🔴 **Raske** | 5×5 | 4 | Minimax + alpha-beta + heuristika |

### 🟢 Kerge – 3×3

3×3 mängus kasutatakse täielikku minimax-otsingut.

See tähendab, et AI uurib kogu mängupuud ning saab seetõttu
mängida matemaatiliselt täiuslikult.

### 🟡 Keskmine – 4×4

4×4 laua puhul kasutatakse:

- piiratud otsingusügavust
- minimax-algoritmi
- alpha-beta kärpimist
- heuristilist hindamist

### 🔴 Raske – 5×5

5×5 laua puhul kasutatakse samuti piiratud otsingut,
kuid otsinguruum on suurem ja ühe käigu arvutamine nõuab rohkem tööd.

Täieliku mängupuu läbimine oleks suuremate laudade puhul liiga aeglane.

---

## 🔄 Dünaamiliselt genereeritud võiduread

Võiduread ei ole programmi sisse kõvakodeeritud.

Funktsioon:

```python
generate_lines()
```

genereerib vajalikud võiduread dünaamiliselt vastavalt:

- laua suurusele
- võiduks vajalike märkide arvule
- horisontaalsetele ridadele
- vertikaalsetele ridadele
- diagonaalidele

Võiduread salvestatakse `@lru_cache` abil vahemällu, et samu
kombinatsioone ei peaks uuesti arvutama.

---

# 3. 📊 Ressursianalüüs

AI jõudluse hindamiseks jooksutati:

> **8 simuleeritud mängu iga raskusastme kohta**

AI mängis päris otsingualgoritmi järgi ning vastasena kasutati juhuslikku käijat.

## Tulemused

| Raskusaste | Laud | Sügavus | Sõlmi / käik | Aeg / käik | AI arvutusaeg / mäng | Mängu pikkus |
|---|---:|---:|---:|---:|---:|---:|
| 🟢 Kerge | 3×3 | 9 | ~1 220 | ~2,1 ms | ~7 ms | ~7 käiku |
| 🟡 Keskmine | 4×4 | 5 | ~6 630 | ~17 ms | ~96 ms | ~11 käiku |
| 🔴 Raske | 5×5 | 4 | ~15 270 | ~81 ms | ~374 ms | ~9 käiku |

---

# 4. 💾 Mälukasutus

Protsessi tipp-RSS enne ja pärast 24 täismängu simulatsiooni oli:

<div align="center">

### ~25,2 MB

**Mälu muutus: 0,00 MB**

</div>

See näitab, et rakenduse kuvatav **AI mälukasutus** peegeldab
peamiselt Pythoni ja Tkinteri baastarbimist, mitte AI algoritmi
suurt lisamälukasutust.

Minimax muudab mängulauda kohapeal (`in-place`) ega jäta iga
otsingusammu järel suuri andmestruktuure mällu.

Võiduread on `lru_cache` abil vahemällu salvestatud ja neid
taaskasutatakse.

---

# 5. 📈 Võiduvõimaluse arvutamine

Funktsioon:

```python
win_probability_pct()
```

hindab mängija hetkeseisu pärast iga käiku.

Arvutus kasutab sama rea-põhist heuristikat, mida kasutatakse
AI otsingus.

Tulemus teisendatakse sigmoidfunktsiooni abil vahemikku:

```text
2% – 98%
```

Mängu lõppedes kuvatakse täpsed väärtused:

```text
100% → võit
50%  → viik
0%   → kaotus
```

Võiduvõimalus kuvatakse rakenduses:

- protsendina
- visuaalse ribana
- pärast iga käiku uueneva väärtusena

---

# 6. 🗂️ Andmete salvestamine

Mängude ajalugu salvestatakse faili:

```text
game_history.json
```

Iga mängu kohta salvestatakse näiteks:

```text
- mängu aeg
- tulemus
- raskusaste
```

Skoor arvutatakse mänguajaloost.

---

# 7. ⚙️ Kasutatud tehnoloogiad

| Tehnoloogia | Kasutus |
|---|---|
| 🐍 **Python** | Põhiprogrammeerimiskeel |
| 🖼️ **Tkinter** | Graafiline kasutajaliides |
| 🧠 **Minimax** | AI otsingualgoritm |
| ✂️ **Alpha-Beta Pruning** | Otsingu optimeerimine |
| 📐 **Heuristika** | Suuremate mängulaudade hindamine |
| 💾 **JSON** | Mänguajaloo salvestamine |
| 🧮 **`resource`** | Protsessi mälukasutuse mõõtmine |
| ⚡ **`lru_cache`** | Võiduridade vahemällu salvestamine |

---

# 8. 📋 Kokkuvõte

> **See AI on eelkõige arvutuslikult, mitte mälu poolest kulukas.**

Raske 5×5 tase teeb ühe käigu kohta ligikaudu **12× rohkem tööd**
kui Kerge 3×3 tase, kuid protsessi mälukasutus püsib praktiliselt
muutumatuna kogu mängu vältel.

Suuremate laudade puhul võimaldavad:

- piiratud otsingusügavus
- alpha-beta kärpimine
- heuristiline hindamisfunktsioon
- võiduridade vahemällu salvestamine

hoida AI arvutusaja mõistlikuna.

---

## 🎮 Projekti põhiidee

```text
Mängija
   │
   ▼
Tkinter GUI
   │
   ├── 3×3 / 4×4 / 5×5 mängulaud
   │
   ├── Skoor ja mänguajalugu
   │
   ├── Võiduvõimaluse hinnang
   │
   ▼
AI
   │
   ├── Minimax
   ├── Alpha-Beta Pruning
   ├── Heuristiline hindamine
   └── LRU Cache
```

---

<p align="center">
  <strong>🎮 Tic-Tac-Toe vs AI</strong><br>
  Python · Tkinter · Minimax · Alpha-Beta Pruning
</p>
