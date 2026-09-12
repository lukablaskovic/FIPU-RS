## FIPU Raspodijeljeni sustavi: final kolokvij (3. 2. 2026.)

<img src="https://fipu.unipu.hr/_pub/themes_static/unipu2020/fipu/icons/fipu_hr.png" alt="Homepage - Faculty of Informatics" style="float:left; width:25%"/>

### Grupa B - online diplomski studij

<b>VAŽNE NAPOMENE (OBAVEZNO PROČITATI PRIJE RJEŠAVANJA):</b>

- Definirajte **novi radni direktorij** naziva: `rs-final-<vaše_ime>-<vaše_prezime>`. Npr. `rs-final-pero-peric`.
- Radni direktorij **možete verzionirati lokalno** koristeći `git`, ako hoćete. Učitavanje repozitorija na udaljeni poslužitelj (npr. GitHub, GitLab i sl.) **nije dozvoljeno**.
- Na Google Forms poveznicu predajete **samo jednu `zip`** (ne `rar`) **datoteku** naziva `rs-final-<vaše_ime>-<vaše_prezime>.zip` koja komprimira vaš radni direktorij i sve poddirektorije.
  - bash naredba: `→ zip -r rs-final-Ime-Prezime.zip .` ili ručno kroz GUI
- U zadacima je potrebno **implementirati samo one funkcionalnosti koje su izričito tražene**. Sve dodatne funkcionalnosti neće se uzimati u obzir pri ocjenjivanju.
- Zadaci gdje se eksplicitno traži virtualno Python okruženje moraju imati ispravnu `requirements.txt` datoteku s ovisnostima (_dependencies_) unutar direktorija aktualnog zadatka/servisa. U suprotnom, zadatak možda neće biti bodovan, ako se ne može utvrditi autentičnost rješenja.
- Sve zadatke potrebno je riješiti u programskom jeziku **Python**, **verzije 3.8 ili novije** ili druge - ako se eksplicitno traži u zadatku.
- Od pomoćnih materijala **dozvoljeno je koristiti isključivo službene šalabahtere**: `rs-mid` i `rs-final`.
- **Svaki drugi oblik korištenja nedozvoljenih materijala ili <u>alata generativne umjetne inteligencije</u> nije dozvoljen i bit će kažnjen poništavanjem svih bodova iz kontinuiranog praćenja u ovoj akademskoj godini te podnošenjem prijave Etičkom povjerenstvu Sveučilišta Jurja Dobrile u Puli**.
- Asistent može pozvati studenta na usmenu obranu kolokvija ako postoji sumnja u korištenje nedozvoljenih materijala ili alata. **Neodazivanjem ili odbijanjem usmene obrane, poništavaju se svi bodovi iz kontinuiranog praćenja u ovoj akademskoj godini**.

Iz 2. kolokvija je moguće ostvariti **maksimalno 60 bodova** iz kontinuiranog praćenja za ak. god. 2025./2026.

**Vrijeme rješavanja:** Kolokvij se piše **150min** (**2.5h**) + dodatnih **15 minuta** za *zippiranje* i predaju rješenja.

<div style="page-break-after: always; break-after: page;"></div>


### Zadatak 1 (12 bodova)

> Sustav online glasanja (e-glasanje) u teoriji izgleda jednostavno, ali u praksi je jedan od najsloženijih sustava za pouzdanu implementaciju. Razlog je što istovremeno treba zadovoljiti zahtjeve koji su međusobno u sukobu. Ukratko, e-glasanje mora biti 100% sigurno i povjerljivo te potpuno anonimno. Na izborima mora vrijediti načelo "jedan čovjek, jedan glas", ali se mora osigurati i da nitko ne može saznati kako je tko glasao. Također, mora se moći dokazati da je vaš glas pravilno prebrojan, ali bez otkrivanja identiteta glasača.

Vaš zadatak je implementirati simulaciju jednog banalnog sustava e-glasanja koristeći _FastAPI_, _aiohttp_ HTTP klijente i poslužitelje, uz dozu asinkronog Python programiranja.

**1.1 (1 bod) Implementirajte novi _FastAPI_ servis** naziva `e_voting_central_system` koji omogućava glasanje na izborima i pregled rezultata. Stvorite virtualno Python okruženje, pohranite ovisnosti i implementirajte osnovni _FastAPI_ servis u datoteci `main.py`.

**1.2 (3 boda)** Zamislite da se izbori sastoje od tri kandidata: `"MPT"`, `"Senf"` i `"Njonjo"`. **Definirajte jednostavni rječnik koji mapira imena kandidata na broj glasova koje su dobili**. Dakle, podaci se pohranjuju _in-memory_. 

