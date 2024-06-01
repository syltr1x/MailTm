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
    data = json.loads(r.text)
    if 201 == r.status_code: print(c.GREEN+"[+] Acount Created"+c.WHITE)
    else: 
        if 400 == r.status_code: print(c.RED+"[-] Err: Invalid values"+c.WHITE)
        elif 422 == r.status_code: print(c.RED+"[-] Err: Account existent"+c.WHITE)
        else: print(c.RED+"[-] Err: Unknow. Code Err : "+r+c.WHITE)

def get_token(email, password):
    url = "https://api.mail.gw/token"
    payload = {
        "address": email,
        "password": password
    }
    headers = { 'Content-Type': 'application/json' }
    r = requests.post(url, headers=headers, json=payload)
    data = json.loads(r.text)
    if 200 in r.status_code: return data['token']
    else: print(c.RED+"[-] Err : Unknow. Code Err : "+r+c.WHITE) 

def delete_account(id, token):
    header = {"authorization":f"Bearer {token}"}
    r = requests.delete(f"https://api.mail.gw/accounts/{id}", headers=header)
    if r.status_code == 204 : print(c.GREEN+"[+] Account Deleted"+c.WHITE)
    elif r.status_code == 404: print(c.RED+"[-] Err : Cuenta inexistente."+c.WHITE)
    else: print(c.RED+"[-] Err : Unknow code Err : "+r+c.WHITE)

def show_msg(token):
    header = {"authorization":f"Bearer {token}"}
    r = requests.get("https://api.mail.gw/messages", headers=header)
    mail_sayisi = r.text
    mail_sayisi = json.loads(mail_sayisi)
    if str(mail_sayisi["hydra:member"]) != "[]":
        id = mail_sayisi["hydra:member"][0]["id"]
        r  = requests.get(f"https://api.mail.gw/messages/{id}", headers=header)
        mail = json.loads(r.text)
        
        mailS = mail["from"]["address"]
        title = mail["subject"]
        content = mail["text"]

        return mail