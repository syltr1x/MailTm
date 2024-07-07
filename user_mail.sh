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
	response=$(curl -sX GET "https://api.mail.gw/domains")
	if [ $? -eq 0 ]; then
		domains=$(echo "$response" | jq -r '."hydra:member"[] | .domain')
	fi
	echo "$domains" > addresses.txt
}

get_address() {
  if [ ! -f 'addresses.txt' ]; then
    get_domains 
  fi
	if [ $1 == "random" ]; then
		echo $(cat addresses.txt | shuf -n 1)
	elif [ $1 == "all" ]; then
    awk 'NR > 0' addresses.txt
	fi
}

get_token() {
  if [ $# -lt 2 ]; then
    echo "[!] Err: Missed parameter. Ex: get_token $email $address"
    return 0
  fi
	header="Content-Type: application/json"
	payload="{\"address\":\"$1\",\"password\":\"$2\"}"
	response=$(curl -sX POST -H "$header" -d "$payload" "https://api.mail.gw/token")
	if [ $? -eq 0 ]; then
		token=$(echo "$response" | jq -r '.token')
	else
		token="empty"
	fi
	echo "$token"
}

get_id() {
  if [ $# -lt 1 ]; then
    echo "[!] Err: Missed parameter. Ex: get_id $token"
  fi
	header="Authorization: Bearer $1"
	payload="{\"token\":\"$1\"}"
	response=$(curl -sX GET -H "$header" -d "$payload" "https://api.mail.gw/me")
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
    accounts=$(jq -r '.[].email' acc_info.json | wc)
		if [ $1 == "len" ]; then
			echo "${#accounts[@]}"
		else
			echo "${accounts[@]}"
		fi
	fi
}
write_account() {
  if [ $# -lt 2 ]; then
    echo "[!] Err: Missed essential paramaters. Ex: write_account $email $password or write_account $email $password $token $id"
  fi
	local email="$1"
	local password="$2"
	local token="${3:-empty}"
	local id="${4:-empty}"
	if [ $token == "empty" ]; then
		token=$(get_token "$email" "$password")
	fi
	if [ $id == "empty" ]; then
		id=$(get_id "$token")
	fi

	if [ ! -f "acc_info.json" ]; then
		accounts=()
	else
		# Lee el fichero y almacena cada mapa dentro de un array
		while IFS= read -r -d '' map; do
			accounts+=( "$map" )
		done < <(jq -c '.[]' acc_info.json)
  fi
		# Crear y añadir mapa de la nueva cuenta al array
		account="{\"email\":\"$email\",\"password\":\"$password\",\"id\":\"$id\",\"token\":\"$token\"}"
		accounts+=("$account")
		# Escribir los cambios en el fichero
		echo "[" > acc_info.json
		for acc in "${accounts[@]}"; do
			echo "    $acc," >> acc_info.json
		done
		sed -i '$ s/,$//' acc_info.json
		echo "]" >> acc_info.json
}

create_account() {
	header="Content-Type: application/json"
	payload="{\"address\":\"$1\",\"password\":\"$2\"}"
	curl -sX POST -H "$header" -d "$payload" -w "%{http_code}" "https://api.mail.gw/accounts"
}

add_account() {
    echo -e "${red}[0] ${end}Atras\n${yellow}[1] ${end}Iniciar sesión  ${yellow}[2] ${end}Crear cuenta"
	echo -n ">>"; read option
	if [ $option -eq "0" ]; then
		return 0
	elif [ $option -eq "1" ]; then
		echo -n "Address (include domain) >> "; read email
		echo -n "Password >> "; read password
		token=$(get_token "$email" "$password")
		id=$(get_id "$token")
		if [ $token -ne "empty" ] && [ $id -ne "empty" ]; then
			$(write_account "$email" "$password" "$token" "$id")
		else
			echo -e "[*] La cuenta no existe, se creara una..."
			$(create_account "$email" "$password")
			echo -e "${green}[+] ${end}Cuenta creada con exito. Almacenando datos..."
			$(write_account "$email" "$password")
			echo -e "${green}[+] ${end}Cuenta almacenada con exito. Puedes continuar :)"
		fi
	elif [ $option -eq "2" ]; then
		echo -n "Address (not include domain) >> "; read email
		echo -n "Password >> "; read password
		domain=$(get_address "random")
		$(create_account "$email$domain" "$password")
		$(write_account "$email" "$password")
	else
		echo -e "${red}[-] Err: ${end}Entrada no valida. Porfavor reintentalo."
	fi
}

show_accounts() {
	accounts=$(get_accounts)
    echo accounts 
	read asa 
}

show_msg() {
    echo "Mirando mensajes"
}

delete_account() {
  accs=$(get_accounts "len")
  if [ $accs -lt 2 ]; then
    address=$(jq -r '.[].email' acc_info.json)
    echo -ne "[?] Are you sure to delete account: $address [Y/n] >> "; read confirm
    if [[ ! $confirm =~ ^[Nn]$ ]]; then
      password=$(jq -r '.[] | "\(.email) \(.password)"' acc_info.json | awk '{ print $2 }')
      token=$(get_token $address $password) 
      id=$(get_id $token)
	    header="Authorization: Bearer $token"
      curl -sX DELETE -H "$header" "https://api.mail.gw/accounts/$id"

      # Delete email line in "acc_info.json"
      sed -i '/"email":"'"$address"'"/d' acc_info.json
    else
      echo "[*] Account isn't deleted"
    fi  
  fi
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
