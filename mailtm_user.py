from colorama import init, Fore as c
import random as r
import requests
import json
import time as tm
import os
init()
############## GET FUNCTIONS ###############

def get_address(req='all'):
    adrsFile = open("addresses.txt", "r")
    addresses = adrsFile.read().split("\n")
    adrsFile.close()
    if req == 'all': return addresses
    elif req == 'random': return addresses[r.randint(0, len(addresses)-1)]

def get_id(token):
    url = "https://api.mail.gw/me"
    payload = {
        "token": token
    }
    header = {"authorization":f"Bearer {token}"}
    r = requests.get(url, headers=header, json=payload)
    data = json.loads(r.text)
    return data["id"] if r.status_code == 200 else r.status_code

def get_token(email, password):
    url = "https://api.mail.gw/token"
    payload = {
        "address": email,
        "password": password
    }
    headers = { 'Content-Type': 'application/json' }
    r = requests.post(url, headers=headers, json=payload)
    data = json.loads(r.text)
    return data["token"] if r.status_code == 200 else r.status_code

def get_accounts(req=""):
    if not os.path.exists('acc_info.json'): return []
    accFile = open('acc_info.json', 'r')
    accData = accFile.read()
    accData = accData[:-1][1:].replace('},', '}},').split('},') if len(accData) > 3 else []
    accFile.close()
    accData = [acc for acc in accData if len(acc) > 5]
    # Request Check
    if req == "len": return len(accData)
    return accData

def save_mail(sender, receiver, title, date, content):
    date_simple = date.split(" ")[0].replace('/','-')
    title = title[:16].replace(':','.')
    file = open(f"{title}_{date_simple}.txt", 'w', encoding='utf8')
    file.write(f'Fecha de emision: {date}')
    file.write(f'\nEmisor: {sender}')
    file.write(f'\nReceptor: {receiver}')
    file.write(f'\nContenido:\n{content}')
    file.close()
    print(c.GREEN+"[+] "+c.WHITE+f"Correo almacenado con exito en {title}.txt")

def add_account():
    print(f"{c.LIGHTRED_EX}[0]{c.WHITE} Atras\n{c.YELLOW}[1]{c.WHITE} Iniciar sesión   {c.YELLOW}[2]{c.WHITE} Crear cuenta")
    option = int(input("Action >> "))
    if option == 0: return 0
    elif option == 1:
        email = input("Address (include domain)>> ")
        password = input("Password >> ")
        token = get_token(email, password)
        id = get_id(token)
        if type(token) != int and type(id) != int:
            write_account(email, password, token=token, id=id)
        else: 
            print(c.YELLOW+"[*] "+c.WHITE+"La cuenta no existia, se creara una...")
            create_account(email, password)
            print(c.GREEN+"[+] "+c.WHITE+"Cuenta creda con exito. Almacenando datos...")
            write_account(email, password)
            print(c.GREEN+"[+] "+c.WHITE+"Cuenta almacenada con exito. Puedes continuar :)")
    elif option == 2:
        email = input("Address (not include domain)>> ")
        address = get_address('random')
        password = input("Password >> ")
        ret_code = create_account(email+address, password)
        if ret_code == 400: print(c.RED+"[-] Datos no validos. Porfavor revisa los campos.")
        if ret_code == 201:
            print(c.GREEN+"[+] "+c.WHITE+"La cuenta se ha creado correctamente. Almacenando los datos...")
            write_account(email+address, password)
            print(c.GREEN+"[+] "+c.WHITE+"La cuenta se ha almacenado correctamente. Puedes continuar :)")
        if ret_code == 422:
            print(c.YELLOW+"[!] "+c.WHITE+"La cuenta que quieres crear ya existe.\n[*] Intentando con otro dominio...")
            res_code = create_account(email+get_address('random'), password)
            if not res_code == 201: print(c.RED+"[!] "+c.WHITE+"No hemos podido crear tu cuenta. Porfavor intenta con otro nombre")
    else: print(c.RED+"[-] Err: Entrada no valida. Porfavor reintentalo."+c.WHITE)

def create_account(email, password):
    url = "https://api.mail.gw/accounts"
    payload = {
        "address": email,
        "password": password
    }
    headers = { 'Content-Type': 'application/json' }
    r = requests.post(url, headers=headers, json=payload)
    return r.status_code

