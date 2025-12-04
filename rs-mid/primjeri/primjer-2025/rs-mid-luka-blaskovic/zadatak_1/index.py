from data.podaci import razredi_studenti

# 1.2

def dohvati_studente_iz_razreda(razredi_studenti: list, naziv_razreda: str) -> list:
    imena_prezimena = []
    for element in razredi_studenti:
        if element["razred"] == naziv_razreda:
            for student in element["studenti"]:
                imena_prezimena.append(student["ime_prezime"])
    return imena_prezimena

#print(dohvati_studente_iz_razreda(razredi_studenti, "1B"))

def dohvati_studente_iz_razreda_comp(razredi_studenti: list, naziv_razreda:str) -> list:
    imena_prezimena = [student["ime_prezime"] for element in razredi_studenti if element["razred"] == naziv_razreda for student in element["studenti"]]
    return imena_prezimena

def dohvati_studente_iz_razreda_fn_high_order(razredi_studenti:list, naziv_razreda:str) -> list:
    element_filter = list(filter(lambda element : element["razred"] == naziv_razreda ,razredi_studenti))

    imena_prezimena = map(lambda student : student["ime_prezime"], element_filter[0]["studenti"])
    return list(imena_prezimena)

# print(dohvati_studente_iz_razreda_fn_high_order(razredi_studenti, "1A"))

# 1.3

def prosjek_studenta(razredi_studenti:list, ime_prezime:str) ->float:
    student_found = None
    for element in razredi_studenti:
        for student in element["studenti"]:
            if student["ime_prezime"] == ime_prezime:
                student_found = student
    if not student_found:
        return None
    else:
        suma = 0
        for kolegij in student_found["kolegiji"]:
            suma+= kolegij["ocjena"]
        #return round(suma / len(student_found["kolegiji"]), 1)

        # ili
        suma = sum(kolegij["ocjena"] for kolegij in student_found["kolegiji"])
        return round(suma / len(student_found["kolegiji"]), 1)

# print(prosjek_studenta(razredi_studenti, "Petar Jurić"))

# ili sa next(iterable)

def prosjek_studenta(razredi_studenti:list, ime_prezime:str) ->float:
    student_found = next(
        (student for element in razredi_studenti for student in element["studenti"] if student["ime_prezime"] == ime_prezime),
        None
    )
    return None if not student_found else round(sum(kolegij["ocjena"] for kolegij in student_found["kolegiji"]) / len(student_found["kolegiji"]), 1)

print(prosjek_studenta(razredi_studenti, "Petar Jurić"))

# 1.4 

razred_broj_studenata_list = [(element["razred"], len(element["studenti"])) for element in razredi_studenti]

# 1.5 

prvi_comprehension = [student["ime_prezime"] for element in razredi_studenti for student in element["studenti"] if element["razred"] == "1B"]