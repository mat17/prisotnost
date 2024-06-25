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
key = b''#kljuc
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
        kopija.append('MALICA;PRIHOD_1;ODHOD_1;PRIHOD_2;ODHOD_2;...\n')
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

def dopust():
    popup = tk.Toplevel(root)
    popup.title('Dopust')
    # okvir uporabnik
    okvir_uporabnik = tk.Frame(popup)
    okvir_uporabnik.pack()
    napis_uporabnik = tk.Label(okvir_uporabnik, text='Izberi osebo :', font=("Arial", 13))
    napis_uporabnik.pack(side='left')
    uporabnik = tk.StringVar()
    uporabnik.set('Nikogar niste izbrali.')
    napis_u = tk.Label(okvir_uporabnik, text=uporabnik.get(), font=("Arial", 13))
    seznam_uporabnikov = tk.OptionMenu(okvir_uporabnik, uporabnik, *uporabniki, command = lambda u=uporabnik, nu=napis_u: nu.configure(text=u))
    seznam_uporabnikov.pack(side='left')
    napis_u.pack(side='left')
    dnevi = [str(i+1) for i in range(31)]
    meseci = ['jan', 'feb', 'mar', 'apr', 'maj', 'jun', 'jul', 'avg', 'sep', 'okt', 'nov', 'dec']
    leto = int(datetime.now().date().year)
    leta = [str(leto-1), str(leto), str(leto+1)]
    # okvir odhod
    okvir_odhod = tk.Frame(popup)
    okvir_odhod.pack()
    napis_odhod = tk.Label(okvir_odhod, text='Belezim dopust od vkljucno:', font=("Arial", 13))
    napis_odhod.pack(side='left')
    dan_odhoda = tk.StringVar()
    dan_odhoda.set('dan')
    napis_do = tk.Label(okvir_odhod, text=dan_odhoda.get(), font=("Arial", 13))
    seznam_dnevov_odhod = tk.OptionMenu(okvir_odhod, dan_odhoda, *dnevi, command = lambda do=dan_odhoda, ndo = napis_do: ndo.configure(text=do))
    seznam_dnevov_odhod.pack(side='left')
    mesec_odhoda = tk.StringVar()
    mesec_odhoda.set('mesec')
    napis_mo = tk.Label(okvir_odhod, text=mesec_odhoda.get(), font=("Arial", 13))
    seznam_mesecev_odhod = tk.OptionMenu(okvir_odhod, mesec_odhoda, *meseci, command = lambda mo=mesec_odhoda, nmo = napis_mo: nmo.configure(text=mo))
    seznam_mesecev_odhod.pack(side='left')
    leto_odhoda = tk.StringVar()
    leto_odhoda.set('leto')
    napis_lo = tk.Label(okvir_odhod, text=leto_odhoda.get(), font=("Arial", 13))
    seznam_let_odhod = tk.OptionMenu(okvir_odhod, leto_odhoda, *leta, command = lambda lo=leto_odhoda, nlo = napis_lo: nlo.configure(text=lo))
    seznam_let_odhod.pack(side='left')
    napis_do.pack(side='left')
    napis_mo.pack(side='left')
    napis_lo.pack(side='left')
    # okvir prihod
    okvir_prihod = tk.Frame(popup)
    okvir_prihod.pack()
    napis_prihod = tk.Label(okvir_prihod, text='Belezim dopust do vkljucno:', font=("Arial", 13))
    napis_prihod.pack(side='left')
    dan_prihoda = tk.StringVar()
    napis_dp = tk.Label(okvir_prihod, text=dan_prihoda.get(), font=("Arial", 13))
    seznam_dnevov_prihod = tk.OptionMenu(okvir_prihod, dan_prihoda, *dnevi, command = lambda dp=dan_prihoda, ndp = napis_dp: ndp.configure(text=dp))
    seznam_dnevov_prihod.pack(side='left')
    mesec_prihoda = tk.StringVar()
    napis_mp = tk.Label(okvir_prihod, text=mesec_prihoda.get(), font=("Arial", 13))
    seznam_mesecev_prihod = tk.OptionMenu(okvir_prihod, mesec_prihoda, *meseci, command = lambda mp=mesec_prihoda, nmp = napis_mp: nmp.configure(text=mp))
    seznam_mesecev_prihod.pack(side='left')
    leto_prihoda = tk.StringVar()
    napis_lp = tk.Label(okvir_prihod, text=leto_prihoda.get(), font=("Arial", 13))
    seznam_let_prihod = tk.OptionMenu(okvir_prihod, leto_prihoda, *leta, command = lambda lp=leto_prihoda, nlp = napis_lp: nlp.configure(text=lp))
    seznam_let_prihod.pack(side='left')
    napis_dp.pack(side='left')
    napis_mp.pack(side='left')
    napis_lp.pack(side='left')
    # okvir geslo
    okvir_geslo = tk.Frame(popup)
    okvir_geslo.pack()
    napis_geslo = tk.Label(okvir_geslo, text='Vpišite geslo uporabnika:', font=("Arial", 13))
    napis_geslo.pack(side='left')
    geslo_vnos = tk.StringVar()
    geslo = tk.Entry(okvir_geslo, textvariable=geslo_vnos, show = '*')
    geslo.pack(side='left')
    geslo.focus_set()
    # okvir potrdi
    okvir_potrdi = tk.Frame(popup)
    okvir_potrdi.pack()
    gumb_potrdi = tk.Button(okvir_potrdi, text='Potrdi', font=("Arial", 13), bg="grey")
    gumb_potrdi.pack()
    gumb_potrdi.config(height=2, width=20, command=lambda u=uporabnik, do=dan_odhoda, mo = mesec_odhoda, lo = leto_odhoda, 
        dp= dan_prihoda, mp = mesec_prihoda, lp = leto_prihoda, 
        g = geslo: [preveri_dopust(u.get(), do.get(), mo.get(), lo.get(), dp.get(), mp.get(), lp.get(), g.get()),print(g.get()), popup.destroy()])
    

