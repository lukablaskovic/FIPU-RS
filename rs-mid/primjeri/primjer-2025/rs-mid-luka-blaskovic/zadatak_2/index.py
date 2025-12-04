from fakultet import student as s
from fakultet import podaci as p



def stvori_student_objekte(razredi_studenti: list):
    svi_student_obj = []
    for razred_info in razredi_studenti:
        naziv_razreda = razred_info["razred"]

        for student_info in razred_info["studenti"]:
            ime, prezime = student_info["ime_prezime"].split(" ", 1)

            # Pretvaranje liste kolegija u rječnik {naziv: ocjena}
            kolegij_ocjene = {
                k["naziv"]: k["ocjena"] for k in student_info["kolegiji"]
            }

            # Stvaranje instance klase Student
            student_obj = s.Student(
                ime=ime,
                prezime=prezime,
                razred=naziv_razreda,
                kolegij_ocjene=kolegij_ocjene
            )

            svi_student_obj.append(student_obj)
    return svi_student_obj


student_objekti = stvori_student_objekte(p.razredi_studenti)

for so in student_objekti:
    print(f"Student: {so.ime} {so.prezime}, Razred: {so.razred}, Kolegiji i ocjene: {so.kolegij_ocjene}")
    print(f"Prosjek: {so.prosjek_ocjena()}")

student_objekti[0].promjena_razreda("1B")
student_objekti[0].promjena_razreda("1C") #Nešto si žbalja!

print(f"{student_objekti[0].ime} je sada {student_objekti[0].razred}")