## FIPU Raspodijeljeni sustavi: final kolokvij (2. 2. 2026.)


<b>Ime i prezime:</b> <span>___________________________________________________________________________________________________</span>
<br><br>
<b>JMBAG:</b> <span>____________________________________________________________________________________________________</span>
<br>
<b>Potpis:</b> <span>___________________________________________________________________________________________________</span>

<b>VAŽNE NAPOMENE (OBAVEZNO PROČITATI PRIJE RJEŠAVANJA):</b>

- Definirajte **novi radni direktorij** naziva: `rs-final-<vaše_ime>-<vaše_prezime>`. Npr. `rs-final-sanja-sanjic`.
- Radni direktorij **možete verzionirati lokalno** koristeći `git`, ako hoćete. Učitavanje repozitorija na udaljeni poslužitelj (npr. GitHub, GitLab i sl.) **nije dozvoljeno**.
- Na Google Forms poveznicu predajete **samo jednu `zip`** (ne `rar`) **datoteku** naziva `rs-final-<vaše_ime>-<vaše_prezime>.zip` koja komprimira vaš radni direktorij i sve poddirektorije.
  - bash naredba: `→ zip -r rs-final-Ime-Prezime.zip .` ili ručno kroz GUI
- U zadacima je potrebno **implementirati samo one funkcionalnosti koje su izričito tražene**. Sve dodatne funkcionalnosti neće se uzimati u obzir pri ocjenjivanju.
- Zadaci gdje se eksplicitno traži virtualno Python okruženje moraju imati ispravnu `requirements.txt` datoteku s ovisnostima (_dependencies_) unutar direktorija aktualnog zadatka. U suprotnom, zadatak možda neće biti bodovan.
- Sve zadatke potrebno je riješiti u programskom jeziku **Python**, **verzije 3.8 ili novije** ili druge ako se eksplicitno traži u zadatku.
- Od pomoćnih materijala **dozvoljeno je koristiti isključivo službene šalabahtere**: `rs-mid` i `rs-final`.
- **Svaki drugi oblik korištenja nedozvoljenih materijala ili <u>alata generativne umjetne inteligencije</u> nije dozvoljen i bit će kažnjen poništavanjem svih bodova iz kontinuiranog praćenja u ovoj akademskoj godini te podnošenjem prijave Etičkom povjerenstvu Sveučilišta u Puli**.
- Asistent može pozvati studenta na usmenu obranu kolokvija ako postoji sumnja u korištenje nedozvoljenih materijala ili alata.

Iz kolokvija je moguće ostvariti **maksimalno 60 bodova** iz kontinuiranog praćenja za ak. god. 2025./2026.

<hr>

### Zadatak 1 (12 bodova)

Sustav online glasanja (e-glasanje) u teoriji izgleda jednostavno, ali u praksi je jedan od najsloženijih sustava za pouzdanu implementaciju. Razlog je što istovremeno treba zadovoljiti zahtjeve koji su međusobno u sukobu. Ukratko, e-glasanje mora biti 100% sigurno i povjerljivo te potpuno anonimno. Na izborima mora vrijediti načelo "jedan čovjek, jedan glas", ali se mora osigurati i da nitko ne može saznati kako je tko glasao. Također, mora se moći dokazati da je vaš glas pravilno prebrojan, ali bez otkrivanja identiteta glasača.

Vaš zadatak je implementirati simulaciju jednog banalnog sustava e-glasanja koristeći FastAPI, a zatim testirati njegovu funkcionalnost pomoću asinkronog _aiohttp_ klijenta/poslužitelja.

1.1 **Implementirajte novi FastAPI servis** naziva `e_voting_central_system` koji omogućava glasanje na izborima i pregled rezultata. Stvorite virtualno Python okruženje, pohranite ovisnosti i implementirajte osnovni FastAPI servis u datoteci `main.py`.

