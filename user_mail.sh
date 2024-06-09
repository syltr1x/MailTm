#!/usr/bin/bash

#Colours
green="\e[0;32m\033[1m"
end="\033[0m\e[0m"
red="\e[0;31m\033[1m"
blue="\e[0;34m\033[1m"
yellow="\e[0;33m\033[1m"
purple="\e[0;35m\033[1m"
turquoise="\e[0;36m\033[1m"
gray="\e[0;37m\033[1m"

# Functions

get_domains() {
	domains=()
	response=$(curl -X GET "https://api.mail.gw/domains")
	if [ $? -eq 0 ]; then
		domains=$(echo "$response" | jq -r '."hydra:member"[] | .domain')
	fi
	echo "$domains"
}

get_address() {
	addresses=()
	echo "$addresses"
}

get_token() {
	header="Content-Type: application/json"
	payload="{\"address\":\"$1\",\"password\":\"$2\"}"
	response=$(curl -X GET -H "$header" -d "$payload" "https://api.mail.gw/token")
	if [ $? -eq 0 ]; then
		token=$(echo "$response" | jq -r '.token')
	else
		token="empty"
	fi
	echo "$token"
}

get_id() {
	header="Authorization: Bearer $1"
	payload="{\"token\":\"$id\"}"
	response=$(curl -X GET -H "$header" -d "$payload" "https://api.mail.gw/me")
	if [ $? -eq 0 ]; then
		id=$(echo "$response" | jq -r '.id')
	else
		id="empty"
	fi
	echo "$id"
}

get_accounts() {
	accounts=()
	if [ ! -f "acc_info.json" ]; then
		echo "$accounts"
	else
		echo "ERROR"
	fi
}
write_account() {
	echo "Guardando $1 $2"
}

add_account() {
    echo -e "[0] Atras\n[1] Iniciar sesión  [2] Crear cuenta"
	echo -n ">>"; read option
	if [ $option -eq "0" ]; then
		return 0
	elif [ $option -eq "1" ]; then
		echo "Address (include domain) >> "; read email
		echo "Password >> "; read password
		token=$(get_token "$email" "$password")
		id=$(get_id "$token")
		if [ $token -ne "empty" ] && [ $id -ne "empty" ]; then
			$(write_account "$email" "$password" "$token" "$id")
		else
			echo -e "[*] La cuenta no existe, se creara una..."
			$(create_account"$email" "$password")
			echo -e "${green}[+] ${end}Cuenta creada con exito. Almacenando datos..."
			$(write_account "$email" "$password")
			echo -e "${green}[+] ${end}Cuenta almacenada con exito. Puedes continuar :)"
		fi
	fi
}

show_accounts() {
    echo "Mirando cuentas"
}

show_msg() {
    echo "Mirando mensajes"
}

delete_account() {
    echo "Borrando"
}

while true; do
    clear
    echo -e "${red}[0] ${end}Salir\n${yellow}[1] ${end}Agregar Cuenta     ${yellow}[2] ${end}Mostrar cuenta\n${yellow}[3] ${end}Mostrar mensajes   ${yellow}[4] ${end}Eliminar cuenta"
    echo -n ">>"; read action
    if [ $action -eq "0" ]; then
        exit 0
    elif [ $action -eq "1" ]; then
        add_account
    elif [ $action -eq "2" ]; then
        show_accounts
    elif [ $action -eq "3" ]; then
        show_msg
    elif [ $action -eq "4" ]; then
        delete_account
    else
        echo -e "[!] Err: Valor inesperado"
    fi
done
