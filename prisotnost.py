import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
import os
import re
from datetime import datetime
import time
from cryptography.fernet import Fernet

uporabniki = []
gesla = []
meseci = ['jan', 'feb', 'mar', 'apr', 'maj', 'jun', 'jul', 'avg', 'sep', 'okt', 'nov', 'dec']
key = b'12345678901234567890123456789012345678901234'#kljuc
fernet = Fernet(key)

input('Pozdravljeni.\n'+
      'Prosimo, pritisnite ENTER in potem izberite datoteko, \n'+
      'kjer se nahajajo imena uporabnikov in gesla.\n')
tk.Tk().withdraw()
filename = filedialog.askopenfilename()

with open (filename,'rb') as f:
    encrypted = f.read()

decrypted = fernet.decrypt(encrypted)
decrypted = decrypted.decode("utf-8")
decrypted = decrypted.strip().split('\r\n')
for vrstica in decrypted:
    uporabnik, geslo = vrstica.strip().split(',')
    uporabnik = uporabnik.strip()
    geslo = geslo.strip()
    uporabniki.append(uporabnik)
    gesla.append(geslo)

def funkcija(row, col):
    popup = tk.Toplevel(root)
    popup.title('Geslo')
    napis = tk.Label(popup, text='Vnesi geslo za uporabnika ' + uporabniki[stolpci * row + col] + ':', font=("Arial", 13))
    vnos_tekst = tk.StringVar()
    vnos = tk.Entry(popup, textvariable=vnos_tekst, show = '*')
    vnos.focus_set()
    gumb = tk.Button(popup, text="Potrdi", height= 1, width=10, font=("Arial", 13))
    gumb.config(command= lambda r=row, c=col, v=vnos: [preveri(r,c,vnos.get()), popup.destroy()])
    napis.pack()
    vnos.pack()
    gumb.pack()

def preveri(row, col, vnos):
    if vnos != gesla[stolpci*row + col]:
        messagebox.showinfo('OPOZORILO','Vneseno geslo ni pravilno. Poskusite znova.')
    else:
        if buttons[row][col]['bg'] == 'green':
            vpr_malica(row, col)
        else:
            spremeni_stanje(row, col, False)

def vpr_malica(row, col):
    mesec = datetime.now().date().month
    mesec = meseci[int(mesec) - 1]
    uporabnik = uporabniki[stolpci*row + col]
    try:
        os.rename(f'{mesec}-{uporabnik}.csv', f'{mesec}-{uporabnik}.txt')
    except:
        pass
    with open(f'{mesec}-{uporabnik}.txt','r') as datoteka:
        malica = datoteka.readlines()
        malica = malica.pop(-1).strip().split(';')
        malica = malica[0]
    if malica == 'DA':
        spremeni_stanje(row,col, False)
    else:
        popup = tk.Toplevel(root)
        popup.title('Malica')
        napis = tk.Label(popup, text = 'Si malical?', font=("Arial", 13))
        gumb_ja = tk.Button(popup, text = 'DA', font=("Arial", 13))
        gumb_ja.config(command= lambda r=row, c=col: [spremeni_stanje(row, col, True), popup.destroy()])
        gumb_ne = tk.Button(popup, text = 'NE', font=("Arial", 13))
        gumb_ne.config(command= lambda r=row, c=col: [spremeni_stanje(row, col, False), popup.destroy()])
        napis.pack()
        gumb_ja.pack()
        gumb_ne.pack()