1.2 Zamislite da se izbori sastoje od tri kandidata: `"Alice"`, `"Bob"` i `"Charlie"`. **Definirajte novi rječnik koji mapira imena kandidata na broj glasova koje su dobili**. Dakle, podaci se pohranjuju _in-memory_. Na početku, svi kandidati imaju 0 glasova. Nakon toga, **implementirajte validacijski Pydantic model** `Vote` koji sadrži sljedeća polja:

- `voter_id`: jedinstveni identifikator birača (string).
- `candidate`: ime kandidata za kojeg se glasa (string).
- `timestamp`: tipa `datetime`, ako nije specificirano, postaviti na `None` ili trenutno vrijeme.


1.3 **Implementirajte `POST` rutu `/vote` koja prima JSON tijelo s podacima o glasanju** čiji se podaci validiraju pomoću implementiranog Pydantic modela `Vote`. Ruta treba:

- Implementirati jednostavni mehanizam za provjeru je li birač sa `voter_id` već glasao (_double-vote check_). Ako jest, vratiti odgovarajući HTTP statusni kod i poruku o grešci.
- Ako birač nije glasao, povećati broj glasova za kandidata navedenog u `candidate` polju i vratiti poruku o uspješnom glasanju za tog kandidata.


1.4 **Implementirajte `GET` rutu `/results` koja vraća trenutne rezultate glasanja** u obliku JSON objekta koji samo prikazuje broj glasova po kandidatu.

Testirajte servis koristeći alate poput curl-a, Postman-a, ugrađene FastAPI dokumentacije (Swagger UI) ili bilo kojeg drugog alata po vlastitom izboru.

### Zadatak 2 (15 bodova)

Zamislite da HTTP zahtjevi dolaze iz različitih gradova, općina, županija, ali i organizacija koje održavaju rješenja za glasanje. Ipak, svi ti zahtjevi dolaze na centralni sustav za glasanje koji ste implementirali u prethodnom zadatku.

Vaš zadatak je implementirati jedan takav asinkroni klijent koristeći `aiohttp` biblioteku, koji će slati zahtjeve FastAPI servisu `e_voting_central_system` i simulirati visoko opterećenje sustava slanjem velikog broja glasova konkurentno.

2.1 **Implementirajte novi _aiohttp_ klijent** koji će slati HTTP zahtjeve prema `e_voting_central_system`. Stvorite virtualno Python okruženje, pohranite ovisnosti, a **klijentski kod napišite u datoteci `client.py`**.

2.2 Unutar `client.py`, implementirajte **korutinu `send_vote(voter_id: str, candidate: str)` koja šalje `HTTP POST` zahtjev na `/vote` rutu FastAPI servisa** s podacima o glasanju u tijelu zahtjeva. Korutina treba:

- Koristiti `aiohttp/asyncio` za slanje asinkronih HTTP zahtjeva prema centralnom servisu za glasanje.
- Rukovati odgovorom servisa i ispisati poruku o uspješnom ili neuspješnom glasanju (ovisno o HTTP odgovoru).
- U HTTP zahtjev dodati trenutni vremenski žig (`datetime.now()`) pod `timestamp` atribut.


2.3 **Implementirajte korutinu `simulate_high_load(num_votes: int)` koja simulira slanje velikog broja glasova** (npr. 1000) s različitim `voter_id`-em i za različite kandidate. Korutina treba:

- Koristiti `asyncio/asyncio` za upravljanje asinkronim slanjem glasova i pozivati `send_vote` korutinu za svaki glas.
- Generirati nasumične `voter_id` vrijednosti koristeći `uuid.uuid4()` naredbu iz iz `uuid` modula.
- Odabrati između kandidata `"Alice"`, `"Bob"` i `"Charlie"` nasumično za svaki glas koristeći `random` modul prema diskretnoj uniformnoj distribuciji (svi kandidati imaju jednaku vjerojatnost odabira).
- Obaviti slanje glasova asinkrono koristeći `asyncio.gather()` kako bi se povećala učinkovitost ove simulacije glasanja i nastojao maksimalno opteretiti centralni sustav za glasanje.
- Zahtjev se treba poslati svakih `10` do `50` milisekundi (nasumično generirano vrijeme čekanja između zahtjeva) kako bi se simulirao realističniji mrežni promet.

