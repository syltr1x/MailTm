import time as tm
import requests
import json 
import os

def get_domains():
    url = "https://api.mail.gw/domains"
    r = requests.get(url)
    if r.status_code == 200:
        data = json.loads(r.text)["hydra:member"]
        return [i["domain"] for i in data]
    else: return []

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

def get_accounts(file):
    if not os.path.exists(f'{file}.json'): return []
    accFile = open(f'{file}.json', 'r')
    accData = accFile.read()
    accData = accData[:-1][1:].replace('},', '}},').split('},') if len(accData) > 3 else []
    accFile.close()
    accData = [acc for acc in accData if len(acc) > 5]
    return accData

def add_account(email, password):
    url = "https://api.mail.gw/accounts"
    payload = {
        "address": email,
        "password": password
    }
    headers = { 'Content-Type': 'application/json' }
    r = requests.post(url, headers=headers, json=payload)
    if 201 == r.status_code: return "[+] Account Created"
    elif 400 == r.status_code: return "[-] Err: Invalid values"
    elif 422 == r.status_code: return "[-] Err: Account already exist"
    else: return r.status_code

def write_account(email, password, token=None, id=None, file="acc_info"):
    if token == None: get_token(email, password)
    if id == None: get_id(token)
    accData = get_accounts(f"{file}.json")
    accFile = open(f'{file}.json', 'w')
    accFile.write('[')
    for acc in accData:
        accItem = json.loads(acc)
        if accData.index(acc) < len(accData)-1: accFile.write('\n    {\n        "email":"'+accItem["email"]+'",\n        "password":"'+accItem["password"]+'",\n        "id":"'+accItem["id"]+'",\n        "token":"'+accItem["token"]+'"\n    },')
        else: accFile.write('\n    {\n        "email":"'+accItem["email"]+'",\n        "password":"'+accItem["password"]+'",\n        "id":"'+accItem["id"]+'",\n        "token":"'+accItem["token"]+'"\n    }\n]')
    accFile.close()

def delete_account(email=None, password=None, token=None, id=None):
    if token == None: token = get_token(email, password)
    if id == None: id = get_id(token)
    header = {"authorization":f"Bearer {token}"}
    r = requests.delete(f"https://api.mail.gw/accounts/{id}", headers=header)
    if r.status_code == 204 : return "[+] Account Deleted"
    elif r.status_code == 404: return "[-] Err: Inexistent Account."
    else: return r.status_code

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