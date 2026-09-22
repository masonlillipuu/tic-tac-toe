1. Prompt-põhine arenduskäik
#	Sinu prompt (kokkuvõtvalt)	Mida ma tegin
1	Genereeri Python tic-tac-toe, vastaseks AI, eraldi aken, võiduprotsent + skooriala	Lõin tic_tac_toe.py — tkinter GUI, minimax-põhine AI, kolm raskusastet (juhuslikkuse määr), võidu/kaotuse verdikt + protsendiriba, skoor (võidud/viigid/kaotused) salvestatuna stats.json-i
2	Lisa AI mälukasutus MB-des + salvesta mängutulemused	Lisasin get_memory_mb() (Pythoni resource moodul, tipp-RSS), mis uueneb kord sekundis; asendasin lihtsa skoorifaili täieliku mänguajalooga game_history.json (iga mäng: aeg, tulemus, raskusaste), skoor tuletatakse nüüd sellest ajaloost
3	Näita koodifaili	Kuvasin kogu tic_tac_toe.py sisu koos struktuuri selgitusega
4	Kuhu andmed salvestatakse?	Selgitasin faili asukohta ja näitasin selle hetkesisu
5	Kerge=klassikaline 3×3, Keskmine=4×4, Raske=5×5	Kirjutasin mänguloogika ümber üldistatuks: generate_lines() genereerib võiduread suvalise laua suuruse ja N-järjest reegli jaoks; 3×3 jaoks jäi täielik minimax (täiuslik mäng), 4×4/5×5 jaoks lisasin alpha-beta kärpimisega piiratud sügavusega otsingu + heuristilise hindamisfunktsiooni (evaluate_board), kuna täielik otsing oleks liiga aeganõudev
6	Näita iga käigu järel oma võiduvõimalust	Lisasin win_probability_pct() — kasutab sama rea-põhist heuristikat, suruб tulemuse sigmoidfunktsiooni kaudu 2–98% vahemikku (täpselt 100/50/0% ainult mängu lõppedes), kuvatud tekstina + värvilise ribana, uueneb iga käigu järel
2. Tehniline arhitektuur
Algoritm: minimax + alpha-beta kärpimine (tic_tac_toe.py:96-135)
3×3 (Kerge): otsingusügavus 9 = kogu mängupuu, AI mängib matemaatiliselt täiuslikult
4×4/5×5: otsingusügavus 5 / 4 koos heuristilise hindamisega (lahtiste ridade potentsiaal), kuna täielik puu oleks liiga suur
Võiduread genereeritakse dünaamiliselt (@lru_cache) iga laua suuruse/võidupikkuse kombinatsiooni jaoks, mitte kõvakoodituna
3. Ressursianalüüs — mis läheb AI vastu mängides "maha"
Jooksutasin 8 simuleeritud mängu iga raskusastme kohta (AI mängis päris otsingu järgi, vastasena juhuslik käija), mõõtes CPU aega, otsingusõlmede arvu ja mälu:

Raskusaste	Laud	Sügavus	Sõlmi/käik	Aeg/käik	AI arvutusaeg/mäng	Mängu pikkus
Kerge	3×3	9 (täielik)	~1 220	~2,1 ms	~7 ms	~7 käiku
Keskmine	4×4	5	~6 630	~17 ms	~96 ms	~11 käiku
Raske	5×5	4	~15 270	~81 ms	~374 ms	~9 käiku
Mälu: protsessi tipp-RSS enne ja pärast 24 täismängu simulatsiooni oli identne (~25,2 MB, delta 0,00 MB). See tähendab, et rakenduse "AI mälukasutus" näit peegeldab peamiselt Pythoni/tkinteri baastarbimist, mitte AI algoritmi ennast — minimax muudab mängulauda kohapeal (in-place) ega jäta jäätmeid mällu, ja võiduridade nimekirjad on vahemällu salvestatud (lru_cache) ning taaskasutatakse.

Kokkuvõte: see AI on arvutuslikult, mitte mälu poolest kulukas — Raske (5×5) tase teeb ühe käigu kohta ~12× rohkem tööd kui Kerge (3×3), aga mälujälg püsib praktiliselt muutumatuna kogu mängu vältel.