Testirajte vaš _aiohttp_ klijent pokretanjem `simulate_high_load(1000)` unutar `client.py` datoteke.

Izmjerite vrijeme potrebno za slanje svih glasova i ispišite ga krajem izvođenja korutine.

2.4 **Nadogradite validaciju Pydantic podatkovnog modela `Vote` u FastAPI servisu** kako biste osigurali da:

- `voter_id` mora biti ne-prazan string.
- `voter_id` mora biti točno 36 znakova dug (UUID.4 string format).
- `candidate` mora biti jedan od sljedećih vrijednosti: "Alice", "Bob", "Charlie".
- `timestamp` mora biti tipa `datetime`.

### Zadatak 3 (18 bodova)

Zamislite da dođe do kompromitacije vašeg centralnog servisa (ili nekog drugog klijenta u raspodijeljenom sustavu e-glasanja) i zlonamjerni korisnik pokuša poslati lažne zahtjeve za glasanje. U tom slučaju, želimo izraditi mehanizam na centralnom servisu koji će obavijestiti sve relevantne čvorove u sustavu o sumnjivim aktivnostima i prekinuti daljnje izvođenja e-glasanja dok se problem ne riješi.

Nadogradite FastAPI servis `e_voting_central_system` iz Zadatka 1 kako biste mu omogućili slanje obavijesti o sumnjivim aktivnostima putem HTTP protokola koristeći asinkronu _aiohttp_ klijentsku sesiju. Kada se otkrije sumnjiva aktivnost, servis treba poslati svim čvorovima u sustavu obavijest o prekidu e-glasanja. Sam prekid nije potrebno implementirati - samo obavještavanje.

3.1 **Unutar direktorija `e_voting_central_system`** **implementirajte Python skriptu `alert_clients.py` koja će sadržavati funkcionalnosti za slanje obavijesti svim čvorovima u sustavu**.

- U _environment_ varijablu pohranite popis URL-ova čvorova u sustavu (npr. `CLIENT_URLS`). Možete koristiti `os.environ` za dohvat varijable okruženja ili `python-dotenv` paket za učitavanje iz `.env` datoteke.
- Unutar `alert_clients.py`, **implementirajte korutinu `notify_suspicious_activity(activity_details: dict)`** koja će:
  - Koristiti `aiohttp` klijentsku sesiju za slanje `HTTP POST` zahtjeva na **sve URL-ove** navedene u `CLIENT_URLS` varijabli okruženja.
  - Unutar tijela HTTP zahtjeva pošaljite proizvoljnu poruku s nekim detaljima sumnjive aktivnosti (npr. `activity_details` rječnik).
  - Čeka na odgovore svih čvorova i ispisuje pojedinačne odgovore ili greške ako ih ima. Vi imate samo 1 čvor (klijent iz drugog zadatka), ali implementacija mora raditi i ako ih je više.

Korutina iz skripte `alert_clients.py` mora se moći koristiti na dva načina:

- **Direktno** - kako biste mogli testirati funkcionalnost slanja obavijesti svim čvorovima.

- **Pozivom korutine unutar FastAPI servisa** kada se otkrije sumnjiva aktivnost - pokušaj dvostrukog glasanja (iz Zadatka 1).


