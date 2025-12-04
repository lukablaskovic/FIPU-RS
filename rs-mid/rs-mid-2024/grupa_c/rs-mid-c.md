# rs-mid (grupa C)

## FIPU Raspodijeljeni sustavi: mid-term kolokvij

### Datum: 18. 12. 2024. (online)

<br><br>
**VAŽNA NAPOMENA**: Predajete samo jednu `zip` datoteku koja sadrži sve skripte/direktorije.

> Datoteka mora biti naziva: `grupaC-ime-prezime.zip` i predaje se na **Google Forms poveznici** **na dnu Merlina/Google Chatu**.

<div style="page-break-after: always; break-after: page;"></div>

### Zadatak 1 (5 bodova)

U datoteci `TemperaturaMora.py` definirajte novu klasu `TemperaturaMora`. Definirajte konstruktor klase koji prima tri argumenta: `grad`, `temperatura_mora` i `datum`. **Implementirajte metodu** `ispis` koja ispisuje podatke o temperaturi mora u sljedećem formatu:

```
[datum] - [grad]: [temperatura_mora]°C
```

_Primjer:_

```
10.11.2024 - Zadar: 16.5°C
```

Uključite definiciju klase u skriptu `index.py`. Definirajte objekt klase `TemperaturaMora`, ali za `datum` pohranite datum vašeg rođenja (koristite modul `datetime`). Datum u metodi `ispis` formatirajte izrazom: `self.datum.strftime('%d-%m-%Y')`

_Primjer:_

```python
from datetime import datetime

neki_datum = datetime(godina, mjesec, dan) # primjer instanciranja datuma
```

Testirajte kod. Pozovite metodu `ispis` nad instancom klase.

### Zadatak 2 (10 bodova)

U datoteci `index.py` definirajte novu korutinu `simuliraj_temperaturu` koja simulira temperaturu mora za proizvoljan broj dana. Korutina očekuje dva argumenta: `broj_dana (int)` i `isSummer (bool)`. Korutina mora simulirati temperaturu mora za svaki dan u rasponu od `1` do `broj_dana`. Ako je `isSummer` postavljen na `True`, temperatura mora ne smije biti manja od 20°C. Ako je `isSummer` postavljen na `False`, temperatura mora ne smije biti veća od 20°C. Vrijednost temperature mora za svaki dan neka bude nasumično generirana vrijednost između 10 i 30°C. Za generiranje nasumične vrijednosti možete iskoristiti: `random.randint(min, max)` ili neku drugu razdiobu iz modula `random`.

**Korutina uvijek mora vratiti:** listu od `broj_dana` n-torki gdje se svaka n-torka sastoji od dva elementa: `dan`, `temperatura_mora` (npr. `(4, 25)` ). Nakon dodavanja svake n-torke u rezultantnu listu, simulirajte čekanje od 0.1 sekundi.

**U main korutini:**

- pozovite **dvaput sekvencijalno** korutinu `simuliraj_temperaturu` s različitim argumentima te ispišite rezultate u terminal. Izmjerite ukupno vrijeme izvršavanja ova dva poziva i zaokružite na 1 decimalu.
- nakon toga pozovite korutinu `simuliraj_temperaturu` **dvaput konkurentno** s istim argumentima kao i u prethodnom koraku te ispišite rezultate u terminal. Izmjerite ukupno vrijeme izvršavanja ova dva poziva i zaokružite na 1 decimalu.

**Izračunajte i ispišite u konzolu** koje je vrijeme izvršavanja bilo brže: sekvencijalno ili konkurentno. Objasnite zašto u komentaru.

### Zadatak 3 (5 bodova)

Pozovite jednom korutinu `simuliraj_temperaturu` za 30 ljetnih dana. Pohranite **rezultat korutine** u varijablu `ljetni_dani`.

Nakon toga, instancirajte objekt klase `TemperaturaMora` za grad na moru gdje biste htjeli otići na ljetovanje 2025. godine, a kao datum pohranite 1. kolovoza 2025. Postavite proizvoljnu temperaturu mora.

**Definirajte novu korutinu** `simuliraj_ljetovanje` koja **simulira promjenu temperature mora u gradu gdje ljetujete za svaki dan kolovoza 2025.** Prvi argument očekuje listu `ljetni_dani`, a drugi instancu klase `TemperaturaMora` koju ste izradili.

Unutar korutine, nad instancom pozovite metodu `dnevna_promjena(nova_temperatura, novi_datum)` za svaki element liste `ljetni_dani` (dodajte implementaciju metode `dnevna_promjena` na odgovarajuće mjesto).

