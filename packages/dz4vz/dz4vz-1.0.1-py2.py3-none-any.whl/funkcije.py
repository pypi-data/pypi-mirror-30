'''
6.) Napišite kratku Python funkciju koja prihvata pozitivan ceo broj n i vraća sumu kvadrata 
svih neparnih pozitivnih brojeva manjih od n.
'''

def suma_neparnih(n):
    if n>0:
        suma = 0
        for i in range(1,n,2):
            suma += i**2
        return suma
    else:
        return 'Broj mora da bude pozitivan.'

'''
4.) Napišite kratku Python funkciju koja prihvata pozitivan ceo broj n i vraća sumu 
kvardrata svih pozitivnih celih brojeva manjih od n.
'''

def suma_kvadrata(n):
    if n>0:
        suma = 0
        for i in range(1,n):
            suma += i**2
        return suma
    else:
        return 'Broj mora da bude pozitivan.'

'''
3.) Napišite kratku Python funkciju minmax(data) koja prihvata sekvencu jednog ili 
više brojeva i vraća najmanji i najveći broj u formi tupla (torke) dužine dva. 
Ne smete da korsitite built-in funkcije min i max pri implementaciji vašeg rešenja.
'''

def minmax(data):
    lista = []
    a = sorted(data)
    lista.insert(0, a[0])
    lista.insert(1, a[-1])
    return tuple(lista)

'''
2.) Napišite kratku Python funkciju is_even(k) koja prihvata celobrojnu vrednost i 
vraća True ako je k paran, a False ako nije. Međutim, vaša funkcija ne sme da koristi 
operacije množenja, deljenja po modulu i običnog deljenja.
'''

def is_even(k):
    parni = [0, 2, 4, 6, 8]
    return int(str(k)[-1]) in parni

'''
1.) Napišite Python funkciju is_multiple(n, m) koja prihvata dve celobrojne vrednosti i 
vraća True ako je n umnožak od m, to jest n=m*i za neki ceo broj i, u suprotnom funkcija vraća False.
'''

def is_multiple(n,m):
    return n%m == 0

'''
Primeri za testiranje po zadatku:

1.) print(is_multiple(24,4)) printa vrednost True
2.) print(is_even(20)) printa vrednost True
3.) print(minmax([4,2,6,2,6,7,5])) ili print(minmax((4,2,6,2,6,7,5))) printa tuple vrednosti (2,7).
4.) print(suma_kvadrata(4)) printa vrednost 14.
6.) print(suma_kvadratanep(4)) printa vrednost 10
'''
