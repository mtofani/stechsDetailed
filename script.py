import requests
import logging
import argparse
import json
from configparser import ConfigParser
from requests.auth import HTTPBasicAuth


# Deshabilita las advertencias de verificación SSL
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

# Lee la configuración desde el archivo config.ini
config = ConfigParser()
config.read('config.ini')

# Configuración del logger
logging.basicConfig(filename=config['Logging']['file_path'], level=config['Logging']['level'])

def check_service(url, user=None, pw=None, use_mock=False, mock_file_path=None, return_data=False):
    try:
        if use_mock:
            with open(mock_file_path, 'r') as mock_file:
                data = json.load(mock_file)
        else:
            auth = HTTPBasicAuth(user, pw)
            response = requests.get(url, auth=auth, verify=False)
            response.raise_for_status()
            data = response.json()

        logging.info(f"EL DATA: {data}")

        if return_data:
            return data

        # Procede con la lógica normal
        if data.get("items") and data["items"].get("status") == "OK" and all(item["value"] for item in data["items"]["statusData"]):
                result = 1
        else:
                result = 0

        logging.info(f"Respuesta {result} para la URL: {url}")
        return result

    except Exception as e:
        logging.error(f"Error en la solicitud para la URL {url}: {e}")
        return 0

def main():
    parser = argparse.ArgumentParser(description="Script para verificar un servicio web.")
    parser.add_argument("-data", action="store_true", help="Obtener la respuesta como una cadena")
    
    args = parser.parse_args()

    # Obtiene la configuración
    url, user, passw = config["Endpoints"]["stechDetailed"], config["Endpoints"]["username"], config["Endpoints"]["password"]
    archivo_mock = './mock.json'

    # Realiza la verificación del servicio
    resultado = check_service(url, user, passw, use_mock=True, mock_file_path=archivo_mock, return_data=args.data)
    
    # Imprime el resultado según la opción -data
    print(json.dumps(resultado, indent=2)) if args.data else print(resultado)

if __name__ == "__main__":
    main()