def veljavnost_datuma(d,m,l):
    if m in ['feb','apr','jun','sep','nov']:
        if m == 'feb':
            if int(l)%4 == 0:
                if int(l)%100 == 0:
                    if int(l)%400 == 0:
                        if int(d)>29:
                            return False
                    else:
                        if int(d)>28:
                            return False
                else:
                    if int(d)>29:
                        return False
            else:
                if int(d)>28:
                    return False
        else:
            if int(d)>30:
                return False
    return True


def preveri_dopust(u, do, mo, lo, dp, mp, lp, g):
    #meseci = ['jan', 'feb', 'mar', 'apr', 'maj', 'jun', 'jul', 'avg', 'sep', 'okt', 'nov', 'dec']
    print(u, do, mo, lo, dp, mp, lp, g)
    danes_l = datetime.now().date().year
    danes_m = datetime.now().date().month
    danes_d = datetime.now().date().day
    veljavnost = True
    # najprej preverimo, da dan odhoda nekje v prihodnosti, torej "vecji" od danasnjega dne"
    if int(lo) < int(danes_l):
        veljavnost = False
        print('1')
    elif int(lo) == int(danes_l):
        if meseci.index(mo)+1 < int(danes_m):
            veljavnost = False
            print('2')
        elif meseci.index(mo)+1 == int(danes_m):
            if int(do) <= int(danes_d):
                veljavnost = False
                print('3')
            else:
                pass
        else:
            pass
    else:
        pass
    #preverimo, da je dan prihoda bolj v prihodnosti kakor dan odhoda
    if veljavnost:
        if int(lp) < int(lo):
            veljavnost = False
            print('4')
        elif int(lp) == int(lo):
            if meseci.index(mp) < meseci.index(mo):
                veljavnost = False
                print('5')
            elif mp==mo:
                if int(dp) < int(do):
                    veljavnost = False
                    print('6')
            else:
                veljavnost = veljavnost_datuma(do,mo,lo) and veljavnost_datuma(dp,mp,lp)
        else:
            veljavnost = veljavnost_datuma(do,mo,lo) and veljavnost_datuma(dp,mp,lp)
    #preverimo geslo
    if g != gesla[uporabniki.index(u)]:
        messagebox.showinfo('OPOZORILO','Vneseno geslo ni pravilno. Poskusite znova.')
        print(g, gesla[uporabniki.index(u)])
        veljavnost = False
    if veljavnost:
        messagebox.showinfo('USPEH!')
        #ustvari/spremeni ustrezne .csv datoteke
    else:
        messagebox.showinfo('OPOZORILO','Napacna nastavitev datumov. Poskusite znova.')



    









 
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

buttons = [[None]*stolpci for _ in range(vrstice+1)]
for vrstica in range(vrstice):
    for stolpec in range(stolpci):
        try:
            uporabnik = uporabniki[stolpci * vrstica + stolpec]
            buttons[vrstica][stolpec] = tk.Button(root, text=uporabnik, font=("Arial", 13), bg="red")
        except:
            buttons[vrstica][stolpec] = tk.Button(root, text='')
            continue
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
            # datoteke ne obstajajo in jih zaradi tega ni mogoče brati. gumb ostaja rdec- spremembe niso potrebne
        buttons[vrstica][stolpec].grid(row=vrstica+1, column=stolpec)
        buttons[vrstica][stolpec].config(height=sirina_gumb, width=visina_gumb, command=lambda r=vrstica,c=stolpec: funkcija(r,c))
buttons[-1].append(tk.Button(root, text="DOPUST", font=("Arial", 13), bg="gray"))
buttons[-1][-1].grid(row=vrstice+1, column=2)
buttons[-1][-1].config(height=sirina_gumb, width=visina_gumb, command=lambda: dopust())

root.mainloop()

##            buttons[vrstica][stolpec] = tk.Button(root, text='/', bg="grey")
##            buttons[vrstica][stolpec].grid(row=vrstica+1, column=stolpec)
##            buttons[vrstica][stolpec].config(height=sirina_gumb, width=visina_gumb)

# VIRI:
# sprememba barve gumba
# https://stackoverflow.com/questions/67472066/tkinter-python-how-to-change-button-colour-after-clicking-other-button
# enkripcija
# https://www.geeksforgeeks.org/encrypt-and-decrypt-files-using-python/
