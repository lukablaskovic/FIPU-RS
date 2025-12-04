from datetime import datetime

class VremenskaPrognoza:
    def __init__(self, grad, temperatura_zraka, datum):
        self.grad = grad
        self.temperatura_zraka = temperatura_zraka
        self.datum = datum

    def ispis(self):
        return(f"{self.datum.strftime('%d-%m-%Y')} - {self.grad}: {self.temperatura_zraka}°C")
    
    def dnevna_promjena(self, nova_temperatura, novi_datum):
        self.temperatura_zraka = nova_temperatura
        self.datum = novi_datum

