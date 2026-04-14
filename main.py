import tkinter as tk
from tkinter import ttk, messagebox
import logging

from tipos_cliente import ClienteRegular, ClientePremium, ClienteCorporativo
from gestor_clientes import GestorClientes
from validaciones import EmailInvalidoError, TelefonoInvalidoError, ClienteNotFoundError

class APP_GIC:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestor Inteligente de Clientes (GIC)")
        self.root.geometry("850x650")
        self.gestor = GestorClientes()
        
        self.crear_widgets()
        self.refrescar_tabla()

    def crear_widgets(self):
        # Frame Formulario
        f_form = ttk.LabelFrame(self.root, text="Datos del Cliente")
        f_form.pack(fill="x", padx=10, pady=10)

        # Campos Base
        ttk.Label(f_form, text="Nombre:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.e_nombre = ttk.Entry(f_form, width=30)
        self.e_nombre.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(f_form, text="Email:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.e_email = ttk.Entry(f_form, width=30)
        self.e_email.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(f_form, text="Teléfono:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.e_tel = ttk.Entry(f_form, width=30)
        self.e_tel.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(f_form, text="Dirección:").grid(row=1, column=2, padx=5, pady=5, sticky="e")
        self.e_dir = ttk.Entry(f_form, width=30)
        self.e_dir.grid(row=1, column=3, padx=5, pady=5)

        # Tipo Cliente
        ttk.Label(f_form, text="Tipo:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.cb_tipo = ttk.Combobox(f_form, values=["Regular", "Premium", "Corporativo"], state="readonly")
        self.cb_tipo.current(0)
        self.cb_tipo.grid(row=2, column=1, padx=5, pady=5)
        self.cb_tipo.bind("<<ComboboxSelected>>", self.on_tipo_change)

        # Campos Dinámicos
        self.lbl_extra1 = ttk.Label(f_form, text="Descuento (%):")
        self.lbl_extra1.grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.e_extra1 = ttk.Entry(f_form, width=30)
        self.e_extra1.grid(row=3, column=1, padx=5, pady=5)

        self.lbl_extra2 = ttk.Label(f_form, text="")
        self.lbl_extra2.grid(row=3, column=2, padx=5, pady=5, sticky="e")
        self.e_extra2 = ttk.Entry(f_form, width=30)
        self.e_extra2.grid(row=3, column=3, padx=5, pady=5)
        self.e_extra2.grid_remove()  # Oculto por defecto

        # Botones de Acción
        f_btns = ttk.Frame(self.root)
        f_btns.pack(fill="x", padx=10, pady=5)

        ttk.Button(f_btns, text="Agregar Cliente", command=self.agregar_cliente).pack(side="left", padx=5)
        ttk.Button(f_btns, text="Eliminar Seleccionado", command=self.eliminar_cliente).pack(side="left", padx=5)
        ttk.Button(f_btns, text="Exportar JSON", command=self.exportar_json).pack(side="left", padx=5)
        ttk.Button(f_btns, text="Exportar CSV", command=self.exportar_csv).pack(side="left", padx=5)

        # Frame Tabla
        f_tabla = ttk.Frame(self.root)
        f_tabla.pack(fill="both", expand=True, padx=10, pady=10)

        cols = ("ID", "Nombre", "Email", "Teléfono", "Tipo", "Info Extra")
        self.tree = ttk.Treeview(f_tabla, columns=cols, show="headings")
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=120)
        
        self.tree.pack(fill="both", expand=True, side="left")
        
        scroll = ttk.Scrollbar(f_tabla, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")

    def on_tipo_change(self, event):
        tipo = self.cb_tipo.get()
        self.e_extra1.delete(0, tk.END)
        self.e_extra2.delete(0, tk.END)
        
        if tipo == "Regular":
            self.lbl_extra1.config(text="Descuento (%):")
            self.e_extra2.grid_remove()
            self.lbl_extra2.config(text="")
        elif tipo == "Premium":
            self.lbl_extra1.config(text="Nivel Membresía:")
            self.e_extra2.grid_remove()
            self.lbl_extra2.config(text="")
        elif tipo == "Corporativo":
            self.lbl_extra1.config(text="Empresa:")
            self.lbl_extra2.config(text="RUT:")
            self.e_extra2.grid()

    def refrescar_tabla(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        clientes = self.gestor.obtener_clientes()
        for cli in clientes:
            info_str = cli.mostrar_info()
            self.tree.insert("", "end", values=(cli.id_cliente, cli.nombre, cli.email, cli.telefono, cli.tipo, info_str))

    def agregar_cliente(self):
        nom = self.e_nombre.get()
        ema = self.e_email.get()
        tel = self.e_tel.get()
        dir = self.e_dir.get()
        tipo = self.cb_tipo.get()
        ext1 = self.e_extra1.get()
        ext2 = self.e_extra2.get()

        try:
            # Polimorfismo / Creación de instancias
            if tipo == "Regular":
                cli = ClienteRegular(0, nom, ema, tel, dir)
                cli.descuento = float(ext1) if ext1 else 0.0
            elif tipo == "Premium":
                ext1 = ext1 if ext1 else "Plata"
                cli = ClientePremium(0, nom, ema, tel, dir, ext1)
            elif tipo == "Corporativo":
                cli = ClienteCorporativo(0, nom, ema, tel, dir, ext1, ext2)

            self.gestor.agregar_cliente(cli)
            
            # Integración con "API" simulada
            self.gestor.validar_identidad_api(cli)
            self.gestor.enviar_email_bienvenida(cli)

            messagebox.showinfo("Éxito", f"Cliente {nom} agregado correctamente.")
            self.refrescar_tabla()
            self.limpiar_form()
            
        except EmailInvalidoError as e:
            messagebox.showerror("Error de Email", str(e))
        except TelefonoInvalidoError as e:
            messagebox.showerror("Error de Teléfono", str(e))
        except ValueError as e:
            messagebox.showerror("Error de Valor", str(e))
        except Exception as e:
            logging.error(e)
            messagebox.showerror("Error Inesperado", f"Ocurrió un error: {e}")

    def eliminar_cliente(self):
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Aviso", "Seleccione un cliente para eliminar.")
            return
        
        item = self.tree.item(seleccion[0])
        id_cli = item['values'][0]
        
        if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar este cliente?"):
            try:
                self.gestor.eliminar_cliente(id_cli)
                self.refrescar_tabla()
                messagebox.showinfo("Éxito", "Cliente eliminado.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def exportar_json(self):
        if self.gestor.exportar_json():
            messagebox.showinfo("Exportar", "Datos exportados a clientes.json exitosamente.")
        else:
            messagebox.showerror("Error", "No se pudo exportar JSON.")

    def exportar_csv(self):
        if self.gestor.exportar_csv():
            messagebox.showinfo("Exportar", "Datos exportados a clientes.csv exitosamente.")
        else:
            messagebox.showerror("Error", "No se pudo exportar CSV.")

    def limpiar_form(self):
        self.e_nombre.delete(0, tk.END)
        self.e_email.delete(0, tk.END)
        self.e_tel.delete(0, tk.END)
        self.e_dir.delete(0, tk.END)
        self.e_extra1.delete(0, tk.END)
        self.e_extra2.delete(0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = APP_GIC(root)
    root.mainloop()