Na početku, svi kandidati imaju 0 glasova. Nakon toga, **implementirajte validacijski Pydantic model** `Vote` koji sadrži sljedeća polja:

- `voter_id`: jedinstveni identifikator birača (_string_).
- `candidate`: ime kandidata za kojeg se glasa (_string_).
- `timestamp`: tipa `datetime`; ako nije specificirano u zahtjevu, postaviti na `None`.


**1.3 (6 bodova)** **Implementirajte `POST` rutu `/vote` koja prima JSON tijelo s podacima o glasanju** čiji se podaci validiraju pomoću implementiranog Pydantic modela `Vote`. *Route handler* funkcija treba:

- Implementirati jednostavni mehanizam za provjeru je li birač sa `voter_id` već glasao (_double-vote check_). Ako jest, vratiti odgovarajući HTTP statusni kod i poruku o grešci.
- ID-eve glasača koji su već glasali pohranite u odgovarajuću pomoćnu strukturu podataka - važno je da se ne pohranjuje tko je kako glasao.
- Ako birač nije glasao, povećajte na servisu broj glasova za kandidata navedenog u `candidate` polju HTTP zahtjeva i vratite odgovarajuću poruku i HTTP statusni kod o uspješnom glasanju za navedenog kandidata.


**1.4 (2 boda)** **Implementirajte `GET` rutu `/results` koja vraća trenutne rezultate glasanja** u obliku JSON objekta koji samo prikazuje broj glasova po kandidatu.

- Ako nema nijednog glasa, vratite poruku da još nema glasova.

*Primjer datotečne strukture:*

```bash
e_voting_central_system
- main.py (poslužitelj)
- models.py
```

<hr>

### Zadatak 2 (17 bodova)

>  Zamislite da HTTP zahtjevi pristižu iz različitih gradova, općina i županija, ali i iz raznih organizacija koje upravljaju sustavima za glasanje. Ipak, svi ti zahtjevi dolaze na centralni sustav za glasanje koji ste implementirali u prethodnom zadatku.

Vaš zadatak je implementirati jedan takav asinkroni Python klijent koristeći `aiohttp` biblioteku, koji će slati zahtjeve prema `e_voting_central_system` servisu i simulirati visoko opterećenje sustava slanjem velikog broja glasova konkurentnom obradom.

**2.1 (1 bod)** **U novom direktoriju `e-voting-client`, implementirajte _aiohttp_ klijent** koji će slati HTTP zahtjeve prema `e_voting_central_system`. Stvorite virtualno Python okruženje, pohranite ovisnosti, a **klijentski kod napišite u datoteci `glasacka_masina.py`**.

**2.2 (5 bodova)** Unutar `glasacka_masina.py`, implementirajte **korutinu `send_vote(voter_id: str, candidate: str)` koja šalje `HTTP POST` zahtjev na `/vote` rutu _FastAPI_ servisa** s podacima o glasanju u tijelu zahtjeva. Korutina treba:

- Koristiti `aiohttp/asyncio` za slanje asinkronih HTTP zahtjeva prema centralnom servisu za glasanje.
- Ispravno rukovati odgovorom *FastAPI* servisa i ispisati poruku u terminal o uspješnom ili neuspješnom glasanju.
- U HTTP zahtjev dodati trenutni vremenski žig: `datetime.now().isoformat()` kao vrijednost `timestamp` polja u JSON tijelu zahtjeva.


**2.3 (8 bodova)** **Implementirajte korutinu `simulate_high_load(num_votes: int)` koja simulira slanje velikog broja glasova** (npr. 5000) s različitim `voter_id`-evima i za različite kandidate. Korutina treba:

- Koristiti `asyncio/asyncio` za upravljanje asinkronim slanjem glasova, a same asinkrone zadatke izvršavati pomoću uz pomoć `send_vote` korutine.
- Generirati nasumične `voter_id` vrijednosti: `uuid.uuid4()` naredba iz `uuid` modula.
- Odabrati između kandidata `"MPT"`, `"Senf"` i `"Njonjo"` nasumično za svaki glas koristeći `random` modul prema diskretnoj uniformnoj distribuciji (svi kandidati imaju jednaku vjerojatnost odabira).
- Obaviti slanje glasova konkurentno koristeći `asyncio.gather()` kako bi se povećala učinkovitost ove simulacije i nastojao maksimalno opteretiti centralni sustav za glasanje.
- Zahtjev se treba poslati svakih `10` do `50` milisekundi (nasumično generirano vrijeme čekanja između zahtjeva) kako bi se simulirao nešto realističniji mrežni promet. Možete implementirati kao *sleep* na početku korutine za slanje zahtjeva.

> Testirajte servis koristeći HTTP klijent po izboru.

