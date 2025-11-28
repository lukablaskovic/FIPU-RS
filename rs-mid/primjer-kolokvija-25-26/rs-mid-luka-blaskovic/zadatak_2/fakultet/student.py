from fakultet.podaci import razredi_studenti

moguci_razredi = set([element["razred"] for element in razredi_studenti])

class Student:
    def __init__(self, ime : str, prezime : str, razred : str, kolegij_ocjene : dict):
        self.ime = ime
        self.prezime = prezime
        self.razred = razred
        self.kolegij_ocjene = kolegij_ocjene

    def prosjek_ocjena(self) -> float:
        if not self.kolegij_ocjene:
            return 0.0
        else:
            avg = round(sum(value for value in self.kolegij_ocjene.values()) / len(self.kolegij_ocjene), 1)
            return avg
    def promjena_razreda(self, novi_razred : str) -> None:

        if novi_razred not in moguci_razredi:
            raise ValueError("Nešto si žbalja!")
        self.razred = novi_razred