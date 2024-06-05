from colorama import init, Fore as c
import time as tm
import requests
import json 
init()

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

def add_account(email, password):
    url = "https://api.mail.gw/accounts"
    payload = {
        "address": email,
        "password": password
    }
    headers = { 'Content-Type': 'application/json' }
    r = requests.post(url, headers=headers, json=payload)
    if 201 == r.status_code: "[+] Account Created"
    elif 400 == r.status_code: "[-] Err: Invalid values"
    elif 422 == r.status_code: "[-] Err: Account already exist"
    else: return r.status_code

def delete_account(id, token):
    header = {"authorization":f"Bearer {token}"}
    r = requests.delete(f"https://api.mail.gw/accounts/{id}", headers=header)
    if r.status_code == 204 : print(c.GREEN+"[+] Account Deleted"+c.WHITE)
    elif r.status_code == 404: print(c.RED+"[-] Err : Cuenta inexistente."+c.WHITE)
    else: print(c.RED+"[-] Err : Unknow code Err : "+r+c.WHITE)

def show_msg(token):
    header = {"authorization":f"Bearer {token}"}
    r = requests.get("https://api.mail.gw/messages", headers=header)
    mail_sayisi = json.loads(r.text)
    if mail_sayisi["hydra:member"] != []:
        out_mails = []
        mails = mail_sayisi["hydra:member"]
        for m in mails:
            id = m["id"]
            r  = requests.get(f"https://api.mail.gw/messages/{id}", headers=header)
            mail = json.loads(r.text)
        
            from_addr = mail["from"]["address"]
            subject = mail["subject"]
            date = mail["createdAt"].split("+")[0].replace("-", "/").replace("T","  ")
            content = mail["text"]

            ## Fix Time 
            times = date.split(" ")[2].split(':')
            local_tmz_offset = -tm.timezone if tm.localtime().tm_isdst == 0 else -tm.altzone
            hour = str(int(times[0])+local_tmz_offset/3600)[:-2]
            date = f"{date.split(" ")[0]} {hour}:{times[1]}:{times[2]}"

            out_mails.append({"from":from_addr, "subject":subject, "date":date, "content": content})
    return out_mails