def write_account(email, password, token=None, id=None, comp=None):
    if token == None: token = get_token(email, password)
    if id == None: id = get_id(token)
    accData = get_accounts()
    if comp == None: accData.append('{'+f'"email":"{email}", "password":"{password}", "id":"{id}", "token":"{token}"'+'}')
    else:
        for i in accData:
            if json.loads(i)["email"] == comp["email"]: 
                accData.remove(i)
                break
            else: print(f"{json.loads(i)["email"]} != {comp["email"]}")
    accFile = open('acc_info.json', 'w')
    accFile.write('[')
    for acc in accData:
        accItem = json.loads(acc)
        if accData.index(acc) < len(accData)-1: accFile.write('\n    {\n        "email":"'+accItem["email"]+'",\n        "password":"'+accItem["password"]+'",\n        "id":"'+accItem["id"]+'",\n        "token":"'+accItem["token"]+'"\n    },')
        else: accFile.write('\n    {\n        "email":"'+accItem["email"]+'",\n        "password":"'+accItem["password"]+'",\n        "id":"'+accItem["id"]+'",\n        "token":"'+accItem["token"]+'"\n    }\n]')
    accFile.close()

def delete_account():
    accounts = get_accounts()
    if len(accounts) == 0: print(c.RED+"[!] "+c.WHITE+"No existe ninguna cuenta."); return 0
    if len(accounts) >= 2:
        print(c.LIGHTRED_EX+"[0] "+c.WHITE+"Atras")
        for acc in range(0, len(accounts), 2):
            opcion_1 = f"{c.YELLOW}[{acc+1}]{c.WHITE} {json.loads(accounts[acc])["email"]}"
            if acc+1 < len(accounts): opcion_2 = f"{c.YELLOW}[{acc+2}]{c.WHITE} {json.loads(accounts[acc+1])["email"]}"
            else: opcion_2 = ""
            print(f"{opcion_1:<30} {opcion_2}")
        selAcc = input("Account >> ")
        try: 
            if int(selAcc) == 0: return 0
            selAcc = int(selAcc)-1
            if selAcc > len(accounts)-1 or selAcc < 0:
                print(c.RED+f"[!] Valor incorrecto, el {selAcc+1} no se encuentra en la lista"+c.WHITE)
                return 0
        except:
            print(c.RED+"[!] Valor incorrecto, porfavor ingresa un número"+c.WHITE)
            return 0
        acc = json.loads(accounts[selAcc])
    else: acc = json.loads(accounts[0])
    action = input(f"[?] Quieres borrar la cuenta: {acc["email"]} [Y/n] >> ")
    if action.lower() != "n":
        print(c.RED+"[!] "+c.WHITE+"Borrando cuenta...")
        token = get_token(acc["email"], acc["password"])
        header = {"authorization":f"Bearer {token}"}
        r = requests.delete(f"https://api.mail.gw/accounts/{id}", headers=header)
        if r.status_code == 204: print(c.GREEN+"[+] "+c.WHITE+"Cuenta eliminada exitosamente.")
        elif r.status_code == 404: print(c.YELLOW+"[*] "+c.WHITE+"La cuenta no existe.")
        write_account(None, None, comp={"email":acc["email"]})
    else: print(c.YELLOW+"[*] "+c.WHITE+"Operacion cancelada.")
    
def show_account():
    accData = get_accounts()
    if len(accData) == 0: print(c.RED+"[!] "+c.WHITE+"No existe ninguna cuenta."); return 0
    if len(accData) >= 2:
        print(c.LIGHTRED_EX+"[0] "+c.WHITE+"Atras")
        for acc in range(0, len(accData), 2):
            opcion_1 = f"{c.YELLOW}[{acc+1}]{c.WHITE} {json.loads(accData[acc])["email"]}"
            if acc+1 < len(accData): opcion_2 = f"{c.YELLOW}[{acc+2}]{c.WHITE} {json.loads(accData[acc+1])["email"]}"
            else: opcion_2 = ""
            print(f"{opcion_1:<30} {opcion_2}")
        selAcc = input("Account >> ")
        try: 
            if int(selAcc) == 0: return 0
            selAcc = int(selAcc)-1
            if selAcc > len(accData)-1 or selAcc < 0:
                print(c.RED+f"[!] Valor incorrecto, el {selAcc+1} no se encuentra en la lista"+c.WHITE)
                return 0
        except:
            print(c.RED+"[!] Valor incorrecto, porfavor ingresa un número"+c.WHITE)
            return 0
        account = json.loads(accData[selAcc])
        print(c.GREEN+"\nDireccion / Address : "+c.WHITE+account["email"]+c.GREEN+"\nContraseña / Password : "+c.WHITE+account["password"]+c.GREEN+"\nId : "+c.WHITE+account["id"]+c.GREEN+"\nToken : "+c.WHITE+account["token"])
    else: 
        account = json.loads(accData[0])
        print(c.GREEN+"\nDireccion / Address : "+c.WHITE+account["email"]+c.GREEN+"\nContraseña / Password : "+c.WHITE+account["password"]+c.GREEN+"\nId : "+c.WHITE+account["id"]+c.GREEN+"\nToken : "+c.WHITE+account["token"])
    input("\n[Enter] para limpiar...")
    
