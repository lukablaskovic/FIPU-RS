import hashlib

korisnici = [
  {"korisnicko_ime": "admin", "lozinka_hash" : "8d43d8eb44484414d61a18659b443fbfe52399510da4689d5352bd9631c6c51b"}, # lozinka = "lozinka123"
  {"korisnicko_ime": "markoMaric", "lozinka" : "5493c883d2b943587ea09ab8244de7a0a88d331a1da9db8498d301ca315d74fa"}, # lozinka = "markoKralj123"
  {"korisnicko_ime": "ivanHorvat", "lozinka" : "a31d1897eb84d8a6952f2c758cdc72e240e6d6d752b33f23d15fd9a53ae7c302"}, # lozinka = "lllllllllllozinka_123"
  {"korisnicko_ime": "Nada000", "lozinka":"492f3f38d6b5d3ca859514e250e25ba65935bcdd9f4f40c124b773fe536fee7d"} # lozinka = "blablabla"
]

def hash_data(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()