El siguiente diagrama detalla la arquitectura de las clases en el sistema usando el estándar UML:

```
classDiagram
    class Cliente {
        +id: int
        +nombre: str
        +email: str
        +telefono: str
        +direccion: str
        +__init__(...)
        +to_dict() dict
        +mostrar_info() str
    }

    class ClienteRegular {
        +descuento: float = 0.0
        +__init__(...)
        +to_dict() dict
        +mostrar_info() str
    }

    class ClientePremium {
        +nivel_membresia: str
        +__init__(...)
        +to_dict() dict
        +mostrar_info() str
    }

    class ClienteCorporativo {
        +nombre_empresa: str
        +rut: str
        +__init__(...)
        +to_dict() dict
        +mostrar_info() str
    }

    class GestorClientes {
        -db_path: str
        -conexion
        +agregar_cliente(c: Cliente)
        +leer_cliente(id) Cliente
        +actualizar_cliente(c: Cliente)
        +eliminar_cliente(id)
        +exportar_json()
        +exportar_csv()
        +validar_identidad_api()
        +enviar_email_bienvenida()
    }

    Cliente <|-- ClienteRegular : Herencia
    Cliente <|-- ClientePremium : Herencia
    Cliente <|-- ClienteCorporativo : Herencia
    GestorClientes o-- Cliente : Agregación
```