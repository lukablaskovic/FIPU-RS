# 3 Load balancing (Raspodjela opterećenja mikroservisa)

**Load balancing** je tehnika koja se koristi za distribuciju opterećenja između više poslužitelja, računala ili mrežnih uređaja. Ova tehnika omogućuje da se opterećenje ravnomjerno raspodijeli između više poslužitelja, kako bi se osigurala visoka dostupnost i pouzdanost sustava.

Ciljevi load balancinga su sljedeći:

- **Ravnomjerna raspodjela opterećenja** - svaki poslužitelj dobiva jednaku količinu zahtjeva
- **Visoka dostupnost** - ako jedan poslužitelj prestane raditi, drugi preuzimaju njegovo opterećenje
- **Prevencija da jedan poslužitelj postane usko grlo** - ako jedan poslužitelj postane preopterećen, load balancer preusmjerava zahtjeve na druge poslužitelje
- **Povećanje performansi** - load balancer može koristiti različite algoritme za raspodjelu opterećenja, ovisno o potrebama sustava

Postoje različite vrste load balancera, međutim mi se nećemo baviti detaljima. U ovom primjeru koristit ćemo **nginx** kao load balancer za naše mikroservise.

**nginx** je popularan web poslužitelj i _reverse proxy server_ koji se koristi za posluživanje web stranica, aplikacija i API-ja. Osim toga, **nginx** se može koristiti kao load balancer za distribuciju opterećenja između više poslužitelja.

<img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQc3C0LvR8Dxa_867W0XUhkdNX3UA9KmBDK_w&s" style="width:50%;"></img>

> Ilustracija rada load balancera

`nginx` nije dio Dockera, niti Pythona, već je zaseban softver koji se može instalirati na računalo.

Međutim, možemo koristiti `nginx` kao Docker kontejner i konfigurirati ga kao load balancer za naše mikroservise.

