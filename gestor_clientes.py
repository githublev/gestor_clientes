import sqlite3
import json
import csv
import logging
import time
from contextlib import closing
from tipos_cliente import Cliente, ClienteRegular, ClientePremium, ClienteCorporativo
from validaciones import ClienteNotFoundError

# Configuración básica del sistema de logs
logging.basicConfig(
    filename='sistema.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

class GestorClientes:
    """Clase principal que gestiona el CRUD de clientes, la conexión a BD y exportaciones."""

    def __init__(self, db_path="clientes.db"):
        self.db_path = db_path
        self.__crear_tabla()

    def __crear_tabla(self):
        """Método privado que inicializa la base de datos y la tabla si no existen."""
        try:
            with closing(sqlite3.connect(self.db_path)) as conexion:
                with conexion:
                    cursor = conexion.cursor()
                    cursor.execute('''
                        CREATE TABLE IF NOT EXISTS clientes (
                            id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
                            nombre TEXT NOT NULL,
                            email TEXT UNIQUE NOT NULL,
                            telefono TEXT NOT NULL,
                            direccion TEXT NOT NULL,
                            tipo TEXT NOT NULL,
                            datos_extra TEXT
                        )
                    ''')
            logging.info("Tabla de clientes inicializada correctamente en BD.")
        except sqlite3.Error as e:
            logging.error(f"Error al inicializar la base de datos: {e}")
            raise e

    def _instanciar_cliente(self, fila) -> Cliente:
        """Convierte una fila de la BD (tupla) en el objeto Cliente correspondiente."""
        id_cli, nom, ema, tel, dir, tipo, datos_extra_json = fila
        datos_extra = json.loads(datos_extra_json) if datos_extra_json else {}

        if tipo == "Regular":
            c = ClienteRegular(id_cli, nom, ema, tel, dir)
            c.descuento = datos_extra.get("descuento", 0.0)
            return c
        elif tipo == "Premium":
            return ClientePremium(id_cli, nom, ema, tel, dir, datos_extra.get("nivel_membresia", "Oro"))
        elif tipo == "Corporativo":
            return ClienteCorporativo(id_cli, nom, ema, tel, dir, datos_extra.get("nombre_empresa", ""), datos_extra.get("rut", ""))
        else:
            return Cliente(id_cli, nom, ema, tel, dir)

    def agregar_cliente(self, cliente: Cliente) -> int:
        """Inserta un nuevo cliente en la BD y retorna su ID asignado."""
        datos_dict = cliente.to_dict()
        tipo = datos_dict.pop("tipo")
        
        # Filtrar atributos base
        base_keys = ["id_cliente", "nombre", "email", "telefono", "direccion"]
        datos_extra = {k: v for k, v in datos_dict.items() if k not in base_keys}

        try:
            with closing(sqlite3.connect(self.db_path)) as conexion:
                with conexion:
                    cursor = conexion.cursor()
                    cursor.execute('''
                        INSERT INTO clientes (nombre, email, telefono, direccion, tipo, datos_extra)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (cliente.nombre, cliente.email, cliente.telefono, cliente.direccion, tipo, json.dumps(datos_extra)))
                    cliente.id_cliente = cursor.lastrowid
            logging.info(f"Cliente '{cliente.nombre}' agregado con ID {cliente.id_cliente}.")
            return cliente.id_cliente
        except sqlite3.IntegrityError:
            logging.warning(f"Intento de ingreso de email duplicado: {cliente.email}")
            raise ValueError("El correo electrónico ya existe en el sistema.")
        except Exception as e:
            logging.error(f"Error al agregar cliente: {e}")
            raise e

    def obtener_clientes(self) -> list:
        """Obtiene una lista con todos los objetos de clientes."""
        clientes = []
        try:
            with closing(sqlite3.connect(self.db_path)) as conexion:
                cursor = conexion.cursor()
                cursor.execute('SELECT * FROM clientes ORDER BY nombre ASC')
                filas = cursor.fetchall()
                for fila in filas:
                    clientes.append(self._instanciar_cliente(fila))
            return clientes
        except Exception as e:
            logging.error(f"Error al obtener clientes: {e}")
            return []

    def actualizar_cliente(self, cliente: Cliente):
        """Actualiza la información de un cliente existente en la BD."""
        datos_dict = cliente.to_dict()
        tipo = datos_dict.pop("tipo")
        
        base_keys = ["id_cliente", "nombre", "email", "telefono", "direccion"]
        datos_extra = {k: v for k, v in datos_dict.items() if k not in base_keys}

        try:
            with closing(sqlite3.connect(self.db_path)) as conexion:
                with conexion:
                    cursor = conexion.cursor()
                    cursor.execute('''
                        UPDATE clientes 
                        SET nombre = ?, email = ?, telefono = ?, direccion = ?, tipo = ?, datos_extra = ?
                        WHERE id_cliente = ?
                    ''', (cliente.nombre, cliente.email, cliente.telefono, cliente.direccion, tipo, json.dumps(datos_extra), cliente.id_cliente))
                    
                    if cursor.rowcount == 0:
                        logging.warning(f"Intento de actualizar un cliente que no existe (ID: {cliente.id_cliente})")
                        raise ClienteNotFoundError(f"No se encontró el cliente con ID {cliente.id_cliente}")
            logging.info(f"Cliente con ID {cliente.id_cliente} actualizado exitosamente.")
        except Exception as e:
            logging.error(f"Error en actualizar_cliente para ID {cliente.id_cliente}: {e}")
            raise e

    def eliminar_cliente(self, id_cliente: int):
        """Elimina un cliente de la BD."""
        try:
            with closing(sqlite3.connect(self.db_path)) as conexion:
                with conexion:
                    cursor = conexion.cursor()
                    cursor.execute('DELETE FROM clientes WHERE id_cliente = ?', (id_cliente,))
                    if cursor.rowcount == 0:
                        raise ClienteNotFoundError(f"No se encontró el cliente con ID {id_cliente} para eliminar.")
            logging.info(f"Cliente con ID {id_cliente} eliminado.")
        except Exception as e:
            logging.error(f"Error al eliminar cliente ID {id_cliente}: {e}")
            raise e

    def exportar_json(self, ruta="clientes.json"):
        """Exporta la base de datos a un archivo JSON."""
        clientes = self.obtener_clientes()
        datos = [c.to_dict() for c in clientes]
        try:
            with open(ruta, 'w', encoding='utf-8') as archivo:
                json.dump(datos, archivo, indent=4, ensure_ascii=False)
            logging.info(f"Base de datos exportada a {ruta} correctamente.")
            return True
        except Exception as e:
            logging.error(f"Falla al exportar JSON: {e}")
            return False

    def exportar_csv(self, ruta="clientes.csv"):
        """Exporta la base de datos a un archivo CSV."""
        clientes = self.obtener_clientes()
        if not clientes:
            logging.warning("No hay datos para exportar a CSV.")
            return False
        
        # Unificamos todas las claves posibles
        campos = set()
        para_exportar = []
        for c in clientes:
            d = c.to_dict()
            campos.update(d.keys())
            para_exportar.append(d)
        
        try:
            with open(ruta, mode='w', encoding='utf-8', newline='') as archivo_csv:
                writer = csv.DictWriter(archivo_csv, fieldnames=list(campos))
                writer.writeheader()
                writer.writerows(para_exportar)
            logging.info(f"Base de datos exportada a {ruta} correctamente.")
            return True
        except Exception as e:
            logging.error(f"Falla al exportar CSV: {e}")
            return False

    def validar_identidad_api(self, cliente: Cliente) -> bool:
        """Simula una llamada a API externa para validar identidad."""
        logging.info(f"Iniciando validación de identidad en API externa para {cliente.email}...")
        time.sleep(0.1) # Simular latencia de red reducida en tests
        if "@" in cliente.email:
            logging.info(f"Identidad validada exitosamente para {cliente.nombre}.")
            return True
        return False

    def enviar_email_bienvenida(self, cliente: Cliente) -> bool:
        """Simula el envío de un correo de bienvenida."""
        logging.info(f"Conectando al servidor SMTP para enviar bienvenida a {cliente.email}...")
        time.sleep(0.1)
        logging.info(f"Email enviado con éxito a {cliente.email}.")
        return True
