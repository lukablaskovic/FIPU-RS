```bash
conda create -n user-service python=3.14
# conda env list (provjera svih conda okruženja)
conda activate user-service

# provjera ista

which python3 (bash)

pip install -r requirements.txt
```

Stvorite `.env` datoteku i dodajte odgovarajuće vrijednosti varijabli okruženja prema `.env.template`:

```bash
touch .env
cat env.template > .env
```

Pokrenite mikroservis:

```bash
python server.py
```

Za pregledavanje baze podataka (SQLite) možete koristiti npr. [DB Browser for SQLite](https://sqlitebrowser.org/).

Napomena: SQLite nije idealno rješnje za raspodijeljeni sustav gdje moramo implementirati konkurentnost i skalabilnost

- trenutno koristimo SQLite radi jednostavni i demonstracije mikroservisa, ali za stvarne projekte trebalo bi koristiti robustniji sustav: PostgreSQL, DynamoDB, itd.