def show_msg():
    accounts = get_accounts()
    if len(accounts) == 0: print(c.RED+"[!] "+c.WHITE+"No existe ninguna cuenta."); return 0
    if len(accounts) >= 2:
        print(c.LIGHTRED_EX+"[0] "+c.WHITE+"Atras")
        for acc in range(0, len(accounts), 2):
            opcion_1 = f"{c.YELLOW}[{acc+1}]{c.WHITE} {json.loads(accounts[acc])["email"]}"
            if acc+1 < len(accounts): opcion_2 = f"{c.YELLOW}[{acc+2}]{c.WHITE} {json.loads(accounts[acc+1])["email"]}"
            else: opcion_2 = ""
            print(f"{opcion_1:<30} {opcion_2}")
        selAcc = input("Account >> ")
        try: 
            if int(selAcc) == 0: return 0
            selAcc = int(selAcc)-1
            if selAcc > len(accounts)-1 or selAcc < 0:
                print(c.RED+f"[!] Valor incorrecto, el {selAcc+1} no se encuentra en la lista"+c.WHITE)
                return 0
        except:
            print(c.RED+"[!] Valor incorrecto, porfavor ingresa un número"+c.WHITE)
            return 0
        acc = json.loads(accounts[selAcc])
    else:
        acc = json.loads(accounts[0])

    token = get_token(acc["email"], acc["password"])
    header = {"authorization":f"Bearer {token}"}
    r = requests.get("https://api.mail.gw/messages", headers=header)
    mail_sayisi = r.text
    mail_sayisi = json.loads(mail_sayisi)
    if str(mail_sayisi["hydra:member"]) != "[]":
        id = mail_sayisi["hydra:member"][0]["id"]
        r  = requests.get(f"https://api.mail.gw/messages/{id}", headers=header)
        mail = r.text
        mail = json.loads(mail)
        
        mailS = mail["from"]["address"]
        title = mail["subject"]
        date = mail["createdAt"].split("+")[0].replace("-","/").replace("T","  ")
        content = mail["text"]

        times = date.split(" ")[2].split(':')
        local_tmz_offset = -tm.timezone if tm.localtime().tm_isdst == 0 else -tm.altzone
        hour = str(int(times[0])+local_tmz_offset/3600)[:-2]
        date = f"{date.split(" ")[0]} {hour}:{times[1]}:{times[2]}"

        print("\n----------------------------------------------")
        print(c.GREEN+" Remitente : "+c.WHITE+mailS+c.GREEN+"\n Fecha : "+c.WHITE+date+c.GREEN+"\n Asunto : "+c.WHITE+title+c.GREEN+"\n Contenido : "+c.WHITE+content[:56]+"...")
        print(c.YELLOW+"\n[0] Atras\n"+c.YELLOW+"[1] "+c.WHITE+"Mostrar todo el contenido   "+c.YELLOW+"[2] "+c.WHITE+"Guardar mensaje")
        option = input('Accion >> ')
        if option == "0": return 0
        if option == "1": print(c.GREEN+f"Contenido : \n{c.WHITE+content}")
        if option == "2": save_mail(mailS, acc["email"], title, date, content)
        else: print(c.RED+f"[-] Err: No existe esa opcion"+c.WHITE)
    else:
        print(c.RED+"[!] NO TIENES NINGUN MENSAJE"+c.WHITE)
    input("\n[Enter] para limpiar...")

try:
    while True:
        tm.sleep(0.28)
        os.system('cls' if os.name == 'nt' else 'clear')
        print("\n"+c.LIGHTRED_EX+"[0] "+c.WHITE+"Salir\n"+c.YELLOW+"[1] "+c.WHITE+"Agregar cuenta      "+c.YELLOW+"[2] "+c.WHITE+"Mostrar cuenta"+('s' if get_accounts('len') > 1 else '')+"\n"+c.YELLOW+"[3] "+c.WHITE+"Mostrar mensajes    "+c.YELLOW+"[4] "+c.WHITE+"Eliminar cuenta")
        action = input("Action >> ")
        if action == "0": exit()
        elif action == "1": add_account()
        elif action == "2": show_account()
        elif action == "3": show_msg()
        elif action == "4": delete_account()
        else: print(c.RED+"[-] "+c.WHITE+"Err : Accion no encontrada")
except KeyboardInterrupt:
    print(c.RED+"\n\nCerrando programa...\n")