**2.4 (3 boda)** **Nadogradite validaciju Pydantic podatkovnog modela `Vote` u _FastAPI_ servisu** kako biste osigurali da:

- `voter_id` mora biti ne-prazan string (obavezno polje)
- `voter_id` mora biti točno 36 znakova dug (UUID.4 string format).
- `candidate` mora biti jedan od sljedećih enumeracija: `"MPT"`, `"Senf"`, `"Njonjo"`. (obavezno polje)
- `timestamp`, ako je naveden, mora biti tipa `datetime` (opcionalno polje)

*Primjer datotečne strukture:*

```bash
e-voting-client
- glasacka_masina.py (klijent)
```

<hr>

### Zadatak 3 (20 bodova)

>  Zamislite da dođe do kompromitacije centralnog servisa (ili nekog drugog klijenta u raspodijeljenom sustavu e-glasanja), primjerice: zlonamjerni korisnik pokuša poslati lažne HTTP zahtjeve za glasanje. U tom slučaju, želimo izraditi mehanizam na centralnom servisu koji će obavijestiti sve čvorove u sustavu o sumnjivim aktivnostima i prekinuti daljnje izvođenja e-glasanja dok se problem ne riješi (u praksi ovo bismo htjeli napraviti nekim bržim komunikacijskim protokolom od HTTP-a).

>  Nadogradite _FastAPI_ servis `e_voting_central_system` iz Zadatka 1 kako biste mu omogućili slanje obavijesti o sumnjivim aktivnostima putem HTTP protokola koristeći asinkronu _aiohttp_ klijentsku sesiju. Kada se otkrije sumnjiva aktivnost, servis treba poslati svim čvorovima u sustavu obavijest o prekidu rada raspodijeljenog sustava.

