# Raspodijeljeni sustavi: Zadaci za vježbu - 21. 11. 2025.

## Asinkroni Python: asyncio, konkurentno izvršavanje, aiohttp

<img src="https://raw.githubusercontent.com/lukablaskovic/FIPU-PJS/main/0.%20Template/FIPU_UNIPU.png" style="width:20%; box-shadow: none !important; float:left;"></img>

<div style="clear: both;"></div>

### Zadatak 1:

**Definirajte korutinu `fetch_users`** koja će slati GET zahtjev na [JSONPlaceholder API](https://jsonplaceholder.typicode.com/) na URL-u: `https://jsonplaceholder.typicode.com/users`. Morate simulirate slanje 5 zahtjeva konkurentno unutar `main` korutine. Unutar `main` korutine izmjerite vrijeme izvođenja programa, a rezultate pohranite u listu odjedanput koristeći `asyncio.gather` funkciju. Nakon toga koristeći `map` funkcije ili _list comprehension_ izdvojite u zasebne 3 liste: samo imena korisnika, samo email adrese korisnika i samo username korisnika. Na kraju `main` korutine ispišite sve 3 liste i vrijeme izvođenja programa.

### Zadatak 2:

Simulirajte izvršavanje sporog I/O zadatka koristeći `sleep` funkciju koja odgađa izvršavanje programa za određeni vremenski period. Napišite sinkronu funkciju `spori_zadatak_fn` koja očekuje argument `vrijeme` (u sekundama) i simulira spori zadatak koji se izvršava toliko vremena. Funkcija treba ispisati poruku kada započne i kada završi izvršavanje. Nakon toga, napišite asinkronu verziju iste funkcije `spori_zadatak_cor`.

**Napravite po 2 poziva za svaku verziju funkcije (sinkrono i asinkrono)** s različitim vremenima trajanja (npr. 2 i 3 sekunde). Mjerite i ispišite ukupno vrijeme potrebno za izvršavanje svih poziva u svakoj verziji (sinkronoj i asinkronoj).

Kako ćete izvršiti asinkronu verziju funkcije da biste postigli konkurentno izvršavanje? Koje vrijeme trajanja očekujete kod konkurentnog izvršavanja? Pokažite rješenje sa i bez `asyncio.gather`.

### Zadatak 3:

**Definirajte dvije korutine**, od kojih će jedna služiti za dohvaćanje činjenica o mačkama koristeći `get_cat_fact` korutinu koja šalje GET zahtjev na URL: `https://catfact.ninja/fact`. Izradite 20 `Task` objekata za dohvaćanje činjenica o mačkama te ih pozovite unutar `main` korutine i rezultate pohranite odjednom koristeći `asyncio.gather` funkciju. Druga korutina `filter_cat_facts` ne šalje HTTP zahtjeve, već mora primiti gotovu listu činjenica o mačkama i vratiti novu listu koja sadrži samo one činjenice koje sadrže riječ "cat" ili "cats" (neovisno o velikim/malim slovima).

_Primjer konačnog ispisa:_

```plaintext
Filtrirane činjenice o mačkama:
- A 2007 Gallup poll revealed that both men and women were equally likely to own a cat.
- The first cat in space was a French cat named Felicette (a.k.a. “Astrocat”) In 1963, France blasted the cat into outer space. Electrodes implanted in her brains sent neurological signals back to Earth. She survived the trip.
- The lightest cat on record is a blue point Himalayan called Tinker Toy, who weighed 1 pound, 6 ounces (616 g). Tinker Toy was 2.75 inches (7 cm) tall and 7.5 inches (19 cm) long.
- The first commercially cloned pet was a cat named "Little Nicky." He cost his owner $50,000, making him one of the most expensive cats ever.
- In the 1750s, Europeans introduced cats into the Americas to control pests.
- A group of cats is called a clowder.
```

### Zadatak 4:

Napišite korutinu `autentifikacija` koja simulira proces autentifikacije korisnika. Korutina treba primiti korisničko ime i lozinku, zatim simulirati sporo I/O čekanje (npr. 2 sekunde) prije nego što vrati `True` ako su korisničko ime i lozinka ispravni. Korisničko ime i lozinku provjerite prema rječniku `korisnici` koji sadrži parove korisničko ime-lozinka.

```python
korisnici = {
    "korisnik1": "lozinka1",
    "korisnik2": "lozinka2",
    "korisnik3": "lozinka3",
}
```

Simulirajte pogrešku u autentifikaciji ako su uneseni podaci netočni (`raise ValueError`).

- Napišite glavnu funkciju koja će poslati konkurentne zahtjeve za autentifikaciju za 5 različitih korisnika (neki s ispravnim, neki s neispravnim podacima). Kako se ponaša `asyncio.gather()` kada se dogodi iznimka u jednoj od korutina?

Simulirajte grešku u autentifikaciji koja se javlja **odmah** nakon 3 sekunde čekanja (npr. ne radi autentifikacijski servis) koji će podići iznimku `TimeoutError`.

- Dodajte _timeout_ prilikom **poziva korutine** `autentifikacija` kako biste simulirali situaciju kada autentifikacijski servis ne odgovara na vrijeme.

<div style="page-break-after: always; break-after: page;"></div>

### Zadatak 5

Sljedeći isječak programskog koda pretvorite u asinkroni program s konkurentnom obradom:

```python
import requests

def fetch_url(url: str) -> str:
    response = requests.get(url, timeout=5)
    return response.text

def main():
    urls = [
        "https://example.com",
        "https://httpbin.org/get",
        "https://api.github.com"
    ]

    for url in urls:
        content = fetch_url(url)
        print(f"Fetched {len(content)} characters from {url}")

if __name__ == "__main__":
    main()
```
