from colorama import init, Fore as c
import requests
import json
init()

def init_program():
    try:
        print("\n[0] Salir\n[1] Crear cuenta   [2] Mostrar cuenta\n[3] Mostrar Msj    [4] Eliminar cuenta")
        action = int(input("Action >> "))
        if action == 0:
            print(c.GREEN+"Cerrando..."+c.WHITE)
            exit()
        elif action == 1:
            email = input("Address (not include domain)>> ")+"@bukhariansiddur.com"
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
    url = "https://api.mail.gw/accounts"
    payload = {
        "address": email,
        "password": password
    }
    headers = { 'Content-Type': 'application/json' }
    r = requests.post(url, headers=headers, json=payload)
    data = r.text
    data = json.loads(data)
    print("------------------------------")
    print(c.GREEN+"[+] Acount Created"+c.WHITE)
    with open("acc_info.json", "w") as accFile:
        accFile.write('{\n    "email":"'+data["address"]+'",\n        "password":"'+password+'",\n        "id":"'+data["id"]+'",')
    get_token(email, password)

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
    with open("acc_info.json", "a") as accFile:
        accFile.write('\n        "token":"'+data["token"]+'"\n}')
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
    with open("acc_info.json", "r") as accFile:
        data = json.loads(accFile.read())
        print(c.GREEN+"\n Direccion / Address : "+c.WHITE+data["email"]+c.GREEN+"\n Contraseña / Password : "+c.WHITE+data["password"]+c.GREEN+"\n Id : "+c.WHITE+data["id"]+c.GREEN+"\n Token : "+c.WHITE+data["token"])
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