**3.1 (6 bodova)** **Dodajte unutar `glasacka_masina.py` asinkroni `aiohttp.web` poslužitelj** na način da će i dalje biti dostupne sve funkcionalnosti klijenta (#1 slanje pojedinog glasa i #2 simulaciju visokog opterećenja) te će također postojati **točno jedna `POST` ruta `/handle_suspicious_activity` koja očekuje (zaprima) obavijesti o sumnjivim aktivnostima od centralnog sustava za glasanje**.

- *aiohttp* poslužitelj neka sluša na proizvoljnom portu
- *route handler* funkcija rute `handle_suspicious_activity`  ispisuje u terminal detalje o incidentu koji pristiže s centralnog servisa i vraća ispravni statusni kod i poruku da je obavijest zaprimljena.
- *route handler* **mora zaustaviti aktivni proces** naredbom `sys.exit()` iz ugrađenog Python modula `sys`
- <u>ako hoćete</u>, radi preglednosti, kod koji se odnosi na poslužitelj moguće je prebaciti u dodatnu datoteku te koristiti kao modul unutar `glasacka_masina.py`

**3.2 (6 bodova)** **Unutar direktorija `e_voting_central_system` iz 1. zadatka, dodajte novu Python skriptu `alert_nodes.py` koja će sadržavati funkcionalnosti za slanje obavijesti svim čvorovima u raspodijeljenom sustavu**.

- U _environment_ varijablu pohranite URL-ove čvorova u sustavu (npr. `NODES_URLS`).

```python
# Možete koristiti `os.environ` za dohvat varijable okruženja, ako ju pohranite u terminal bash naredbom: export varijabla=vrijednost
# Ili, možete koristiti `python-dotenv` paket za učitavanje varijabli iz `.env` datoteke.
from dotenv import load_dotenv
load_dotenv()
varijabla = os.getenv("VARIJABLA")
```

- Unutar `alert_nodes.py`, **implementirajte korutinu `notify_suspicious_activity(activity_details: dict)`** koja će:
  - Koristiti _aiohttp_ klijentsku sesiju za slanje `HTTP POST` zahtjeva na **sve URL-ove** navedene u `NODES_URLS` varijabli okruženja.
  - Unutar tijela HTTP zahtjeva pošaljite proizvoljnu poruku s nekim detaljima sumnjive aktivnosti. Struktura JSON objekta nije bitna.
  - Korutina čeka na odgovore svih čvorova i ispisuje pojedinačne odgovore ili greške. Vi imate samo 1 čvor (iz zadatka 3.1), ali implementacija mora raditi i ako ih je više.

- Korutina `notify_suspicious_activity` mora se moći koristiti na dva načina:

  - **Direktno** - kako biste mogli izravno testirati funkcionalnost slanja obavijesti svim čvorovima.


  - **Pozivom unutar FastAPI servisa** kada se otkrije sumnjiva aktivnost - npr. pokušaj dvostrukog glasanja (iz Zadatka 1.3).


**3.3 (8 bodova)** Tijekom izvođenja simulacije glasanja, odnosno u realnom scenariju dok traje proces glasanja i klijentski kod aktivno radi, korutine `simulate_high_load` i `send_vote` preuzimaju glavnu dretvu. Posljedica toga je da poslužitelj u tom razdoblju nije u stanju obrađivati dolazne HTTP zahtjeve, uključujući i one za `/handle_suspicious_activity` rutu. Odnosno, moguće je istovremeno pokrenuti ili *aiohttp* poslužitelj ili simulaciju.

> **Pripazite**: `notify_suspicious_activity` je korutina definirana unutar `e_voting_central_system/alert_nodes.py`, dok je `handle_suspicious_activity` *handler funkcija* unutar novog *aiohttp* poslužitelja iz `glasacka_masina.py`.

- **Riješite prethodno navedeni problem tako da `simulate_high_load` i `aiohttp.web` poslužitelj** **pokrenete kao dva odvojena asinkrona zadatka (`asyncio.Task`) <u>unutar istog _event loopa_ aktivne dretve</u>**, koristeći `AppRunner` iz modula `aiohttp.web` i `asyncio` biblioteku. Zadatak je osigurati da oba zadatka rade istovremeno, bez međusobnog blokiranja.

  - `aiohttp.web` poslužitelj pokrenite na proizvoljnom portu, a korutinu `simulate_high_load` **pokrenite u pozadini** odmah nakon što se poslužitelj uspješno inicijalizira.


  - Na kraju, testirajte implementaciju tako da pokrenete `simulate_high_load(50000)`  (ili više) dok paralelno šaljete `POST` zahtjev na rutu `/handle_suspicious_activity` pomoću *FastAPI* skripte `alert_nodes.py`.


  - Mora biti vidljivo da poslužitelj i dalje ispravno obrađuje dolazni zahtjev (gasi proces) čak i pod visokim opterećenjem klijentske simulacije glasanja.

<div style="page-break-after: always; break-after: page;"></div>

*Primjer datotečne strukture:*

```bash
e_voting_central_system
- main.py (poslužitelj)
- models.py
- alert_nodes.py (klijent)
- .env
e-voting-client
- glasacka_masina.py (klijent + poslužitelj)
```

<hr>

### Zadatak 4 (11 bodova)

Izradite Docker predloške za *FastAPI* servis `e_voting_central_system` i novi `aiohttp.web` poslužitelj iz Zadatka 3.1 kako biste omogućili jednostavno pokretanje oba servisa unutar Docker kontejnera.

**4.1 (4 boda)** **Unutar direktorija `e_voting_central_system` izradite Dockerfile** koji će omogućiti izgradnju Docker predloška za vaš *FastAPI* servis. `Dockerfile` treba:

- Koristiti službeni Python bazni predložak po izboru
- Kopirati sve potrebne datoteke unutar kontejnera
- Instalirati sve potrebne ovisnosti navedene u `requirements.txt` datoteci
- Pokrenuti *FastAPI* servis koristeći `uvicorn` poslužitelj na proizvoljnom portu (*hint: naredba u šalabahteru*)

> Hint: Prilikom pokretanja Docker kontejnera, možete postaviti varijablu okruženja `NODES_URLS` kroz CLI, opcijom `-e`. _Primjer:_ `-e NODES_URLS="http://localhost:8081`  **ili** postaviti unutar Dockerfilea naredbom `ENV VARIJABLA=VRIJEDNOST`

**4.2 (4 boda)** **Unutar direktorija vašeg _aiohttp_ poslužitelja iz Zadatka 3 izradite Dockerfile** koji će omogućiti izgradnju Docker predloška za vaš asinkroni poslužitelj. `Dockerfile` treba:

- Koristiti službeni Python bazni predložak po izboru
- Kopirati sve potrebne datoteke unutar kontejnera
- Instalirati sve potrebne ovisnosti navedene u `requirements.txt` datoteci
- Dokumentirati port
- Pokrenuti Python skriptu

**4.3 (3 boda)** **Testirajte međusobnu komunikaciju oba servisa (_service-to-service communication_) pokretanjem oba Docker kontejnera (*FastAPI* i _aiohttp_)**; slanjem glasova putem _aiohttp_ simulacije na centralni servis. Također, testirajte slanje obavijesti o sumnjivim aktivnostima iz *FastAPI* servisa prema *aiohttp* poslužitelju dok traje izvođenje simulacije visokog opterećenja.

- **Važno:** U README ili komentare koda dodajte Docker CLI naredbe koje ste koristili za izgradnju predloška i pokretanje kontejnera za oba servisa.
