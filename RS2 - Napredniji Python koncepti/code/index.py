


brojevi = [1,2,3,4,5]

kvadrati = list(map(lambda x: x**2, brojevi))

# rezultat = [expression for element in iterable]

kvadrati_c = [element ** 2 for element in brojevi]

niz = ["jabuka", "kruska", "brek", "banan"]

# lista velicina stringova

nizovi_map = list(map(lambda x : len(x), niz))

# rezultat = [expression for element in iterable]



brojevi = [3, 4, 6, 7, 10]

# transofmracija da dobijem kvadrate neparnih brojeva

nova = list(filter(lambda x : x % 2 == 0 , brojevi))
print(list(map(lambda x : x ** 2, nova)))

# list comprehension

# {key: value for element in iterable2}

rezultat = [broj**2 if broj % 2 == 0 else None for broj in brojevi]
print(rezultat)


