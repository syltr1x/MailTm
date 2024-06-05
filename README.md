### 📄 Documentation for use "api_mail.py"

> ### **Add an Account:** `add_account(email, password)`
Create an account in server using address and password passed. 

> ### **Save an Account:** `write_account(email, password, token=None, id=None, file="acc_info")`
Save account in a JSON file, store address, password, token and id. If two last aren't passed
the function call `get_token` and `get_id`. If you try write inexistent account return error because can't obtain valid token and id

> ### **Delete an Account:** `delete_account(email=None, password=None, token=None)`
Need token for delete account from server, if this isn't passed, the function require email and password
for call `get_token`

> ### **show_msg** `show_msg(email, password)`
Return a list of messages of account. EX:

    [{"from":"user1@gmail.com", "subject":"IMPORTANT MEET",
    "date", "DD/MM/YYYY hh:mm:ss", "content":"bla bla bla"}]

#

> ### **Get Domains avaibles:** `get_domains()` 🆕
Return a list of domains admited for create an account

> ### **Get Token of Existing account:** `get_token(email, password)`
Return token of account

> ### **Get ID of Existing account:** `get_id(token)`
Return ID of account