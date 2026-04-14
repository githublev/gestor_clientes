from validaciones import validar_email, validar_telefono, validar_texto

class Cliente:
    """Clase base que representa un Cliente genérico en el sistema."""
    
    def __init__(self, id_cliente: int, nombre: str, email: str, telefono: str, direccion: str):
        validar_texto(nombre, "nombre")
        validar_email(email)
        validar_telefono(telefono)
        validar_texto(direccion, "dirección")
        
        # Encapsulamiento: Aunque se usan propiedades públicas, la validación garantiza la integridad.
        self.id_cliente = id_cliente
        self.nombre = nombre.strip()
        self.email = email.lower().strip()
        self.telefono = telefono.strip()
        self.direccion = direccion.strip()
        self.tipo = "Base"

    def to_dict(self):
        """Convierte los atributos del objeto a un diccionario (útil para JSON/DB)."""
        return {
            "id_cliente": self.id_cliente,
            "nombre": self.nombre,
            "email": self.email,
            "telefono": self.telefono,
            "direccion": self.direccion,
            "tipo": self.tipo
        }

    def mostrar_info(self):
        """Método polimórfico para mostrar información resumida del cliente."""
        return f"[{self.tipo}] {self.nombre} - {self.email} ({self.telefono})"

class ClienteRegular(Cliente):
    """Subclase para clientes regulares, sin beneficios especiales por ahora."""
    
    def __init__(self, id_cliente: int, nombre: str, email: str, telefono: str, direccion: str):
        super().__init__(id_cliente, nombre, email, telefono, direccion)
        self.tipo = "Regular"
        self.descuento = 0.0

    def to_dict(self):
        datos = super().to_dict()
        datos["descuento"] = self.descuento
        return datos

    def mostrar_info(self):
        return super().mostrar_info() + f" - Descuento: {self.descuento}%"

class ClientePremium(Cliente):
    """Subclase para clientes premium, con un nivel de membresía y beneficios."""
    
    def __init__(self, id_cliente: int, nombre: str, email: str, telefono: str, direccion: str, nivel_membresia: str = "Oro"):
        super().__init__(id_cliente, nombre, email, telefono, direccion)
        validar_texto(nivel_membresia, "nivel_membresia")
        self.tipo = "Premium"
        self.nivel_membresia = nivel_membresia

    def to_dict(self):
        datos = super().to_dict()
        datos["nivel_membresia"] = self.nivel_membresia
        return datos

    def mostrar_info(self):
        return super().mostrar_info() + f" - Membresía: {self.nivel_membresia}"

class ClienteCorporativo(Cliente):
    """Subclase para clientes que representan empresas."""
    
    def __init__(self, id_cliente: int, nombre: str, email: str, telefono: str, direccion: str, nombre_empresa: str, rut: str):
        super().__init__(id_cliente, nombre, email, telefono, direccion)
        validar_texto(nombre_empresa, "nombre_empresa")
        validar_texto(rut, "rut")
        self.tipo = "Corporativo"
        self.nombre_empresa = nombre_empresa
        self.rut = rut

    def to_dict(self):
        datos = super().to_dict()
        datos["nombre_empresa"] = self.nombre_empresa
        datos["rut"] = self.rut
        return datos

    def mostrar_info(self):
        return f"[{self.tipo}] {self.nombre_empresa} ({self.rut}) - Contacto: {self.nombre} | {self.email}"
