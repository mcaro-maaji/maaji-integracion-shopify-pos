"""
Modulo que ejecuta tareas de Distribución Continua o CD en producción.
Es util a la hora de realizar cambios en archivos o ejecutar comandos post-despliegue del proyecto.
"""

from maaji_integracion_shopify_pos.config import Configuration
from maaji_integracion_shopify_pos.fieldsmapping import FieldMapping

Configuration.purchase_orders.default_supplier_name_like = "ART MODE"
Configuration.save_file()
FieldMapping.remove_file()
