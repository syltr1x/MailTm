from colorama import init, Fore as c
import random as r
import requests
import json
import os
init()

def get_address():
    adrsFile = open("addresses.txt", "r")
    addresses = adrsFile.read().split("\n")
    adrsFile.close()
    return addresses[r.randint(0, len(addresses)-1)]

def init_program():
    try:
        print("\n[0] Salir\n[1] Crear cuenta   [2] Mostrar cuenta\n[3] Mostrar Msj    [4] Eliminar cuenta"+("\n[5] Mostrar Cuentas" if os.path.exists('acc_info.json') else ""))
        action = int(input("Action >> "))
        if action == 0:
            print(c.GREEN+"Cerrando..."+c.WHITE)
            exit()
        elif action == 1:
            email = input("Address (not include domain)>> ")
            password = input("Password >> ")
            add_account(email, password)
        elif action == 2:
            print(c.YELLOW+"[!] Remember : This account expires in 10 minutes"+c.WHITE)
            show_account()
        elif action == 3:
            print("Revisando mensajes...")
            show_msg()
        elif action == 4:
            delete_account()
        else:
            print(c.RED+"[-] Err : Action not found..."+c.WHITE)
        init_program()
    except KeyboardInterrupt:
        print(c.RED+"\n\nCtrl+C Detectado... Cerrando programa... Bye (~.v)\n")

def add_account(email, password):
    email = email+get_address()
    # Create account in server
    url = "https://api.mail.gw/accounts"
    payload = {
        "address": email,
        "password": password
    }
    headers = { 'Content-Type': 'application/json' }
    r = requests.post(url, headers=headers, json=payload)
    data = r.text
    data = json.loads(data)
    # Detect Account file
    if os.path.exists('acc_info.json'):
        accFile = open('acc_info.json', 'r')
        accData = accFile.read()
        accData = accData[:-1][1:].replace('},', '}},').split('},') if len(accData) > 3 else []
        accFile.close()
    else: accData = []
    # Write new account in file
    accData.append('{'+f'"email":"{email}", "password":"{password}", "id":"{data["id"]}", "token":"{get_token(email, password)}"'+'}')
    print(c.GREEN+"[+] Account Created"+c.WHITE)
    accFile = open('acc_info.json', 'w')
    accFile.write('[')
    for acc in accData:
        accItem = json.loads(acc)
        if accData.index(acc) < len(accData)-1: accFile.write('\n    {\n        "email":"'+accItem["email"]+'",\n        "password":"'+accItem["password"]+'",\n        "id":"'+accItem["id"]+'",\n        "token":"'+accItem["token"]+'"\n    },')
        else: accFile.write('\n    {\n        "email":"'+accItem["email"]+'",\n        "password":"'+accItem["password"]+'",\n        "id":"'+accItem["id"]+'",\n        "token":"'+accItem["token"]+'"\n    }\n]')
    accFile.close()

def get_token(email, password):
    url = "https://api.mail.gw/token"
    payload = {
        "address": email,
        "password": password
    }
    headers = { 'Content-Type': 'application/json' }
    r = requests.post(url, headers=headers, json=payload)
    data = r.text
    data = json.loads(data)
    return data["token"]

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
    accFile = open("acc_info.json", "r")
    accData = accFile.read()
    accData = accData[:-1][1:].replace('},','}},').split('},') if len(accData) > 3 else []
    accFile.close()
    for acc in accData:
        acc = json.loads(acc)
        print(c.GREEN+"\n Direccion / Address : "+c.WHITE+acc["email"]+c.GREEN+"\n Contraseña / Password : "+c.WHITE+acc["password"]+c.GREEN+"\n Id : "+c.WHITE+acc["id"]+c.GREEN+"\n Token : "+c.WHITE+acc["token"])
    accFile.close()

def show_msg():
    with open("acc_info.json", "r") as accFile:
        data = json.loads(accFile.read())
        token = data["token"]
    accFile.close()
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
        content = mail["text"]

        print("\n------------------------------")
        print(c.GREEN+" Remitente / From : "+c.WHITE+mailS+c.GREEN+"\n Asunto / Subject : "+c.WHITE+title+c.GREEN+"\n Contenido / Content : "+c.WHITE+content)
    else:
        print(c.RED+"[!] NO TIENES NINGUN MENSAJE"+c.WHITE)


print("Bienvenido a MailTm API... v.V")
init_program()