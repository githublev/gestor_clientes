import unittest
import os
from tipos_cliente import ClienteRegular, ClientePremium
from validaciones import EmailInvalidoError, TelefonoInvalidoError
from gestor_clientes import GestorClientes

class TestSistemaClientes(unittest.TestCase):

    def setUp(self):
        """Prepara el entorno de pruebas creando un gestor con base de datos temporal."""
        self.db_test = "test_clientes.db"
        if os.path.exists(self.db_test):
            os.remove(self.db_test)
        self.gestor = GestorClientes(self.db_test)
    
    def tearDown(self):
        """Limpia el entorno al terminar."""
        if os.path.exists(self.db_test):
            os.remove(self.db_test)

    def test_validar_email_correcto(self):
        """Verifica que la instanciación funcione con un correo correcto."""
        c = ClienteRegular(0, "Juan Test", "test@example.com", "+56912345678", "Calle 1")
        self.assertEqual(c.email, "test@example.com")

    def test_validar_email_incorrecto(self):
        """Verifica que atrape un email con formato inválido."""
        with self.assertRaises(EmailInvalidoError):
            ClienteRegular(0, "Juan", "correo-sin-arroba", "12345678", "Dir 1")

    def test_validar_telefono_incorrecto(self):
        """Verifica que atrape un teléfono con letras o muy corto."""
        with self.assertRaises(TelefonoInvalidoError):
            ClienteRegular(0, "Juan", "test@test.com", "abc", "Dir 1")

    def test_agregar_cliente_bd(self):
        """Verifica la incersión en la base de datos de SQLite."""
        c = ClienteRegular(0, "Maria Test", "maria@ejemplo.com", "987654321", "Av Test")
        id_asignado = self.gestor.agregar_cliente(c)
        self.assertGreater(id_asignado, 0)
        
        # Recuperar y comprobar
        clientes = self.gestor.obtener_clientes()
        self.assertEqual(len(clientes), 1)
        self.assertEqual(clientes[0].nombre, "Maria Test")

    def test_polimorfismo_instancias(self):
        """Verifica que al recuperar desde SQlite devuelva la subclase correspondiente."""
        c = ClientePremium(0, "Pedro", "pedro@test.com", "12345678", "Dir", "Plata")
        self.gestor.agregar_cliente(c)
        clientes = self.gestor.obtener_clientes()
        self.assertIsInstance(clientes[0], ClientePremium)
        self.assertEqual(clientes[0].nivel_membresia, "Plata")

if __name__ == '__main__':
    unittest.main()