def spremeni_stanje(row, col, malica_da):
    mesec = datetime.now().date().month
    mesec = meseci[int(mesec) - 1]
    dan = datetime.now().date().day
    ura = datetime.now().time().hour
    ura = str(ura) + ":"
    minute = datetime.now().time().minute
    ura += str(minute)
    uporabnik = uporabniki[stolpci*row + col]
    #spremeni barvo gumba, razen ce smo samo oznacili malicanje
    if buttons[row][col]['bg'] == 'green':
        if not malica_da:
            buttons[row][col].config(bg = 'red')
    else:
        buttons[row][col].config(bg = 'green')
    #ali se je uporabnik ta mesec ze prijavil? ce ja, preveri, ali obstaja vrstica za danasnji dan
    if os.path.exists(f'{mesec}-{uporabnik}.csv') or os.path.exists(f'{mesec}-{uporabnik}.txt'): 
        try:
            os.rename(f'{mesec}-{uporabnik}.csv', f'{mesec}-{uporabnik}.txt')
        except:
            pass
        with open(f'{mesec}-{uporabnik}.txt','r+') as datoteka:
            kopija = datoteka.readlines()
            zadnji_dan = len(kopija) - 1
            if zadnji_dan < int(dan):
                for _ in range(int(dan)-zadnji_dan-1):
                    kopija.append('\n')
                kopija.append('NE\n')
    #uporabnik se ta mesec se ni prijavil in gotovo nima vrstice za danasnji dan
    else:
        kopija = []
        kopija.append('MALICA;PRIHOD_1, ODHOD_1;PRIHOD_2;ODHOD_2;...\n')
        for _ in range(dan-1):
            kopija.append('\n')
        kopija.append('NE\n')
    zadnja_vrstica = kopija.pop(-1).strip().split(';')
    if malica_da:
        zadnja_vrstica[0] = 'DA'
    else:
        zadnja_vrstica.append(ura)
    zadnja_vrstica = ';'.join(zadnja_vrstica)
    zadnja_vrstica += '\n'
    with open(f'{mesec}-{uporabnik}.txt','w') as datoteka:
        for vrstica in kopija:
            datoteka.write(vrstica)
        datoteka.write(zadnja_vrstica)
        datoteka.truncate()
    os.rename(f'{mesec}-{uporabnik}.txt', f'{mesec}-{uporabnik}.csv')
    
root = tk.Tk()
root.title('Evidentiranje prisotnosti')

label1= tk.Label(root, text=
                 'Rdeci gumbi oznacujejo odsotne sodelavce. \n'+
                 'Zeleni gumbi oznacujejo prisotne sodelavce.\n'+
                 '      Gumbu spremenite barvo tako, da kliknete nanj.')
label1.grid(row=0, column=0, columnspan=3, padx=0, pady=5, sticky='w')

stolpci = 3
vrstice = len(uporabniki)//3 + (len(uporabniki)%3)%2 + (len(uporabniki)%3)//2
sirina_gumb = 3
visina_gumb = 25
bckgrnd =["red", "green"]

mesec = datetime.now().date().month
mesec = meseci[int(mesec) - 1]
dan = int(datetime.now().date().day)

buttons = [[None]*stolpci for _ in range(vrstice)]
for vrstica in range(vrstice):
    for stolpec in range(stolpci):
        try:
            uporabnik = uporabniki[stolpci * vrstica + stolpec]
            buttons[vrstica][stolpec] = tk.Button(root, text=uporabnik, font=("Arial", 13), bg="red")
            try:
                os.rename(f'{mesec}-{uporabnik}.csv', f'{mesec}-{uporabnik}.txt')
                with open(f'{mesec}-{uporabnik}.txt','r') as datoteka:
                    zadnja = datoteka.readlines()
                    zadnji_dan = len(zadnja)-1
                    zadnja = zadnja.pop(-1).strip().split(';')
                if len(zadnja)%2==0 and zadnji_dan == dan:
                    buttons[vrstica][stolpec].config(bg = 'green')
                os.rename(f'{mesec}-{uporabnik}.txt', f'{mesec}-{uporabnik}.csv')
            except:
                pass
            buttons[vrstica][stolpec].grid(row=vrstica+1, column=stolpec)
            buttons[vrstica][stolpec].config(height=sirina_gumb, width=visina_gumb, command=lambda r=vrstica,c=stolpec: funkcija(r,c))
        except:
            pass

root.mainloop()

##            buttons[vrstica][stolpec] = tk.Button(root, text='/', bg="grey")
##            buttons[vrstica][stolpec].grid(row=vrstica+1, column=stolpec)
##            buttons[vrstica][stolpec].config(height=sirina_gumb, width=visina_gumb)

# VIRI:
# sprememba barve gumba
# https://stackoverflow.com/questions/67472066/tkinter-python-how-to-change-button-colour-after-clicking-other-button
# enkripcija
# https://www.geeksforgeeks.org/encrypt-and-decrypt-files-using-python/
