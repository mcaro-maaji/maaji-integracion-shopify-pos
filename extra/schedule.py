import subprocess
import time
import schedule

# HORAS DE EJECUCIÓN DE ORDENES DE COMPRA
## HORARIO AM
# 05/12/2024 07:00:00 - 14 horas -> date-start 04/12/2024 17:00:00
# 05/12/2024 07:00:00 + 5  horas -> date-end   05/12/2024 12:00:00
## HORARIO PM
# 05/12/2024 12:00:00 + 0  horas -> date-start 05/12/2024 12:00:00
# 05/12/2024 12:00:00 + 5  horas -> date-end   05/12/2024 17:00:00

# Se cuentan con 2 tareas para ejecutar para cada tienda, por horarios 7 AM y 12 PM, diariamente.

PROYECT_CURRENT_WORKING_DIR = "<path>"

def make_task_purchase_orders(*args: str):
    # Aquí colocas el código que deseas ejecutar periódicamente
    def task():
        print("Ejecutando tarea stocky ordenes de compra...")
        subprocess.call(["python3", "-m", "maaji_integracion_shopify_pos",
                        "run", "purchase-orders", *args], cwd=PROYECT_CURRENT_WORKING_DIR)
    return task

task_purchase_orders_maaji_pos_am = make_task_purchase_orders("--store", "maaji_pos",
                                                              "--env", "uat",
                                                              "--date-start", "0 days, -14",
                                                              "--date-end", "0 days, 5")

task_purchase_orders_maaji_pos_pm = make_task_purchase_orders("--store", "maaji_pos",
                                                              "--env", "uat",
                                                              "--date-start", "0 days, -5",
                                                              "--date-end", "0 days, 5")

task_purchase_orders_maaji_pos_outlet_am = make_task_purchase_orders("--store", "maaji_pos_outlet",
                                                                     "--env", "uat",
                                                                     "--date-start", "0 days, -14",
                                                                     "--date-end", "0 days, 5")

task_purchase_orders_maaji_pos_outlet_pm = make_task_purchase_orders("--store", "maaji_pos_outlet",
                                                                     "--env", "uat",
                                                                     "--date-start", "0 days, -5",
                                                                     "--date-end", "0 days, 5")

# Programar la ejecución de la tarea en un horario específico
# schedule.every().month.at("12:00").do(tarea)
schedule.every().day.at("07:00").do(task_purchase_orders_maaji_pos_am)
schedule.every().day.at("07:00").do(task_purchase_orders_maaji_pos_outlet_am)
schedule.every().day.at("12:00").do(task_purchase_orders_maaji_pos_pm)
schedule.every().day.at("12:00").do(task_purchase_orders_maaji_pos_outlet_pm)
# schedule.every().year.at("January 1 00:00").do(tarea)
# schedule.every().monday.at("15:45").do(tarea)
# schedule.every().minute.at(":30").do(tarea)

# Ejecutar la tarea de forma continua
while True:
    schedule.run_pending()
    time.sleep(1)