Možemo ga preuzeti preko Docker Huba, na sljedećoj poveznici: [https://hub.docker.com/\_/nginx](https://hub.docker.com/_/nginx)

```bash
docker pull nginx
```

**Dokumentacija**: [https://nginx.org/en/docs/](https://nginx.org/en/docs/)

## 3.1 Horizontalno skaliranje koristeći samo Docker Compose

**Horizontalno skaliranje** (_eng. Horizontal scaling_) mikroservisa odnosi se na povećanje broja instanci mikroservisa kako bi se povećala dostupnost i performanse sustava. Primjerice, ako iz našeg primjera imamo samo jednu instancu `weather-fastapi` mikroservisa, možemo dodati još jednu instancu u slučaju da prva prestane raditi.

Dakle, u ovom kontekstu samo povećavamo **broj instanci mikroservisa**.

<img src="https://github.com/lukablaskovic/FIPU-RS/blob/main/RS7%20-%20Kontejnerizacija%20i%20Load%20balancing/screenshots/horizonta-scaling.png?raw=true" style="width:50%;"></img>

> Ilustracija horizontalnog skaliranja mikroservisa

Na primjer, želimo dodati 3 replike `weather-fastapi` mikroservisa i 2 replike `aiohttp-regije` mikroservisa. To radimo kroz `docker-compose.yml` datoteku:

_Sintaksa:_

```yaml
version: "3.8"

services:
  naziv_servisa:
    image: ime_docker_predloska
    ports:
      - "host_port:container_port"
    deploy:
      replicas: broj_replika
```

Odnosno na našem primjeru:

```yaml
version: "3.8"

services:
  aiohttp-regije:
    image: aiohttp-regije:1.0
    ports:
      - "${PORT}:${PORT}"
    env_file:
      - .env
    networks:
      - interna_mreza
    deploy:
      replicas: 2

  weather-fastapi:
    image: weather-fastapi:1.0
    ports:
      - "8000:8000"
    networks:
      - interna_mreza
    deploy:
      replicas: 3

networks:
  interna_mreza: # proizvoljno ime mreže
    driver: bridge # tip mreže
```

Možemo pokrenuti ove kontejnere, međutim dobit ćemo **grešku** prilikom pokretanja budući da Docker pokušava mapirati isti port na više kontejnera prema domaćinu, što nije dozvoljeno.

<img src="https://github.com/lukablaskovic/FIPU-RS/blob/main/RS7%20-%20Kontejnerizacija%20i%20Load%20balancing/screenshots/docker-compose-swarm-problem.png?raw=true" style="width:80%;"></img>

Problem možemo riješiti koristeći **nginx** kao load balancer koji će **distribuirati zahtjeve na različite mikroservise**.

Prvo ćemo dodati `nginx` kontejner u `docker-compose.yml` datoteku:

- radi pojednostavljenja, trenutno ćemo maknuti dinamičko mapiranje portova i staviti fiksne portove za svaki mikroservis

```yaml
version: "3.8"

services:
  aiohttp-regije:
    image: aiohttp-regije:1.0
    ports:
      - "4000:4000" # fiksni port za aiohttp-regije
    networks:
      - interna_mreza
    deploy:
      replicas: 2

  weather-fastapi:
    image: weather-fastapi:1.0
    ports:
      - "8000:8000" # fiksni port za weather-fastapi
    networks:
      - interna_mreza
    deploy:
      replicas: 3

  nginx: # dodajemo nginx load balancer
    image: nginx
    ports:
      - "80:80"
    volumes: # mapiramo konfiguracijsku datoteku
      - ./nginx.conf:/etc/nginx/nginx.conf # konfiguracijska datoteka za nginx je nginx.conf
    networks:
      - interna_mreza

networks:
  interna_mreza: # proizvoljno ime mreže
    driver: bridge # tip mreže
```

`nginx` definiramo unutar konfiguracijske datoteke `nginx.conf` koja se mora nalaziti u istom direktoriju kao i `docker-compose.yml` datoteka:

Struktura direktorija:

```plaintext
compose-example/
  ├── aiohttp-regije/
  │   ├── app.py
  │   ├── requirements.txt
  │   ├── Dockerfile
  ├── weather-fastapi/
  │   ├── main.py
  │   ├── models.py
  │   ├── requirements.txt
  │   └── Dockerfile
  ├── nginx.conf
  ├── .env
  └── docker-compose.yml
```

**Reverse proxy** odnosi se na tehniku koja omogućuje da se zahtjevi preusmjere s jednog poslužitelja na drugi. U našem slučaju, `nginx` će **preusmjeravati zahtjeve na različite mikroservise**. Više o ovoj temi pročitajte na sljedećoj [poveznici](https://www.zscaler.com/resources/security-terms-glossary/what-is-reverse-proxy).

Unutar `nginx.conf` datoteke, prvo ćemo definirati `upstream` blok u kojem ćemo navesti sve mikroservise na koje će `nginx` preusmjeravati zahtjeve, to su `aiohttp-regije` i `weather-fastapi` mikroservisi:

**VAŽNO!** Bez obzira na interne portove unutar kontejnera, ovdje možemo definirati na koje portove će `nginx` preusmjeravati zahtjeve, odnosno koje portove će koristiti domaćin (**krajnji korisnik**).

Trenutni portovi definirani unutar `docker-compose.yml` su:

- `aiohttp-regije`: `4000`
- `weather-fastapi`: `8000`

Otvorite `nginx.conf` datoteku:

1. korak: definicija `events` bloka gdje navodimo najveći broj konekcija koje `nginx` može obraditi istovremeno

```plaintext
events {
    worker_connections 1024;
}
```

2. korak: definicija `http` bloka gdje navodimo `upstream` blok i `server` blok

Prvo ćemo navesti `upstream` blokove u kojima navodimo naše mikroservise:

```plaintext
http {
  upstream aiohttp-regije {
    server aiohttp-regije:4000;
  }

  upstream weather-fastapi {
    server weather-fastapi:8000;
  }
}
```

3. korak: definiramo _reverse-proxy_ na proizvoljnom portu (npr. `80`) i **preusmjeravamo sve zahtjeve** na `aiohttp-regije` i `weather-fastapi` mikroservise:

- na lokaciji `/aiohttp` preusmjeravamo sve zahtjeve na `aiohttp-regije` mikroservis
- na lokaciji `/fastapi` preusmjeravamo sve zahtjeve na `weather-fastapi` mikroservis

Ukupna konfiguracija `nginx.conf` datoteke:

```nginx
events {
    worker_connections 1024;
}


http {

upstream aiohttp-regije {
  server aiohttp-regije:4000;
}

upstream weather-fastapi {
  server weather-fastapi:8000;
}


server {
    listen 80;

    location /aiohttp {
        proxy_pass http://aiohttp-regije;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /fastapi {
        proxy_pass http://weather-fastapi;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}

}
```

Jednostavno pokrećemo opet mikroservise koristeći `docker-compose up` naredbu:

```bash
docker compose up
```

Otvorite `http://localhost/aiohttp` i `http://localhost/fastapi` u web pregledniku i provjerite radi li load balancer kako treba.

Vidimo da nema grešaka, `nginx` uspješno preusmjerava zahtjeve na `aiohttp-regije` i `weather-fastapi` mikroservise.

```bash
nginx-1            | /docker-entrypoint.sh: /docker-entrypoint.d/ is not empty, will attempt to perform configuration
nginx-1            | /docker-entrypoint.sh: Looking for shell scripts in /docker-entrypoint.d/
nginx-1            | /docker-entrypoint.sh: Launching /docker-entrypoint.d/10-listen-on-ipv6-by-default.sh
nginx-1            | 10-listen-on-ipv6-by-default.sh: info: IPv6 listen already enabled
nginx-1            | /docker-entrypoint.sh: Sourcing /docker-entrypoint.d/15-local-resolvers.envsh
nginx-1            | /docker-entrypoint.sh: Launching /docker-entrypoint.d/20-envsubst-on-templates.sh
nginx-1            | /docker-entrypoint.sh: Launching /docker-entrypoint.d/30-tune-worker-processes.sh
nginx-1            | /docker-entrypoint.sh: Configuration complete; ready for start up
weather-fastapi-1  | INFO:     Started server process [1]
weather-fastapi-1  | INFO:     Waiting for application startup.
weather-fastapi-1  | INFO:     Application startup complete.
weather-fastapi-1  | INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
nginx-1            | 172.20.0.1 - - [22/Jan/2025:08:12:35 +0000] "GET /aiohttp HTTP/1.1" 404 14 "-" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36"
weather-fastapi-1  | INFO:     172.20.0.4:59704 - "GET /fastapi HTTP/1.0" 404 Not Found
nginx-1            | 172.20.0.1 - - [22/Jan/2025:08:12:38 +0000] "GET /fastapi HTTP/1.1" 404 22 "-" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36"
nginx-1            | 172.20.0.1 - - [22/Jan/2025:08:16:49 +0000] "GET /aiohttp HTTP/1.1" 404 14 "-" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36"
weather-fastapi-1  | INFO:     172.20.0.4:33340 - "GET /fastapi HTTP/1.0" 404 Not Found
nginx-1            | 172.20.0.1 - - [22/Jan/2025:08:16:51 +0000] "GET /fastapi HTTP/1.1" 404 22 "-" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36"
```

Vidimo da u Docker Desktopu nemamo više duple instance `weather-fastapi` i `aiohttp-regije` mikroservisa, već samo jednu instancu svakog mikroservisa, a `nginx` uspješno preusmjerava zahtjeve na njih.

Dakle, **horizontalno skaliranje** mikroservisa možemo postići kroz `docker-compose.yml` datoteku i `nginx` kao load balancer, a cijelu apstrakciju balansiranja izvršava sam `nginx` kontejner 😎

<img src="https://github.com/lukablaskovic/FIPU-RS/blob/main/RS7%20-%20Kontejnerizacija%20i%20Load%20balancing/screenshots/comopse-nginx-correct.png?raw=true" style="width:100%;"></img>

> Load balancer `nginx` uspješno preusmjerava zahtjeve na `aiohttp-regije` i `weather-fastapi` mikroservise
