"""Agenda Estudiantil en un solo archivo.

Incluye inicio de sesión, materias, horarios, tareas, exámenes, reportes y
guardado automático en JSON. Solo requiere Python 3.10 o superior.
"""

import hashlib
import json
import re
import tkinter as tk
from datetime import date
from pathlib import Path
from tkinter import messagebox, simpledialog, ttk
from tkinter.scrolledtext import ScrolledText
from uuid import uuid4


ARCHIVO_DATOS = Path(__file__).with_name("agenda_datos.json")
DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
HORAS = ["07:30", "08:30", "09:30", "10:30", "11:30", "12:30", "13:30"]
PRIORIDADES = ["Alta", "Media", "Baja"]
TIPOS_REPORTE = [
    "Resumen general",
    "Listado de materias",
    "Tareas pendientes",
    "Tareas completadas",
    "Próximos exámenes",
    "Horario semanal",
]


def nuevo_id():
    return uuid4().hex


def encriptar(clave):
    return hashlib.sha256(clave.encode("utf-8")).hexdigest()


def cargar_datos():
    if not ARCHIVO_DATOS.exists():
        return {"usuarios": {}}
    try:
        return json.loads(ARCHIVO_DATOS.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        messagebox.showwarning("Datos", "No se pudo leer el archivo JSON. Se iniciará vacío.")
        return {"usuarios": {}}


def guardar_datos(datos):
    ARCHIVO_DATOS.write_text(
        json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def fecha_valida(texto):
    try:
        date.fromisoformat(texto)
        return True
    except ValueError:
        return False


class Formulario(simpledialog.Dialog):
    def __init__(self, parent, titulo, campos, valores=None):
        self.campos = campos
        self.valores = valores or {}
        self.controles = {}
        self.resultado = None
        super().__init__(parent, titulo)

    def body(self, master):
        primero = None
        for fila, campo in enumerate(self.campos):
            clave, etiqueta = campo[0], campo[1]
            tipo = campo[2] if len(campo) > 2 else "entrada"
            opciones = campo[3] if len(campo) > 3 else []
            ttk.Label(master, text=etiqueta + ":").grid(
                row=fila, column=0, sticky="nw", padx=(0, 12), pady=6
            )
            valor = str(self.valores.get(clave, ""))
            if tipo == "combo":
                control = ttk.Combobox(master, values=opciones, state="readonly", width=35)
                control.set(valor)
            elif tipo == "texto":
                control = tk.Text(master, width=38, height=5, wrap="word")
                control.insert("1.0", valor)
                control.bind("<Shift-Return>", self.salto_linea)
            else:
                control = ttk.Entry(master, width=38, show="*" if tipo == "clave" else "")
                control.insert(0, valor)
            control.grid(row=fila, column=1, sticky="ew", pady=6)
            self.controles[clave] = (control, tipo)
            primero = primero or control
        master.columnconfigure(1, weight=1)
        return primero

    @staticmethod
    def salto_linea(evento):
        evento.widget.insert("insert", "\n")
        return "break"

    def apply(self):
        self.resultado = {}
        for clave, (control, tipo) in self.controles.items():
            if tipo == "texto":
                valor = control.get("1.0", "end").strip()
            else:
                valor = control.get().strip()
            self.resultado[clave] = valor


class AgendaApp:
    FONDO = "#f4f5fb"
    MORADO = "#6c5ce7"
    OSCURO = "#1c2144"
    TURQUESA = "#23c4b6"

    def __init__(self, root):
        self.root = root
        self.root.title("Agenda Estudiantil")
        self.root.geometry("1250x760")
        self.root.minsize(1000, 650)
        self.root.configure(bg=self.FONDO)
        self.datos = cargar_datos()
        self.correo_actual = None
        self.horario_seleccionado = None
        self.mapa_horario = {}
        self.dias_visibles = []
        self.configurar_estilos()
        self.crear_demo()
        self.mostrar_login()

    def configurar_estilos(self):
        estilo = ttk.Style()
        try:
            estilo.theme_use("clam")
        except tk.TclError:
            pass
        estilo.configure("TFrame", background=self.FONDO)
        estilo.configure("Card.TFrame", background="white")
        estilo.configure(
            "Titulo.TLabel", background=self.FONDO, foreground=self.OSCURO,
            font=("Segoe UI", 21, "bold")
        )
        estilo.configure(
            "TButton", font=("Segoe UI", 10), padding=(10, 7),
            background="white", foreground=self.OSCURO
        )
        estilo.configure(
            "Principal.TButton", font=("Segoe UI", 10, "bold"), padding=(12, 8),
            background=self.MORADO, foreground="white"
        )
        estilo.map("Principal.TButton", background=[("active", "#5848d6")])
        estilo.configure("Peligro.TButton", background="#fdebef", foreground="#a83b55")
        estilo.configure(
            "Treeview", rowheight=32, background="white", fieldbackground="white",
            foreground=self.OSCURO, font=("Segoe UI", 9)
        )
        estilo.configure(
            "Treeview.Heading", background="#ebeafd", foreground="#454a72",
            font=("Segoe UI", 9, "bold"), padding=7
        )
        estilo.map("Treeview", background=[("selected", "#dcd8ff")])
        estilo.configure(
            "Horario.Treeview", rowheight=49, background="#f7f7ff",
            fieldbackground="#f7f7ff", font=("Segoe UI", 9, "bold")
        )
        estilo.configure(
            "Horario.Treeview.Heading", background="#393d68", foreground="white",
            font=("Segoe UI", 9, "bold"), padding=8
        )
        estilo.configure("TNotebook.Tab", font=("Segoe UI", 10, "bold"), padding=(12, 9))
        estilo.map(
            "TNotebook.Tab", background=[("selected", self.MORADO)],
            foreground=[("selected", "white")]
        )

    def crear_demo(self):
        if "demo@agenda.com" not in self.datos["usuarios"]:
            self.datos["usuarios"]["demo@agenda.com"] = {
                "nombre": "Estudiante Demo", "apellido": "", "carrera": "Sistemas",
                "ciclo": "1", "clave": encriptar("Demo123"),
                "materias": [], "horarios": [], "tareas": [], "examenes": []
            }
            guardar_datos(self.datos)

    @property
    def usuario(self):
        return self.datos["usuarios"][self.correo_actual]

    def guardar(self):
        guardar_datos(self.datos)
        self.actualizar_todo()

    def limpiar(self):
        for control in self.root.winfo_children():
            control.destroy()

    def mostrar_login(self):
        self.correo_actual = None
        self.limpiar()
        exterior = tk.Frame(self.root, bg=self.FONDO)
        exterior.pack(fill="both", expand=True)
        caja = tk.Frame(exterior, bg="white", highlightbackground="#dddff0", highlightthickness=1)
        caja.place(relx=0.5, rely=0.5, anchor="center")

        dibujo = tk.Canvas(caja, width=360, height=500, bg=self.MORADO, highlightthickness=0)
        dibujo.grid(row=0, column=0)
        dibujo.create_rectangle(30, 30, 330, 190, fill="white", outline="")
        dibujo.create_rectangle(50, 48, 310, 87, fill=self.OSCURO, outline="")
        dibujo.create_text(70, 68, anchor="w", text="MI AGENDA SEMANAL", fill="white",
                           font=("Segoe UI", 12, "bold"))
        for x, letra in zip((75, 125, 175, 225, 275), ("L", "M", "M", "J", "V")):
            dibujo.create_text(x, 107, text=letra, fill="#6f7693", font=("Segoe UI", 9, "bold"))
            dibujo.create_rectangle(x - 15, 123, x + 15, 150,
                                    fill=self.TURQUESA if x == 175 else "#efedff", outline="")
            dibujo.create_rectangle(x - 15, 158, x + 15, 180, fill="#eefaf7", outline="")
        dibujo.create_line(165, 136, 172, 143, 185, 130, fill="white", width=3)
        dibujo.create_text(48, 250, anchor="w", text="Tu semestre,\nbajo control.",
                           fill="white", font=("Segoe UI", 25, "bold"))
        dibujo.create_text(50, 350, anchor="w",
                           text="Materias organizadas\nHorarios claros\nTareas al día",
                           fill="#eeeaff", font=("Segoe UI", 11))

        formulario = ttk.Frame(caja, style="Card.TFrame", padding=42)
        formulario.grid(row=0, column=1, sticky="nsew")
        ttk.Label(formulario, text="Bienvenido", background="white", foreground=self.OSCURO,
                  font=("Segoe UI", 23, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 22))
        ttk.Label(formulario, text="Correo electrónico", background="white").grid(row=1, column=0, sticky="w")
        correo = ttk.Entry(formulario, width=38)
        correo.grid(row=2, column=0, sticky="ew", pady=(5, 13))
        ttk.Label(formulario, text="Contraseña", background="white").grid(row=3, column=0, sticky="w")
        clave = ttk.Entry(formulario, width=38, show="*")
        clave.grid(row=4, column=0, sticky="ew", pady=(5, 20))

        def ingresar(evento=None):
            email = correo.get().strip().lower()
            registro = self.datos["usuarios"].get(email)
            if not registro or registro["clave"] != encriptar(clave.get()):
                messagebox.showerror("Ingreso", "Correo o contraseña incorrectos.")
                return
            self.correo_actual = email
            self.mostrar_principal()

        ttk.Button(formulario, text="Iniciar sesión", style="Principal.TButton",
                   command=ingresar).grid(row=5, column=0, sticky="ew", pady=(0, 9))
        ttk.Button(formulario, text="Crear cuenta", command=self.registrar).grid(
            row=6, column=0, sticky="ew"
        )
        ttk.Label(formulario, text="Demo: demo@agenda.com · Demo123", background="white",
                  foreground="#6f7693").grid(row=7, column=0, pady=(25, 0))
        correo.insert(0, "demo@agenda.com")
        clave.insert(0, "Demo123")
        clave.bind("<Return>", ingresar)

    def registrar(self):
        campos = [
            ("nombre", "Nombre"), ("apellido", "Apellido"),
            ("correo", "Correo electrónico"), ("carrera", "Carrera"),
            ("ciclo", "Ciclo"), ("clave", "Contraseña", "clave")
        ]
        ventana = Formulario(self.root, "Crear cuenta", campos)
        if not ventana.resultado:
            return
        r = ventana.resultado
        email = r["correo"].lower()
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            messagebox.showerror("Registro", "Ingrese un correo válido.")
            return
        if email in self.datos["usuarios"]:
            messagebox.showerror("Registro", "Ese correo ya está registrado.")
            return
        if any(not r[c] for c in ("nombre", "apellido", "carrera", "ciclo")) or len(r["clave"]) < 4:
            messagebox.showerror("Registro", "Complete todos los campos y use una contraseña de 4 caracteres.")
            return
        self.datos["usuarios"][email] = {
            "nombre": r["nombre"], "apellido": r["apellido"], "carrera": r["carrera"],
            "ciclo": r["ciclo"], "clave": encriptar(r["clave"]),
            "materias": [], "horarios": [], "tareas": [], "examenes": []
        }
        guardar_datos(self.datos)
        self.correo_actual = email
        self.mostrar_principal()

    def mostrar_principal(self):
        self.limpiar()
        barra = tk.Frame(self.root, bg=self.OSCURO, height=70)
        barra.pack(fill="x")
        barra.pack_propagate(False)
        tk.Label(barra, text="AGENDA ESTUDIANTIL", bg=self.OSCURO, fg="white",
                 font=("Segoe UI", 16, "bold")).pack(side="left", padx=22)
        tk.Label(barra, text=f"{self.usuario['nombre']} · {self.usuario['carrera']}",
                 bg=self.OSCURO, fg="#c9cdea").pack(side="left")
        ttk.Button(barra, text="Cerrar sesión", command=self.mostrar_login).pack(
            side="right", padx=20, pady=17
        )
        contenido = ttk.Frame(self.root, padding=14)
        contenido.pack(fill="both", expand=True)
        self.tabs = ttk.Notebook(contenido)
        self.tabs.pack(fill="both", expand=True)
        self.crear_materias()
        self.crear_horarios()
        self.crear_tareas()
        self.crear_examenes()
        self.crear_reportes()
        self.actualizar_todo()

    def nueva_tab(self, nombre):
        tab = ttk.Frame(self.tabs, padding=18)
        self.tabs.add(tab, text=nombre)
        return tab

    def tabla(self, padre, columnas, estilo="Treeview"):
        marco = ttk.Frame(padre)
        marco.pack(fill="both", expand=True, pady=(10, 0))
        tree = ttk.Treeview(marco, columns=[c[0] for c in columnas], show="headings", style=estilo)
        for clave, titulo, ancho, ancla in columnas:
            tree.heading(clave, text=titulo)
            tree.column(clave, width=ancho, anchor=ancla)
        barra = ttk.Scrollbar(marco, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=barra.set)
        tree.grid(row=0, column=0, sticky="nsew")
        barra.grid(row=0, column=1, sticky="ns")
        marco.rowconfigure(0, weight=1)
        marco.columnconfigure(0, weight=1)
        return tree

    def seleccionado(self, tree):
        filas = tree.selection()
        if not filas:
            messagebox.showwarning("Selección", "Seleccione primero un registro.")
            return None
        return filas[0]

    def materia(self, materia_id):
        return next((m for m in self.usuario["materias"] if m["id"] == materia_id), None)

    def nombre_materia(self, materia_id):
        item = self.materia(materia_id)
        return item["nombre"] if item else "Materia eliminada"

    def id_materia(self, nombre):
        item = next((m for m in self.usuario["materias"] if m["nombre"] == nombre), None)
        return item["id"] if item else None

    def nombres_materias(self):
        return [m["nombre"] for m in sorted(self.usuario["materias"], key=lambda x: x["nombre"])]

    # MATERIAS
    def crear_materias(self):
        tab = self.nueva_tab("Materias")
        encabezado = ttk.Frame(tab)
        encabezado.pack(fill="x")
        ttk.Label(encabezado, text="Gestión de materias", style="Titulo.TLabel").pack(side="left")
        ttk.Button(encabezado, text="+ Nueva materia", style="Principal.TButton",
                   command=self.agregar_materia).pack(side="right")
        botones = ttk.Frame(tab)
        botones.pack(fill="x", pady=(12, 0))
        ttk.Button(botones, text="Editar", command=self.editar_materia).pack(side="right", padx=4)
        ttk.Button(botones, text="Eliminar", style="Peligro.TButton",
                   command=self.eliminar_materia).pack(side="right", padx=4)
        self.tabla_materias = self.tabla(tab, [
            ("nombre", "Materia", 260, "w"), ("docente", "Docente", 220, "w"),
            ("lugar", "Lugar", 160, "w"), ("unidades", "Unidades", 90, "center")
        ])
        self.tabla_materias.bind("<<TreeviewSelect>>", lambda e: self.detalle_materia())
        self.tabla_materias.bind("<Double-1>", lambda e: self.editar_materia())
        self.detalle = tk.Text(tab, height=7, wrap="word", bg="white", bd=0, padx=9, pady=7)
        self.detalle.pack(fill="x", pady=(10, 0))
        self.detalle.insert("1.0", "Seleccione una materia para ver sus tareas y horario.")
        self.detalle.configure(state="disabled")

    def formulario_materia(self, valores=None):
        return Formulario(self.root, "Materia", [
            ("nombre", "Nombre"), ("docente", "Docente"),
            ("lugar", "Lugar"), ("unidades", "Unidades")
        ], valores).resultado

    def agregar_materia(self):
        r = self.formulario_materia()
        if not r:
            return
        if any(not r[k] for k in r) or not r["unidades"].isdigit() or int(r["unidades"]) <= 0:
            messagebox.showerror("Materia", "Complete los campos y use unidades mayores a cero.")
            return
        if any(m["nombre"].lower() == r["nombre"].lower() for m in self.usuario["materias"]):
            messagebox.showerror("Materia", "Ya existe una materia con ese nombre.")
            return
        self.usuario["materias"].append({"id": nuevo_id(), **r, "unidades": int(r["unidades"])})
        self.guardar()

    def editar_materia(self):
        item_id = self.seleccionado(self.tabla_materias)
        if not item_id:
            return
        item = self.materia(item_id)
        r = self.formulario_materia(item)
        if not r:
            return
        if any(not r[k] for k in r) or not r["unidades"].isdigit() or int(r["unidades"]) <= 0:
            messagebox.showerror("Materia", "Datos inválidos.")
            return
        item.update(r)
        item["unidades"] = int(r["unidades"])
        self.guardar()

    def eliminar_materia(self):
        item_id = self.seleccionado(self.tabla_materias)
        if not item_id:
            return
        vinculado = any(x["materia_id"] == item_id for grupo in ("horarios", "tareas", "examenes")
                        for x in self.usuario[grupo])
        if vinculado:
            messagebox.showerror("Materia", "No se puede eliminar porque tiene datos asociados.")
            return
        if messagebox.askyesno("Eliminar", "¿Desea eliminar la materia?"):
            self.usuario["materias"] = [m for m in self.usuario["materias"] if m["id"] != item_id]
            self.guardar()

    def actualizar_materias(self):
        self.tabla_materias.delete(*self.tabla_materias.get_children())
        for m in sorted(self.usuario["materias"], key=lambda x: x["nombre"]):
            self.tabla_materias.insert("", "end", iid=m["id"],
                                       values=(m["nombre"], m["docente"], m["lugar"], m["unidades"]))

    def detalle_materia(self):
        seleccion = self.tabla_materias.selection()
        if not seleccion:
            return
        item = self.materia(seleccion[0])
        tareas = [t for t in self.usuario["tareas"]
                  if t["materia_id"] == item["id"] and t["estado"] == "Pendiente"]
        horarios = [h for h in self.usuario["horarios"] if h["materia_id"] == item["id"]]
        lineas = [item["nombre"], f"Docente: {item['docente']} · Lugar: {item['lugar']} · Unidades: {item['unidades']}",
                  "", "TAREAS PENDIENTES"]
        lineas += [f"• {t['fecha']} [{t['prioridad']}] {t['titulo']}" for t in tareas] or ["• Ninguna"]
        lineas += ["", "HORARIO"]
        lineas += [f"• {h['dia']} {h['inicio']} - {h['fin']} · {h['aula']}" for h in horarios] or ["• Sin horario"]
        self.detalle.configure(state="normal")
        self.detalle.delete("1.0", "end")
        self.detalle.insert("1.0", "\n".join(lineas))
        self.detalle.configure(state="disabled")

    # HORARIOS
    def crear_horarios(self):
        tab = self.nueva_tab("Horarios")
        encabezado = ttk.Frame(tab)
        encabezado.pack(fill="x")
        ttk.Label(encabezado, text="Horario de clases", style="Titulo.TLabel").pack(side="left")
        ttk.Button(encabezado, text="+ Nuevo horario", style="Principal.TButton",
                   command=self.agregar_horario).pack(side="right")
        botones = ttk.Frame(tab)
        botones.pack(fill="x", pady=(12, 6))
        ttk.Button(botones, text="Editar", command=self.editar_horario).pack(side="right", padx=4)
        ttk.Button(botones, text="Eliminar", style="Peligro.TButton",
                   command=self.eliminar_horario).pack(side="right", padx=4)
        columnas = [("hora", "Hora", 150, "center")] + [(d, d, 180, "center") for d in DIAS[:5]]
        self.tabla_horario = self.tabla(tab, columnas, "Horario.Treeview")
        self.tabla_horario.tag_configure("par", background="#e9e7ff")
        self.tabla_horario.tag_configure("impar", background="#eefaf7")
        self.tabla_horario.bind("<ButtonRelease-1>", self.clic_horario)

    def datos_horario(self, valores=None):
        return Formulario(self.root, "Horario", [
            ("materia", "Materia", "combo", self.nombres_materias()),
            ("dia", "Día", "combo", DIAS),
            ("inicio", "Hora de inicio", "combo", HORAS[:-1]),
            ("fin", "Hora de fin", "combo", HORAS[1:]),
            ("aula", "Aula")
        ], valores or {"dia": "Lunes", "inicio": "07:30", "fin": "08:30"}).resultado

    def horario_valido(self, r, ignorar=None):
        if (
            not all(r.values())
            or r["inicio"] not in HORAS[:-1]
            or r["fin"] not in HORAS[1:]
            or r["fin"] <= r["inicio"]
        ):
            messagebox.showerror("Horario", "Seleccione un rango válido entre 07:30 y 13:30.")
            return False
        for h in self.usuario["horarios"]:
            if h["id"] != ignorar and h["dia"] == r["dia"] and r["inicio"] < h["fin"] and r["fin"] > h["inicio"]:
                messagebox.showerror("Horario", "El horario se cruza con otra materia.")
                return False
        return True

    def agregar_horario(self):
        if not self.usuario["materias"]:
            messagebox.showwarning("Horario", "Primero registre una materia.")
            return
        r = self.datos_horario()
        if not r or not self.horario_valido(r):
            return
        self.usuario["horarios"].append({
            "id": nuevo_id(), "materia_id": self.id_materia(r.pop("materia")), **r
        })
        self.guardar()

    def editar_horario(self):
        if not self.horario_seleccionado:
            messagebox.showwarning("Horario", "Seleccione directamente una materia de la tabla.")
            return
        item = next(h for h in self.usuario["horarios"] if h["id"] == self.horario_seleccionado)
        inicial = {**item, "materia": self.nombre_materia(item["materia_id"])}
        r = self.datos_horario(inicial)
        if not r or not self.horario_valido(r, item["id"]):
            return
        item.update(r)
        item["materia_id"] = self.id_materia(item.pop("materia"))
        self.guardar()

    def eliminar_horario(self):
        if not self.horario_seleccionado:
            messagebox.showwarning("Horario", "Seleccione una materia de la tabla.")
            return
        if messagebox.askyesno("Eliminar", "¿Desea eliminar el horario?"):
            self.usuario["horarios"] = [h for h in self.usuario["horarios"]
                                         if h["id"] != self.horario_seleccionado]
            self.guardar()

    def actualizar_horarios(self):
        self.tabla_horario.delete(*self.tabla_horario.get_children())
        self.mapa_horario = {}
        self.horario_seleccionado = None
        for indice, (inicio, fin) in enumerate(zip(HORAS, HORAS[1:])):
            fila = f"hora-{indice}"
            valores = [f"{inicio} - {fin}"]
            for dia in DIAS[:5]:
                h = next((x for x in self.usuario["horarios"]
                          if x["dia"] == dia and x["inicio"] < fin and x["fin"] > inicio), None)
                valores.append(self.nombre_materia(h["materia_id"]) if h else "")
                if h:
                    self.mapa_horario[(fila, dia)] = h["id"]
            self.tabla_horario.insert("", "end", iid=fila, values=valores,
                                      tags=("par" if indice % 2 == 0 else "impar",))

    def clic_horario(self, evento):
        fila = self.tabla_horario.identify_row(evento.y)
        columna = int(self.tabla_horario.identify_column(evento.x).replace("#", "") or 0)
        if fila and 2 <= columna <= 6:
            dia = DIAS[columna - 2]
            self.horario_seleccionado = self.mapa_horario.get((fila, dia))

    # TAREAS
    def crear_tareas(self):
        tab = self.nueva_tab("Tareas")
        encabezado = ttk.Frame(tab)
        encabezado.pack(fill="x")
        ttk.Label(encabezado, text="Gestión de tareas", style="Titulo.TLabel").pack(side="left")
        ttk.Button(encabezado, text="+ Nueva tarea", style="Principal.TButton",
                   command=self.agregar_tarea).pack(side="right")
        botones = ttk.Frame(tab)
        botones.pack(fill="x", pady=(12, 0))
        ttk.Button(botones, text="Editar", command=self.editar_tarea).pack(side="right", padx=3)
        ttk.Button(botones, text="Eliminar", style="Peligro.TButton",
                   command=self.eliminar_tarea).pack(side="right", padx=3)
        ttk.Button(botones, text="Completar/Reabrir", command=self.cambiar_tarea).pack(side="right", padx=3)
        self.tabla_tareas = self.tabla(tab, [
            ("estado", "Estado", 100, "center"), ("fecha", "Entrega", 105, "center"),
            ("prioridad", "Prioridad", 90, "center"), ("materia", "Materia", 180, "w"),
            ("titulo", "Título", 220, "w"), ("descripcion", "Descripción", 320, "w")
        ])
        self.tabla_tareas.tag_configure("alta", background="#f8dede")
        self.tabla_tareas.tag_configure("media", background="#fff1c9")
        self.tabla_tareas.tag_configure("baja", background="#dff2e4")

    def datos_tarea(self, valores=None):
        inicial = valores or {"fecha": date.today().isoformat(), "prioridad": "Media"}
        return Formulario(self.root, "Tarea", [
            ("materia", "Materia", "combo", self.nombres_materias()),
            ("titulo", "Título"), ("descripcion", "Descripción", "texto"),
            ("fecha", "Fecha (AAAA-MM-DD)"),
            ("prioridad", "Prioridad", "combo", PRIORIDADES)
        ], inicial).resultado

    def agregar_tarea(self):
        if not self.usuario["materias"]:
            messagebox.showwarning("Tarea", "Primero registre una materia.")
            return
        r = self.datos_tarea()
        if not r or not r["materia"] or not r["titulo"] or not fecha_valida(r["fecha"]):
            messagebox.showerror("Tarea", "Complete la materia, el título y una fecha válida.")
            return
        self.usuario["tareas"].append({
            "id": nuevo_id(), "materia_id": self.id_materia(r.pop("materia")),
            "estado": "Pendiente", **r
        })
        self.guardar()

    def editar_tarea(self):
        item_id = self.seleccionado(self.tabla_tareas)
        if not item_id:
            return
        item = next(t for t in self.usuario["tareas"] if t["id"] == item_id)
        r = self.datos_tarea({**item, "materia": self.nombre_materia(item["materia_id"])})
        if not r or not r["titulo"] or not fecha_valida(r["fecha"]):
            messagebox.showerror("Tarea", "Datos inválidos.")
            return
        item.update(r)
        item["materia_id"] = self.id_materia(item.pop("materia"))
        self.guardar()

    def cambiar_tarea(self):
        item_id = self.seleccionado(self.tabla_tareas)
        if item_id:
            item = next(t for t in self.usuario["tareas"] if t["id"] == item_id)
            item["estado"] = "Completada" if item["estado"] == "Pendiente" else "Pendiente"
            self.guardar()

    def eliminar_tarea(self):
        item_id = self.seleccionado(self.tabla_tareas)
        if item_id and messagebox.askyesno("Eliminar", "¿Desea eliminar la tarea?"):
            self.usuario["tareas"] = [t for t in self.usuario["tareas"] if t["id"] != item_id]
            self.guardar()

    def actualizar_tareas(self):
        self.tabla_tareas.delete(*self.tabla_tareas.get_children())
        orden = {"Alta": 0, "Media": 1, "Baja": 2}
        for t in sorted(self.usuario["tareas"], key=lambda x: (x["estado"] == "Completada", x["fecha"], orden[x["prioridad"]])):
            self.tabla_tareas.insert("", "end", iid=t["id"],
                values=(t["estado"], t["fecha"], t["prioridad"], self.nombre_materia(t["materia_id"]),
                        t["titulo"], t["descripcion"]), tags=(t["prioridad"].lower(),))

    # EXÁMENES
    def crear_examenes(self):
        tab = self.nueva_tab("Exámenes")
        encabezado = ttk.Frame(tab)
        encabezado.pack(fill="x")
        ttk.Label(encabezado, text="Gestión de exámenes", style="Titulo.TLabel").pack(side="left")
        ttk.Button(encabezado, text="+ Nuevo examen", style="Principal.TButton",
                   command=self.agregar_examen).pack(side="right")
        botones = ttk.Frame(tab)
        botones.pack(fill="x", pady=(12, 0))
        ttk.Button(botones, text="Editar", command=self.editar_examen).pack(side="right", padx=4)
        ttk.Button(botones, text="Eliminar", style="Peligro.TButton",
                   command=self.eliminar_examen).pack(side="right", padx=4)
        self.tabla_examenes = self.tabla(tab, [
            ("fecha", "Fecha", 105, "center"), ("hora", "Hora", 80, "center"),
            ("materia", "Materia", 180, "w"), ("aula", "Aula", 110, "w"),
            ("temas", "Temas a evaluar", 500, "w")
        ])

    def datos_examen(self, valores=None):
        return Formulario(self.root, "Examen", [
            ("materia", "Materia", "combo", self.nombres_materias()),
            ("fecha", "Fecha (AAAA-MM-DD)"), ("hora", "Hora (HH:MM)"),
            ("aula", "Aula"), ("temas", "Temas a evaluar", "texto")
        ], valores or {"fecha": date.today().isoformat(), "hora": "08:00"}).resultado

    def validar_examen(self, r):
        return r and all(r.values()) and fecha_valida(r["fecha"]) and bool(re.fullmatch(r"([01]\d|2[0-3]):[0-5]\d", r["hora"]))

    def agregar_examen(self):
        if not self.usuario["materias"]:
            messagebox.showwarning("Examen", "Primero registre una materia.")
            return
        r = self.datos_examen()
        if not self.validar_examen(r):
            messagebox.showerror("Examen", "Complete todos los datos correctamente.")
            return
        self.usuario["examenes"].append({
            "id": nuevo_id(), "materia_id": self.id_materia(r.pop("materia")), **r
        })
        self.guardar()

    def editar_examen(self):
        item_id = self.seleccionado(self.tabla_examenes)
        if not item_id:
            return
        item = next(e for e in self.usuario["examenes"] if e["id"] == item_id)
        r = self.datos_examen({**item, "materia": self.nombre_materia(item["materia_id"])})
        if not self.validar_examen(r):
            messagebox.showerror("Examen", "Datos inválidos.")
            return
        item.update(r)
        item["materia_id"] = self.id_materia(item.pop("materia"))
        self.guardar()

    def eliminar_examen(self):
        item_id = self.seleccionado(self.tabla_examenes)
        if item_id and messagebox.askyesno("Eliminar", "¿Desea eliminar el examen?"):
            self.usuario["examenes"] = [e for e in self.usuario["examenes"] if e["id"] != item_id]
            self.guardar()

    def actualizar_examenes(self):
        self.tabla_examenes.delete(*self.tabla_examenes.get_children())
        for e in sorted(self.usuario["examenes"], key=lambda x: (x["fecha"], x["hora"])):
            self.tabla_examenes.insert("", "end", iid=e["id"],
                values=(e["fecha"], e["hora"], self.nombre_materia(e["materia_id"]), e["aula"], e["temas"]))

    # REPORTES
    def crear_reportes(self):
        tab = self.nueva_tab("Reportes")
        ttk.Label(tab, text="Reportes académicos", style="Titulo.TLabel").pack(anchor="w")
        controles = ttk.Frame(tab)
        controles.pack(fill="x", pady=12)
        ttk.Label(controles, text="Tipo de reporte:").pack(side="left")
        self.tipo_reporte = ttk.Combobox(controles, values=TIPOS_REPORTE, state="readonly", width=28)
        self.tipo_reporte.pack(side="left", padx=8)
        self.tipo_reporte.set("Resumen general")
        self.tipo_reporte.bind("<<ComboboxSelected>>", lambda e: self.actualizar_reporte())
        self.texto_reporte = ScrolledText(tab, wrap="word", font=("Consolas", 10), padx=12, pady=12)
        self.texto_reporte.pack(fill="both", expand=True)

    def reporte_materias(self):
        lineas = ["LISTADO DE MATERIAS", "====================", ""]
        lineas += [f"{m['nombre']} | Docente: {m['docente']} | Lugar: {m['lugar']} | Unidades: {m['unidades']}"
                   for m in self.usuario["materias"]] or ["No hay materias."]
        return "\n".join(lineas)

    def reporte_tareas(self, estado):
        lineas = [f"TAREAS {estado.upper()}", "====================", ""]
        tareas = [t for t in self.usuario["tareas"] if t["estado"] == estado]
        lineas += [f"[{t['prioridad']}] {t['fecha']} | {self.nombre_materia(t['materia_id'])} | {t['titulo']}"
                   for t in tareas] or ["No hay tareas."]
        return "\n".join(lineas)

    def reporte_examenes(self):
        lineas = ["PRÓXIMOS EXÁMENES", "=================", ""]
        examenes = [e for e in self.usuario["examenes"] if e["fecha"] >= date.today().isoformat()]
        lineas += [f"{e['fecha']} {e['hora']} | {self.nombre_materia(e['materia_id'])} | {e['temas']}"
                   for e in examenes] or ["No hay próximos exámenes."]
        return "\n".join(lineas)

    def reporte_horario(self):
        lineas = ["HORARIO SEMANAL", "===============", ""]
        for dia in DIAS:
            items = [h for h in self.usuario["horarios"] if h["dia"] == dia]
            if items:
                lineas.append(dia)
                lineas += [f"  {h['inicio']} - {h['fin']} | {self.nombre_materia(h['materia_id'])}"
                           for h in sorted(items, key=lambda x: x["inicio"])]
                lineas.append("")
        return "\n".join(lineas) if len(lineas) > 3 else "HORARIO SEMANAL\n\nNo hay horarios."

    def actualizar_reporte(self):
        tipo = self.tipo_reporte.get()
        if tipo == "Listado de materias":
            texto = self.reporte_materias()
        elif tipo == "Tareas pendientes":
            texto = self.reporte_tareas("Pendiente")
        elif tipo == "Tareas completadas":
            texto = self.reporte_tareas("Completada")
        elif tipo == "Próximos exámenes":
            texto = self.reporte_examenes()
        elif tipo == "Horario semanal":
            texto = self.reporte_horario()
        else:
            pendientes = sum(t["estado"] == "Pendiente" for t in self.usuario["tareas"])
            texto = (
                "RESUMEN GENERAL\n===============\n\n"
                f"Materias: {len(self.usuario['materias'])}\n"
                f"Horarios: {len(self.usuario['horarios'])}\n"
                f"Tareas pendientes: {pendientes}\n"
                f"Exámenes próximos: {sum(e['fecha'] >= date.today().isoformat() for e in self.usuario['examenes'])}"
            )
        self.texto_reporte.delete("1.0", "end")
        self.texto_reporte.insert("1.0", texto)

    def actualizar_todo(self):
        if not self.correo_actual or not hasattr(self, "tabs"):
            return
        self.actualizar_materias()
        self.actualizar_horarios()
        self.actualizar_tareas()
        self.actualizar_examenes()
        self.actualizar_reporte()


def main():
    root = tk.Tk()
    AgendaApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
