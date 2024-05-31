from colorama import init, Fore as c
import random as r
import requests
import json
import os
init()

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

def add_account():
    print("[0] Atras\n[1] Iniciar sesión   [2] Crear cuenta")
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

def write_account(email, password, token=None, id=None):
    if token == None: token = get_token(email, password)
    if id == None: id = get_id(token)
    # Detect Account file
    if os.path.exists('acc_info.json'):
        accFile = open('acc_info.json', 'r')
        accData = accFile.read()
        accData = accData[:-1][1:].replace('},', '}},').split('},') if len(accData) > 3 else []
        accFile.close()
    else: accData = []
    # Write new account in file
    accData.append('{'+f'"email":"{email}", "password":"{password}", "id":"{id}", "token":"{token}"'+'}')
    accFile = open('acc_info.json', 'w')
    accFile.write('[')
    for acc in accData:
        accItem = json.loads(acc)
        if accData.index(acc) < len(accData)-1: accFile.write('\n    {\n        "email":"'+accItem["email"]+'",\n        "password":"'+accItem["password"]+'",\n        "id":"'+accItem["id"]+'",\n        "token":"'+accItem["token"]+'"\n    },')
        else: accFile.write('\n    {\n        "email":"'+accItem["email"]+'",\n        "password":"'+accItem["password"]+'",\n        "id":"'+accItem["id"]+'",\n        "token":"'+accItem["token"]+'"\n    }\n]')
    accFile.close()

def delete_account():
    with open("acc_info.json", "r") as accFile:
        data = json.loads(accFile.read())
        id = data["id"]
        token = data["token"]
    accFile.close()
    header = {"authorization":f"Bearer {token}"}
    r = requests.delete(f"https://api.mail.gw/accounts/{id}", headers=header)
    with open("acc_info.json", "w") as accFile:
        accFile.write(" [!] NO Account Exists !!!")
    accFile.close()
    print(c.GREEN+"[+] Account Deleted"+c.WHITE)

def show_account():
    # File Verification
    if not os.path.exists('acc_info.json'):
        print(c.RED+"[!] "+c.WHITE+"No existen cuentas. Porfavor añade una primero.")
        return 0
    # Account Read and Display
    accData = get_accounts()
    if len(accData) >= 2:
        print("[0] Atras")
        for acc in range(0, len(accData), 2):
            opcion_1 = f"[{acc+1}] {json.loads(accData[acc])["email"]}"
            if acc+1 < len(accData): opcion_2 = f"[{acc+2}] {json.loads(accData[acc+1])["email"]}"
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
    if len(accounts) >= 2:
        for acc in range(0, len(accounts), 2):
            opcion_1 = f"[{acc+1}] {json.loads(accounts[acc])["email"]}"
            if acc+1 < len(accounts): opcion_2 = f"[{acc+2}] {json.loads(accounts[acc+1])["email"]}"
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

        print("\n----------------------------------------------")
        print(c.GREEN+" Remitente : "+c.WHITE+mailS+c.GREEN+"\n Fecha : "+c.WHITE+date+c.GREEN+"\n Asunto : "+c.WHITE+title+c.GREEN+"\n Contenido : "+c.WHITE+content[:56]+"...")
    else:
        print(c.RED+"[!] NO TIENES NINGUN MENSAJE"+c.WHITE)
    print("\n[0] Atras\n[1] Mostrar todo el contenido   [2] Guardar mensaje")
    option = input('Accion >> ')
    if option == "0": return 0
    if option == "1": print(c.GREEN+f"Contenido : \n{c.WHITE+content}")
    input("\n[Enter] para limpiar...")

try:
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("\n[0] Salir\n[1] Agregar cuenta      [2] Mostrar cuenta"+('s' if get_accounts('len') > 1 else '')+"\n[3] Mostrar mensajes    [4] Eliminar cuenta")
        action = input("Action >> ")
        if action == "0": exit()
        elif action == "1": add_account()
        elif action == "2": show_account()
        elif action == "3": show_msg()
        elif action == "4": delete_account()
        else: print(c.RED+"[-] Err : Accion no encontrada"+c.WHITE)
except KeyboardInterrupt:
    print(c.RED+"\n\nCtrl+C Detectado... Cerrando programa... Bye (~.v)\n")