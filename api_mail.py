from colorama import init, Fore as c
import requests
import json
init()

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
    r = str(r)
    print("------------------------------")
    if "201" in r: print(c.GREEN+"[+] Acount Created"+c.WHITE)
    else: 
        if "400" in r: print(c.RED+"[-] Err: Invalid values"+c.WHITE)
        elif "422" in r: print(c.RED+"[-] Err: Account existent"+c.WHITE)
        else: print(c.RED+"[-] Err: Unknow. Code Err : "+r+c.WHITE)

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
    r = str(r)
    if "200" in r.text: return data['token']
    else: print(c.RED+"[-] Err : Unknow. Code Err : "+r+c.WHITE) 

def delete_account(id, token):
    header = {"authorization":f"Bearer {token}"}
    r = requests.delete(f"https://api.mail.gw/accounts/{id}", headers=header)
    r = str(r)
    if "204" in r: print(c.GREEN+"[+] Account Deleted"+c.WHITE)
    else: 
        if "404" in r: print(c.RED+"[-] Err : Cuenta inexistente."+c.WHITE)
        else: print(c.RED+"[-] Err : Unknow. Code Err : "+r+c.WHITE)

def show_msg(token):
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