3.2 **Transformirajte _aiohttp_ klijenta iz Zadatka 2 u `aiohttp.web` asinkroni poslužitelj** koji će i dalje omogućavati sve funkcionalnosti klijenta (#1 slanje pojedinog glasa i #2 simulaciju visokog opterećenja) te će također imati **novu `POST` rutu `/suspicious_activity` koja očekuje (zaprima) obavijesti o sumnjivim aktivnostima od centralnog sustava za glasanje**.

- Tijekom izvođenja simulacije glasanja, odnosno u realnom scenariju dok traje proces glasanja i klijentski kod aktivno radi, korutina `simulate_high_load` preuzima glavnu dretvu izvođenja. Posljedica toga je da poslužitelj u tom razdoblju nije u stanju obrađivati dolazne HTTP zahtjeve, uključujući i one na `/suspicious_activity` rutu.


3.3 **Riješite prethodno navedeni problem tako da `simulate_high_load` i `aiohttp.web` poslužitelj** **pokrenete kao dva odvojena asinkrona zadatka (Task) unutar istog _event loopa_**, koristeći `AppRunner` iz modula `aiohttp.web` i `asyncio` biblioteku.

Zadatak je osigurati da oba zadatka rade istovremeno, bez međusobnog blokiranja.

- `aiohttp.web` poslužitelj pokrenite na proizvoljnom portu, a korutinu `simulate_high_load` **pokrenite u pozadini** odmah nakon što se poslužitelj uspješno inicijalizira.

- Na kraju testirajte implementaciju tako da pokrenete `simulate_high_load(10000)` dok paralelno šaljete POST zahtjeve na rutu `/suspicious_activity` pomoću FastAPI skripte `alert_clients.py`.

- Na taj način mora biti vidljivo da poslužitelj i dalje ispravno obrađuje dolazne zahtjeve čak i pod visokim opterećenjem klijentske simulacije.

### Zadatak 4 (15 bodova)

Izradite Docker predloške za FastAPI servis `e_voting_central_system` i novi `aiohttp.web` poslužitelj iz Zadatka 3 kako biste omogućili jednostavno pokretanje oba servisa unutar Docker kontejnera.

4.1 **Unutar direktorija `e_voting_central_system` izradite Dockerfile** koji će omogućiti izgradnju Docker predloška za vaš FastAPI servis. `Dockerfile` treba:

- Koristiti službeni Python bazni predložak
- Kopirati sve potrebne datoteke unutar kontejnera
- Instalirati sve potrebne ovisnosti navedene u `requirements.txt` datoteci
- Pokrenuti FastAPI servis koristeći `uvicorn` poslužitelj na proizvoljnom portu

Prilikom pokretanja docker kontejnera, možete postaviti varijablu okruženja `CLIENT_URLS` kroz CLI, opcijom `-e`. _Primjer:_ `-e CLIENT_URLS="http://localhost:8081`.

4.2 **Unutar direktorija vašeg _aiohttp_ poslužitelja iz Zadatka 3 izradite Dockerfile** koji će omogućiti izgradnju Docker predloška za vaš asinkroni poslužitelj. `Dockerfile` treba:

- Koristiti službeni Python bazni predložak
- Kopirati sve potrebne datoteke unutar kontejnera
- Instalirati sve potrebne ovisnosti navedene u `requirements.txt` datoteci
- Pokrenuti _aiohttp_ poslužitelj na **proizvoljnom portu**

4.3 **Testirajte međusobnu komunikaciju oba servisa (_service-to-service communication_) pokretanjem oba Docker kontejnera (FastAPI i _aiohttp_)**; slanjem glasova putem _aiohttp_ simulacije na centralni servis. Također, testirajte slanje obavijesti o sumnjivim aktivnostima iz FastAPI servisa prema `aiohttp` poslužitelju dok traje izvođenje simulacije visokog opterećenja.

4.4 **Implementirajte Docker Compose unutar radnog direktorija** koji će omogućiti jednostavno pokretanje oba sustava (FastAPI i aiohttp) koristeći jednu Docker Compose naredbu. Definirajte potrebne servise, zajedničku mrežu i varijable okruženja unutar `docker-compose.yml` datoteke.

Pokrenite oba servisa koristeći Docker Compose i testirajte njihove izolirane funkcionalnosti i međusobnu komunikaciju.
