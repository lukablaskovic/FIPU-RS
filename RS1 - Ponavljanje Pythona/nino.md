# Raspodijeljeni sustavi: Zadaci za vježbu (RS1)

#### Datum: 31. 10. 2025.

<img src="https://web.fipulab.unipu.hr/_ipx/_/fipu_unipu_hr.png" alt="FIPUlab - Laboratorij Fakulteta informatike u Puli" style="width:20%; float:left;"/>

<div style="clear:both;"></div>

## Zadatak 1: Broj telefona

Definirajte Python funkciju `validiraj_broj_telefona(broj: str)` koja očekuje broj telefona kao ulazni parametar te vraća rječnik sa sljedećim ključevima:

```python
{
"pozivni_broj": pogledati tablicu (str),
"broj_ostatak": ostatak broja (str),
"vrsta": "fiksna mreža" ili "mobilna mreža" ili "posebne usluge" (str),
"mjesto" : pogledati tablicu (str),
"operator": pogledati tablicu (str),
"validan": True ili False (bool)
}
```

**Validacijska pravila:**

- Funkcija mora ispraviti `broj` tako da ukloni sve nepotrebne znakove (razmake, crtice, zagrade, random whitespace itd.) i provjeriti je li broj ispravan prema pravilima u nastavku.
- Pozivni broj mora biti jedan od onih navedenih u tablici ispod.
- Nakon pozivnog broja, `broj_ostatak` mora imati točno 6 ili 7 znamenki za fiksne mreže, 6 ili 7 znamenki za mobilne mreže te točno 6 znamenki za posebne usluge. `broj_ostatak` predstavlja pretplatnički dio broja (bez pozivnog broja).
- `broj` može počinjati s opcionalnim znakom `+`, `385` ili `00385`, ili pak varijante sa zagradama `(385)917217633` za međunarodne pozive; validacija to mora uzeti u obzir.
- Funkcija mora preslikati/mapirati `broj` na odgovarajuću `vrstu`, `mjesto` ili `operator` na temelju pozivnog broja.
- Ako je broj mobilan, `mjesto` postavite na `None`. Ako je broj posebne usluge, postavite `mjesto` i `operator` na `None`. Ako je broj fiksan, `operator` postavite na `None`.

Ako je broj valjan, postavite ključ `validan` na True i ispunite ostale ključeve prema tablici. Ako broj nije valjan, postavite `validan` na False te postavite samo one ključeve koje je moguće odrediti (npr. `pozivni_broj` i `broj_ostatak`).

**Još napomena:**

- Poželjno je definirati pomoćne funkcije za čišćenje i validaciju broja.

- Korisne metode: `str.replace()`, `str.startsWith()`, `str.isdigit()`, `len()`, `str.join()` (Google it).

- Zadatak probajte riješiti bez regularnih izraza (RegEx).

Tablica pozivnih brojeva:

| Pozivni broj | Mjesto / Operater                 | Vrsta          |
| ------------ | --------------------------------- | -------------- |
| 01           | Grad Zagreb i Zagrebačka županija | Fiksna mreža   |
| 020          | Dubrovačko-neretvanska županija   | Fiksna mreža   |
| 021          | Splitsko-dalmatinska županija     | Fiksna mreža   |
| 022          | Šibensko-kninska županija         | Fiksna mreža   |
| 023          | Zadarska županija                 | Fiksna mreža   |
| 031          | Osječko-baranjska županija        | Fiksna mreža   |
| 032          | Vukovarsko-srijemska županija     | Fiksna mreža   |
| 033          | Virovitičko-podravska županija    | Fiksna mreža   |
| 034          | Požeško-slavonska županija        | Fiksna mreža   |
| 035          | Brodsko-posavska županija         | Fiksna mreža   |
| 040          | Međimurska županija               | Fiksna mreža   |
| 042          | Varaždinska županija              | Fiksna mreža   |
| 043          | Bjelovarsko-bilogorska županija   | Fiksna mreža   |
| 044          | Sisačko-moslavačka županija       | Fiksna mreža   |
| 047          | Karlovačka županija               | Fiksna mreža   |
| 048          | Koprivničko-križevačka županija   | Fiksna mreža   |
| 049          | Krapinsko-zagorska županija       | Fiksna mreža   |
| 051          | Primorsko-goranska županija       | Fiksna mreža   |
| 052          | Istarska županija                 | Fiksna mreža   |
| 053          | Ličko-senjska županija            | Fiksna mreža   |
| 091          | A1 Hrvatska                       | Mobilna mreža  |
| 092          | Tomato                            | Mobilna mreža  |
| 095          | Telemach                          | Mobilna mreža  |
| 097          | bonbon                            | Mobilna mreža  |
| 098, 099     | Hrvatski Telekom                  | Mobilna mreža  |
| 0800         | Besplatni pozivi                  | Posebne usluge |
| 060          | Komercijalni pozivi               | Posebne usluge |
| 061          | Glasovanje telefonom              | Posebne usluge |
| 064          | Usluge s neprimjerenim sadržajem  | Posebne usluge |
| 065          | Nagradne igre                     | Posebne usluge |

_Source: https://hr.wikipedia.org/wiki/Pozivni_broj_

# Raspodijeljeni sustavi: Zadatak za vježbu - 31. 10. 2025.

