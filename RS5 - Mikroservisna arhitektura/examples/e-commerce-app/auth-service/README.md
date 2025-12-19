```bash
conda create -n auth-service python=3.14
# conda env list (provjera svih conda okruženja)
conda activate auth-service

# provjera
which python3
# ili
which python
# Očekujemo nešto u stilu: /opt/anaconda3/envs/auth-service/bin/python3......

pip install -r requirements.txt
```

Kao preduvjet za rad mikroservisa, potrebno je registrirati mikroservis na [Auth0](https://auth0.com/) platformi.

Stvorite `.env` datoteku i dodajte odgovarajuće vrijednosti varijabli okruženja prema `.env.template`:

```bash
touch .env
cat env.template > .env
```

Pokrenite mikroservis:

```bash
python server.py
```

Za direktno dobivanje auth0 tokena na serverskoj strani, može se pokrenuti skripta:

```bash
python get_auth0_access_token.py
```
