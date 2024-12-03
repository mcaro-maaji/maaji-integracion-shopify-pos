# maaji-integracion-shopify-pos

# Instalación y requisitos
Con el siguiente comando:

pip install --editable git+https://github.com/mcaro-maaji/maaji-integracion-shopify-pos.git

Revisar las variables de entorno en el archivo .env.example

En el archivo de configuración se debe establecer la siguiente configuración previa antes de la ejecición:

*configuracion.json*

"webdriver": {
    "options": {
        "add_arguments": [
            "--window-size=1024,800", // Esto es para abrir la ventana del navegador.
            "--handless", // Esto impide que se abra la ventana del navegador.
            "--log-level-3" // Retirar los logs
        ]
    },
    "name_webdriver": "edge"
}

### Obtener el navegador de Chrome para linux (Recomendado)

- Descargar el paquete .deb
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb

- Instalar el paquete descargado
sudo dpkg -i google-chrome-stable_current_amd64.deb

- Resolver dependencias si es necesario
sudo apt --fix-broken install

- Un solo comando:
sudo apt update && sudo apt install wget -y && wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && sudo dpkg -i google-chrome-stable_current_amd64.deb && sudo apt --fix-broken install -y

