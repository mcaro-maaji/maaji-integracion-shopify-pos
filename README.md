# Maaji Integracion Shopify POS

## Instalación y requisitos
1. La instalación es con el siguiente comando:

```sh
pip install git+https://github.com/mcaro-maaji/maaji-integracion-shopify-pos.git
```

2. Establecer las variables de entorno en el archivo **.env** usando como base **.env.example**.

3. La variable de entorno **WORKING_DIR_MAAJI_INTEGRACION_SHOPIFY_POS**
será la ruta en donde se almacena todos los datos incluido el archivo .env, configuración.json, etc.

3. En el archivo de configuración se debe establecer la siguiente configuración previa antes de la ejecición:

*configuracion.json*

```json
"webdriver": {
    "name_webdriver": "chrome" // Nombre del navegador según el que se vaya a utilizar.
    "options": {
        "add_arguments": [
            "--window-size=1024,800", // Esto es para abrir la ventana del navegador. (Solo pruebas)
            "--handless", // Esto impide que se abra la ventana del navegador.
            "--log-level-3" // Retirar los logs
        ]
    }
}
```

### Obtener el navegador de Chrome para linux (Recomendado)

```sh
# Descargar el paquete .deb
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb

# Instalar el paquete descargado
sudo dpkg -i google-chrome-stable_current_amd64.deb

# Resolver dependencias si es necesario
sudo apt --fix-broken install

# Un solo comando:
sudo apt update && sudo apt install wget -y && wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && sudo dpkg -i google-chrome-stable_current_amd64.deb && sudo apt --fix-broken install -y
```

### Ejecución servicio de ordenes de compra en stocky

```sh
maaji-integracion-shopify-pos run purchase-orders --store=maaji_co_test --env=uat --date=02/08/2024