Iterirajte kroz listu `ljetni_dani`, a **svaki novi dan u kolovozu** (tj. `novi_datum`) generirajte sljedećim izrazom:

```python
from datetime import timedelta
novi_datum = instanca.datum + timedelta(days=1)
```

Nakon svakog poziva metode, ispišite podatke o temperaturi mora za taj dan u terminal. Korutina nema povratnu vrijednost.

_Primjer konačnog ispisa:_

```
1-8-2025 - Dubrovnik: 24°C
2-8-2025 - Dubrovnik: 20°C
3-8-2025 - Dubrovnik: 28°C
4-8-2025 - Dubrovnik: 23°C
...
30-8-2025 - Dubrovnik: 22°C
```

### Zadatak 4 (10 bodova)

Definirajte mikroservis u datoteci `microservice_temperatura_mora.py` u kojem ćete definirati `aiohttp` poslužitelj koji sluša na proizvoljnom portu.

U mikroservisu **instancirajte 3 objekta klase** `TemperaturaMora` **za 3 različita grada s proizvoljnim podacima**.

- definirajte GET rutu `/temperatura-mora/{grad}` gdje klijent može dobiti najnoviju temperaturu mora za proslijeđeni grad u parametru rute. Vratite klijentu podatke o temperaturi mora za traženi grad (između dostupnih gradova za koje ste instancirali objekte). Ako klijent pokuša dohvatiti temperaturu mora za grad koji ne postoji, vratite odgovarajuću pogrešku i statusni kod.
  - _Primjer HTTP odgovora_: `{'temperatura_mora': '18-12-2024 - Pula: 12°C'}`
- definirajte POST rutu `/temperatura-mora/{grad}` gdje klijent može postaviti novu temperaturu mora **za proslijeđeni grad** **za današnji datum**. Klijent šalje **JSON objekt s jednim ključem** `nova_temperatura`. Ako klijent pokuša postaviti temperaturu mora za grad koji ne postoji, vratite odgovarajuću pogrešku i statusni kod. U suprotnom, ruta vraća statusni kod uspjeha i poruku `"Temperatura mora {nova_temperatura} za grad {grad} postavljena za današnji datum."`.

_Testirajte ispravnost mikroservisa koristeći neki od HTTP klijenata, npr. Thunder Client, Postman, curl._

### Zadatak 5 (10 bodova)

**Nadogradite mikroservis iz prethodnog zadatka** na sljedeći način:

- **Definirajte novu odgovarajuću rutu** koja će omogućiti simulaciju promjena temperature mora za cijeli mjesec srpanj za dani grad. Klijent šalje **JSON objekt s jednim ključem** `srpanjski_dan`. Vrijednost ključa je jedna n-torka (`dan`, `temperatura_mora`)

  - U `index.py`, generirajte 30 ljetnih dana pozivanjem korutine `simuliraj_temperaturu`. Pohranite rezultat u varijablu `srpanjski_dani`.
  - Za svaku n-torku iz `srpanjski_dani` pošaljite zahtjev na novodefiniranu rutu mikroservisa. Zahtjeve pošaljite **konkurentno** iz `index.py` skripte.
  - U definiciji rute mikroservisa (_handler_ funkciji), pozovite metodu `dnevna_promjena` za dani grad i proslijeđeni srpanjski dan. Datum definirajte za `dan` (srpnja 2025. godine) iz proslijeđene n-torke.
  - Ako je sve u redu, endpoint vraća odgovarajući statusni kod, a u tijelu odgovora: poruku dobivenu metodom `ispis`

_Primjer rezultata:_

```
[{'temp_mora': '01-07-2025 - Pula: 22°C'},
{'temp_mora': '02-07-2025 - Pula: 23°C'},
... ukupno 30 dana ...
{'temp_mora' : '30-07-2025 - Pula: 28°C'}]
```

- **Kada ste završili s prethodnim**, izmijenite implementaciju mikroservisa na način da dodate `main` korutinu u `microservice_temperatura_mora.py` te simulirate internu klijent-poslužitelj komunikaciju unutar samo ove skripte koristeći klasu `aiohttp.AppRunner` za pozadinsko izvođenje poslužitelja i klasu `aiohttp.ClientSession` za slanje 30 zahtjeva na taj (interni) poslužitelj (dakle, ne više iz `index.py` skripte).

<hr>

Ukupno bodova: **40**
Ostvareno bodova: \_\_

---