## Zadatak: Nino Telefonino

<img src="https://raw.githubusercontent.com/lukablaskovic/FIPU-PJS/main/0.%20Template/FIPU_UNIPU.png" style="width:20%; box-shadow: none !important; float:left;"></img>

### Tekst zadatka

Ima jedan Nino kemu rabi novi telefonino. E ben, zato: Definiraj Python funkciju `validiraj_broj_telefona(broj: str)` koja očekuje broj telefona kao ulazni parametar te vraća rječnik sa sljedećim ključevima:

```python
{
"pozivni_broj": pogledati tablicu (str),
"broj_ostatak": ostatak broja (str),
"vrsta": "fiksna mreža" ili "mobilna mreža" ili "posebne usluge" (str),
"mjesto" : pogledati tablicu (str),
"operater": pogledati tablicu (str),
"validan": True ili False (bool)
}
```

**Validacijska pravila:**

- Funkcija mora ispraviti `broj` tako da ukloni sve nepotrebne znakove (razmake, crtice, zagrade, random whitespace itd.) i provjeriti je li broj ispravan prema pravilima u nastavku.
- Pozivni broj mora biti jedan od onih navedenih u tablici ispod.
- Nakon pozivnog broja, `broj_ostatak` mora imati točno 6 ili 7 znamenki za fiksne mreže, 6 ili 7 znamenki za mobilne mreže te točno 6 znamenki za posebne usluge. `broj_ostatak` predstavlja pretplatnički dio broja (bez pozivnog broja).
- `broj` može počinjati s opcionalnim znakom `+`, `385` ili `00385`, ili pak varijante sa zagradama `(385)917217633` za međunarodne pozive; validacija to mora uzeti u obzir.
- Funkcija mora preslikati/mapirati `broj` na odgovarajuću `vrstu`, `mjesto` ili `operater` na temelju pozivnog broja.
- Ako je broj mobilan, `mjesto` postavite na `None`. Ako je broj posebne usluge, postavite `mjesto` i `operater` na `None`. Ako je broj fiksan, `operater` postavite na `None`.

Ako je broj valjan, postavite ključ `validan` na True i ispunite ostale ključeve prema tablici. Ako broj nije valjan, postavite `validan` na False te postavite samo one ključeve koje je moguće odrediti (npr. `pozivni_broj` i `broj_ostatak`).

**Još napomena:**

- Poželjno je definirati pomoćne funkcije za čišćenje i validaciju broja.

- Korisne metode: `str.replace()`, `str.startsWith()`, `str.isdigit()`, `len()`, `str.join()` (Google it).

- Zadatak probajte riješiti bez regularnih izraza (RegEx).

### Tablica pozivnih brojeva RH:

| Pozivni broj | Mjesto / Operater                                             | Vrsta          |
| ------------ | ------------------------------------------------------------- | -------------- |
| 01           | Grad Zagreb i Zagrebačka županija                             | Fiksna mreža   |
| 020          | Dubrovačko-neretvanska županija                               | Fiksna mreža   |
| 021          | Splitsko-dalmatinska županija                                 | Fiksna mreža   |
| 022          | Šibensko-kninska županija                                     | Fiksna mreža   |
| 023          | Zadarska županija                                             | Fiksna mreža   |
| 031          | Osječko-baranjska županija                                    | Fiksna mreža   |
| 032          | Vukovarsko-srijemska županija                                 | Fiksna mreža   |
| 033          | Virovitičko-podravska županija                                | Fiksna mreža   |
| 034          | Požeško-slavonska županija                                    | Fiksna mreža   |
| 035          | Brodsko-posavska županija                                     | Fiksna mreža   |
| 040          | Međimurska županija                                           | Fiksna mreža   |
| 042          | Varaždinska županija                                          | Fiksna mreža   |
| 043          | Bjelovarsko-bilogorska županija                               | Fiksna mreža   |
| 044          | Sisačko-moslavačka županija                                   | Fiksna mreža   |
| 047          | Karlovačka županija                                           | Fiksna mreža   |
| 048          | Koprivničko-križevačka županija                               | Fiksna mreža   |
| 049          | Krapinsko-zagorska županija                                   | Fiksna mreža   |
| 051          | Primorsko-goranska županija                                   | Fiksna mreža   |
| 052          | Istarska županija                                             | Fiksna mreža   |
| 053          | Ličko-senjska županija                                        | Fiksna mreža   |
| 091          | A1 Hrvatska                                                   | Mobilna mreža  |
| 092          | Tomato                                                        | Mobilna mreža  |
| 095          | Telemach                                                      | Mobilna mreža  |
| 097          | bonbon                                                        | Mobilna mreža  |
| 098, 099     | Hrvatski Telekom                                              | Mobilna mreža  |
| 0800         | Besplatni pozivi                                              | Posebne usluge |
| 060          | Komercijalni pozivi                                           | Posebne usluge |
| 061          | Glasovanje telefonom                                          | Posebne usluge |
| 064          | Usluge s neprimjerenim sadržajem                              | Posebne usluge |
| 065          | Nagradne igre                                                 | Posebne usluge |
| 069          | Usluge namijenjene djeci                                      | Posebne usluge |
| 072          | jedinstveni pristupni broj za cijelu državu za posebne usluge | Posebne usluge |
