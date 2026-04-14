import re

class EmailInvalidoError(Exception):
    """Excepción lanzada cuando el correo electrónico no tiene un formato válido."""
    pass

class TelefonoInvalidoError(Exception):
    """Excepción lanzada cuando el teléfono no tiene un formato válido."""
    pass

class ClienteNotFoundError(Exception):
    """Excepción lanzada cuando no se encuentra un cliente en el sistema."""
    pass

def validar_email(email: str) -> bool:
    """Valida que un correo electrónico tenga un formato estándar."""
    patron = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if not re.match(patron, email):
        raise EmailInvalidoError(f"El email '{email}' es inválido.")
    return True

def validar_telefono(telefono: str) -> bool:
    """Valida que un teléfono contenga solo números y un largo aceptable (ej. 8 a 15)."""
    # Permitir opcionalmente '+' al inicio y espacios
    t_limpio = telefono.replace(" ", "")
    patron = r'^\+?[0-9]{8,15}$'
    if not re.match(patron, t_limpio):
        raise TelefonoInvalidoError(f"El teléfono '{telefono}' no es válido. Debe contener entre 8 y 15 dígitos.")
    return True

def validar_texto(texto: str, campo: str) -> bool:
    """Valida que un campo de texto no esté vacío."""
    if not texto or not texto.strip():
        raise ValueError(f"El campo {campo} no puede estar vacío.")
    return True
