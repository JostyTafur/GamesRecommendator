import pandas as pd
import heapq
import tkinter as tk
from tkinter import Toplevel, Label, Button
from tkinter import font
import tkinter as tk
from tkinter import ttk
import networkx as nx
import matplotlib.pyplot as plt
from PIL import Image, ImageTk
from Grafo import Grafo
import os

#videojuegos_cercanos = []
inicio = None
imagen_grafico = None
nro_juegos = 0

def dijkstra(grafo, inicio, plataforma, genero, productora, año_inicio, año_final):
    distancias = {nodo: float('inf') for nodo in grafo.obtener_nodos()}
    distancias[inicio] = 0
    cola_prioridad = [(0, inicio)]
    visitados = set()

    while cola_prioridad:
        _, nodo_actual = heapq.heappop(cola_prioridad)
        if nodo_actual in visitados:
            continue
        visitados.add(nodo_actual)

        for nodo_vecino in grafo.aristas[nodo_actual]:
            peso = grafo.aristas[nodo_actual][nodo_vecino]
            distancia_nueva = distancias[nodo_actual] + peso
            if distancia_nueva < distancias[nodo_vecino]:
                distancias[nodo_vecino] = distancia_nueva
                heapq.heappush(cola_prioridad, (distancia_nueva, nodo_vecino))

    # Filtrar los juegos según la plataforma, género, productora y rango de años especificados
    videojuegos_filtrados = []
    for juego, distancia in distancias.items():
        if plataforma == "Todas" or grafo.nodos[juego]['platform'] == plataforma:
            if genero == "Todos" or grafo.nodos[juego]['genre'] == genero:
                if productora == "Todas" or grafo.nodos[juego]['publisher'] == productora:
                    año = int(grafo.nodos[juego]['year'])
                    if año_inicio <= año <= año_final:
                        videojuegos_filtrados.append((juego, distancia))

    return sorted(videojuegos_filtrados, key=lambda x: x[1])[1:21]

def cerrar_ventana(root):
    root.destroy()

def obtener_Grafico():
    # Crear un nuevo grafo de NetworkX
    grafo_nx = nx.Graph()

# Agregar el nodo de inicio al grafo
    grafo_nx.add_node(entry_juego_partida.get(), label=grafo.nodos[inicio]['label'], color='red')

    videogames_grafo = videojuegos_cercanos[:nro_juegos]

# Agregar los videojuegos cercanos como nodos y las aristas correspondientes
    for juego, distancia in videogames_grafo:
        nodo_juego = grafo.nodos[juego]
        nombre_juego = nodo_juego['label']
        peso_arista = str(distancia)
        node_juego = str(juego)
        grafo_nx.add_node(node_juego, label=nombre_juego)
        grafo_nx.add_edge(entry_juego_partida.get(), node_juego, weight=peso_arista)

# Generar una representación gráfica circular del grafo
    pos = nx.shell_layout(grafo_nx)

# Obtener las etiquetas de los nodos
    labels = {node: grafo_nx.nodes[node]['label'] for node in grafo_nx.nodes}

# Obtener los pesos de las aristas
    edge_labels = nx.get_edge_attributes(grafo_nx, 'weight')

    node_sizes = [2000] + [1000] * len(videogames_grafo)

# Asignar colores diferentes a los nodos
    node_colors = ['red'] + ['green'] * len(videogames_grafo)

# Crear una figura
    fig = plt.figure(figsize=(6, 6))

# Dibujar el grafo en la figura
    nx.draw_networkx(
        grafo_nx,
        pos,
        labels=labels,
        node_size=node_sizes,
        node_color=node_colors,
        with_labels=True
    )

# Dibujar los pesos de las aristas
    nx.draw_networkx_edge_labels(
        grafo_nx,
        pos,
        edge_labels=edge_labels
    )
    temp_filename = "temp.png"
    fig.savefig(temp_filename)

    ventana_imagen = Toplevel()
    ventana_imagen.title("Imagen Generada")

    # Cargar la imagen generada con PIL
    imagen = Image.open(temp_filename)
    imagen_tk = ImageTk.PhotoImage(imagen)

    # Mostrar la imagen en una etiqueta
    etiqueta_imagen = Label(ventana_imagen, image=imagen_tk)
    etiqueta_imagen.pack()

    boton_cerrar = Button(ventana_imagen, text="Cerrar", command=lambda: cerrar_ventana(ventana_imagen))
    boton_cerrar.pack()
    # Eliminar el archivo temporal y cerrar la imagen con PIL
    imagen.close()
    os.remove(temp_filename)

def obtener_recomendaciones():
    global nro_juegos
    
    nombre_inicio = entry_juego_partida.get()
    plataforma_deseada = entry_plataforma.get()
    genero_deseado = entry_genero.get()
    productora_deseada = entry_productora.get()
    año_inicial_deseado = int(entry_año_inicio.get())
    año_final_deseado = int(entry_año_final.get())
    nro_juegos = int(entry_nrojuegos.get())
    
    global videojuegos_cercanos
    global inicio
    
    # Buscar el nodo de inicio en base al nombre
    inicio = None
    for nodo in grafo.nodos:
       if grafo.nodos[nodo]['name'] == nombre_inicio:
            inicio = nodo
            break

    # Verificar si se encontró el nodo de inicio
    if inicio is None:
        frame_canvas.delete(1.0, tk.END)
        frame_canvas.insert(tk.END, "El videojuego de inicio no se encuentra en el grafo.\n")
    else:
        # Utilizar el algoritmo de Dijkstra para encontrar las distancias y filtrar por plataforma
        videojuegos_cercanos = dijkstra(grafo, inicio, plataforma_deseada, genero_deseado, productora_deseada, año_inicial_deseado, año_final_deseado)
        
        mostrar_resultados(videojuegos_cercanos, plataforma_deseada, nro_juegos)
        
# Función para mostrar los juegos recomendados como "cards"
def mostrar_resultados(videojuegos_cercanos, plataforma_deseada, nro_juegos):

    # Crear un Frame para el ListView dentro del Canvas
    frame_listview = tk.Frame(canvas, bg="#DFF6FE")
    canvas.create_window((0, 0), window=frame_listview, anchor="nw")

    # Crear la etiqueta para el mensaje
    mensaje = tk.Label(frame_listview, text=f"Los {nro_juegos} videojuegos más cercanos en relación al peso para la plataforma {plataforma_deseada}:", font=font_style)
    mensaje.pack()

    # Mostrar los juegos en el Listbox
    colores = ["#F2B900", "#F25330", "#BD0036"]
    num_colores = len(colores)

    for i, (juego, distancia) in enumerate(videojuegos_cercanos[:nro_juegos]):
        color = colores[i % num_colores]
        frame_juego = tk.Frame(frame_listview, bg=color, padx=10, pady=10, relief="raised")
        frame_juego.pack(padx=10, pady=10)

        # Label para mostrar el nombre del juego
        label_nombre = tk.Label(frame_juego, text=f"Juego: {grafo.nodos[juego]['name']}", font=font_style, bg=color)
        label_nombre.pack()

        label_label = tk.Label(frame_juego, text=f"Etiqueta: {grafo.nodos[juego]['label']}", font=font_style, bg=color)
        label_label.pack()

        label_plataforma = tk.Label(frame_juego, text=f"Plataforma: {grafo.nodos[juego]['platform']}", font=font_style, bg=color)
        label_plataforma.pack()

        label_genero = tk.Label(frame_juego, text=f"Genero: {grafo.nodos[juego]['genre']}", font=font_style, bg=color)
        label_genero.pack()

        label_productora = tk.Label(frame_juego, text=f"Productora: {grafo.nodos[juego]['publisher']}", font=font_style, bg=color)
        label_productora.pack()

        label_año = tk.Label(frame_juego, text=f"Año: {grafo.nodos[juego]['year']}", font=font_style, bg=color)
        label_año.pack()

        # Label para mostrar la distancia
        label_distancia = tk.Label(frame_juego, text=f"Distancia: {distancia}", font=font_style, bg=color)
        label_distancia.pack()

    # Configurar el tamaño del Canvas
    canvas.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

    # Configurar el desplazamiento del Canvas con el Scrollbar
    canvas.bind("<Configure>", lambda event: canvas.configure(scrollregion=canvas.bbox("all")))

    # Configurar el desplazamiento del Canvas con el mousewheel
    canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(int(-1 * (event.delta / 120)), "units"))

def cerrar_app():
    ventana.destroy()

# Ejemplo de uso
grafo = Grafo()

df = pd.read_csv('Dataset/Dataset_Videogames.csv', delimiter=';')

# Recorrer cada fila del dataframe
for index, row in df.iterrows():
    id = row['Id']
    label = row['Label']
    name = row['Name']
    platform = row['Platform']
    year = row['Year']
    genre = row['Genre']
    publisher = row['Publisher']

    grafo.agregar_nodo(id, label=label, name=name, platform=platform, year=year, genre=genre, publisher=publisher)

    for nodo in grafo.obtener_nodos():
      peso = 11
      if nodo != id:
        if grafo.nodos[nodo]['platform'] == platform:
          peso-=3
        if grafo.nodos[nodo]['year'] == year:
          peso-=2
        if grafo.nodos[nodo]['genre'] == genre:
          peso-=4
        if grafo.nodos[nodo]['publisher'] == publisher:
          peso-=1
      if peso < 11 and peso > 0:
        grafo.agregar_arista(id, nodo, peso)

def actualizar_lista(event):
    # Obtener el texto ingresado por el usuario
    texto_busqueda = entry_juego_partida.get()
    
    # Limpiar la lista de juegos
    lista_juegos.delete(0, tk.END)
    
    # Verificar si el texto de búsqueda coincide con algún juego
    for nodo in grafo.nodos:
        if texto_busqueda.lower() in grafo.nodos[nodo]['name'].lower():
            lista_juegos.insert(tk.END, grafo.nodos[nodo]['name'])

def seleccionar_juego(event):
    # Obtener el juego seleccionado en la lista
    juego_seleccionado = lista_juegos.get(lista_juegos.curselection())
    
    # Colocar el juego seleccionado en el input
    entry_juego_partida.delete(0, tk.END)
    entry_juego_partida.insert(tk.END, juego_seleccionado)
    ocultar_lista_juegos(None)

def mostrar_lista_juegos(event):
    # Mostrar el ListBox
    lista_juegos.place(x=entry_juego_partida.winfo_x(), y=entry_juego_partida.winfo_y() + entry_juego_partida.winfo_height())
    lista_juegos.lift()

def ocultar_lista_juegos(event):
    # Ocultar el ListBox
    lista_juegos.place_forget()

plataformas = [] #Lista para almacenar las plataformas sin repetirse

def agregar_lista_platforms():

    lista_plataform.delete(0, tk.END)
    
    # Recorrer los nodos y obtener las plataformas únicas
    for nodo in grafo.nodos:
        platform = grafo.nodos[nodo]['platform']
        if platform not in plataformas:
            plataformas.append(platform)
    
    lista_plataform.insert(tk.END, "Todas")
    # Insertar las plataformas en la lista
    for plataforma in plataformas:
        lista_plataform.insert(tk.END, plataforma)

def actualizar_lista_platforms(event):
    texto_busqueda = entry_plataforma.get()
    
    # Limpiar la lista de juegos
    lista_plataform.delete(0, tk.END)
    
    # Verificar si el texto de búsqueda coincide con algún juego
    for plat in plataformas:
        if texto_busqueda.lower() in plat.lower():
            lista_plataform.insert(tk.END, plat)

def seleccionar_platform(event):
    # Obtener la plataforma seleccionada en el ComboBox
    plataforma_seleccionada = lista_plataform.get(lista_plataform.curselection())
    
    # Establecer la plataforma seleccionada en el entry
    entry_plataforma.delete(0, tk.END)
    entry_plataforma.insert(tk.END, plataforma_seleccionada)
    ocultar_lista_platforms(None)

def mostrar_lista_platforms(event):
    # Mostrar el ListBox
    lista_plataform.place(x=entry_plataforma.winfo_x(), y=entry_plataforma.winfo_y() + entry_plataforma.winfo_height())
    lista_plataform.lift()

def ocultar_lista_platforms(event):
    # Ocultar el ListBox
    lista_plataform.place_forget()

genero = []

def agregar_lista_generos():

    lista_genero.delete(0, tk.END)
    
    # Recorrer los nodos y obtener las plataformas únicas
    for nodo in grafo.nodos:
        genre = grafo.nodos[nodo]['genre']
        if genre not in genero:
            genero.append(genre)
    
    lista_genero.insert(tk.END, "Todos")
    # Insertar las plataformas en la lista
    for genre in genero:
        lista_genero.insert(tk.END, genre)

def actualizar_lista_genero(event):
    # Limpiar el ComboBox de géneros
    texto_busqueda = entry_genero.get()
    
    # Limpiar la lista de juegos
    lista_genero.delete(0, tk.END)
    
    # Verificar si el texto de búsqueda coincide con algún juego
    for gen in genero:
        if texto_busqueda.lower() in gen.lower():
            lista_genero.insert(tk.END, gen)

def seleccionar_genero(event):
    # Obtener el género seleccionado en el ComboBox
    genero_seleccionado = lista_genero.get(lista_genero.curselection())
    
    # Establecer el género seleccionado en el entry
    entry_genero.delete(0, tk.END)
    entry_genero.insert(tk.END, genero_seleccionado)
    
def mostrar_lista_genero(event):
    # Mostrar el ListBox
    lista_genero.place(x=entry_genero.winfo_x(), y=entry_genero.winfo_y() + entry_genero.winfo_height())
    lista_genero.lift()

def ocultar_lista_genero(event):
    # Ocultar el ListBox
    lista_genero.place_forget()

productora = []

def agregar_lista_productoras():

    lista_productora.delete(0, tk.END)
    
    # Recorrer los nodos y obtener las plataformas únicas
    for nodo in grafo.nodos:
        product = grafo.nodos[nodo]['publisher']
        if product not in productora:
            productora.append(product)
    
    lista_productora.insert(tk.END, "Todas")
    # Insertar las plataformas en la lista
    for product in productora:
        lista_productora.insert(tk.END, product)

def actualizar_lista_productoras():
    # Limpiar el ComboBox de productoras
    texto_busqueda = entry_productora.get()
    
    # Limpiar la lista de juegos
    lista_productora.delete(0, tk.END)
    
    # Verificar si el texto de búsqueda coincide con algún juego
    for prod in productora:
        if texto_busqueda.lower() in prod.lower():
            lista_productora.insert(tk.END, prod)

def seleccionar_productora(event):
    # Obtener la productora seleccionada en el ComboBox
    productora_seleccionada = lista_productora.get(lista_productora.curselection())
    
    # Establecer la productora seleccionada en el entry
    entry_productora.delete(0, tk.END)
    entry_productora.insert(tk.END, productora_seleccionada)

def mostrar_lista_productora(event):
    # Mostrar el ListBox
    lista_productora.place(x=entry_productora.winfo_x(), y=entry_productora.winfo_y() + entry_productora.winfo_height())
    lista_productora.lift()

def ocultar_lista_productora(event):
    # Ocultar el ListBox
    lista_productora.place_forget()


# Crear la ventana principal
ventana = tk.Tk()
ventana.title("Sistema de Recomendación de Juegos")

ventana.geometry("1200x700")

# Cargar la imagen de fondo
ventana.configure(background="#05283C")

# Cambiar el font de las letras
font_style = font.Font(family="Helvetica", size=12)
font_title = font.Font(family="Helvetica", size=20)
font_subtitle = font.Font(family="Helvetica", size=14)

frame_entrada = tk.Frame(ventana, bg=ventana["bg"])
frame_entrada.pack(pady=10)

frame_filtros = tk.Frame(frame_entrada, bg="#203F51")
frame_filtros.grid(row=5, column=0, columnspan=2, pady=20)

label_title = tk.Label(frame_entrada, text="VideoGames Recomendator", font=font_title, bg=ventana["bg"], fg='#DFF6FE', highlightthickness=0)
label_title.grid(row=0, column=0, padx=5, pady=5, columnspan=5)

# Etiqueta y entrada para el juego de partida
label_juego_partida = tk.Label(frame_entrada, text="Juego de partida:", font=font_style, bg=ventana["bg"], fg='#DFF6FE', highlightthickness=0)
label_juego_partida.grid(row=1, column=0, padx=5, pady=5)
entry_juego_partida = tk.Entry(frame_entrada, font=font_style, bg="#DFF6FE", fg='#05283C', width=40)
entry_juego_partida.grid(row=1, column=1, padx=5, pady=5)

entry_juego_partida.bind("<KeyRelease>", actualizar_lista)
entry_juego_partida.bind('<FocusIn>',mostrar_lista_juegos)
entry_juego_partida.bind('<FocusOut>', ocultar_lista_juegos)

lista_juegos = tk.Listbox(frame_entrada, width=60, height=6)
#lista_juegos.grid(row=1, column=1, padx=3,pady=3)

lista_juegos.bind("<<ListboxSelect>>", seleccionar_juego)

label_subtitle = tk.Label(frame_filtros, text="Filtros de busqueda", font=font_title, bg=frame_filtros["bg"], fg='#DFF6FE', highlightthickness=0)
label_subtitle.grid(row=1, column=2, padx=5, pady=5, columnspan=2)

# Etiqueta y entrada para la plataforma
label_plataforma = tk.Label(frame_filtros, text="Plataforma:", font=font_style, bg=frame_filtros["bg"], fg='#DFF6FE', highlightthickness=0)
label_plataforma.grid(row=2, column=2, padx=10, pady=20)
entry_plataforma = tk.Entry(frame_filtros, font=font_style, bg="#DFF6FE", fg='#05283C', width=40)
entry_plataforma.grid(row=2, column=3, padx=10, pady=20)

entry_plataforma.bind("<KeyRelease>", actualizar_lista_platforms)
entry_plataforma.bind('<FocusIn>',mostrar_lista_platforms)
entry_plataforma.bind('<FocusOut>', ocultar_lista_platforms)

lista_plataform = tk.Listbox(frame_filtros, width=60, height=6)


entry_plataforma.insert(tk.END, "Todas")

agregar_lista_platforms()

lista_plataform.bind("<<ListboxSelect>>", seleccionar_platform)

# Etiqueta y entrada para el género
label_genero = tk.Label(frame_filtros, text="Género:", font=font_style, bg=frame_filtros["bg"], fg='#DFF6FE', highlightthickness=0)
label_genero.grid(row=4, column=2, padx=10, pady=20)
entry_genero = tk.Entry(frame_filtros, font=font_style, bg="#DFF6FE", fg='#05283C', width=40)
entry_genero.grid(row=4, column=3, padx=10, pady=20)

entry_genero.bind("<KeyRelease>", actualizar_lista_genero)
entry_genero.bind('<FocusIn>',mostrar_lista_genero)
entry_genero.bind('<FocusOut>', ocultar_lista_genero)

lista_genero = tk.Listbox(frame_filtros, width=60, height=6)

entry_genero.insert(tk.END, "Todos")

agregar_lista_generos()

lista_genero.bind("<<ListboxSelect>>", seleccionar_genero)

# Etiqueta y entrada para publisher
label_productora = tk.Label(frame_filtros, text="Productora:", font=font_style, bg=frame_filtros["bg"], fg='#DFF6FE', highlightthickness=0)
label_productora.grid(row=6, column=2, padx=10, pady=20)
entry_productora = tk.Entry(frame_filtros, font=font_style, bg="#DFF6FE", fg='#05283C', width=40)
entry_productora.grid(row=6, column=3, padx=10, pady=20)

entry_productora.bind("<KeyRelease>", actualizar_lista_productoras)
entry_productora.bind('<FocusIn>',mostrar_lista_productora)
entry_productora.bind('<FocusOut>', ocultar_lista_productora)

lista_productora = tk.Listbox(frame_filtros, width=60, height=6)

entry_productora.insert(tk.END, "Todas")

agregar_lista_productoras()

lista_productora.bind("<<ListboxSelect>>", seleccionar_productora)

frame_year = tk.Frame(frame_filtros, bg=frame_filtros["bg"])
frame_year.grid(row=8, column=3, padx=10, pady=25)

# Etiqueta y entrada para el año inicio
label_año_inicio = tk.Label(frame_filtros, text="Intervalo de años", font=font_style, bg=frame_filtros["bg"], fg='#DFF6FE', highlightthickness=0)
label_año_inicio.grid(row=8, column=2, padx=10, pady=25)
entry_año_inicio = tk.Entry(frame_year, font=font_style, bg="#DFF6FE", fg='#05283C', width=18)
entry_año_inicio.grid(row=0, column=0, padx=5, pady=10)

entry_año_inicio.insert(tk.END, "1900")

# Etiqueta y entrada para el año final
label_año_final = tk.Label(frame_year, text="a", font=font_style, bg=frame_filtros["bg"], fg='#DFF6FE', highlightthickness=0)
label_año_final.grid(row=0, column=1, padx=1, pady=1)
entry_año_final = tk.Entry(frame_year, font=font_style, bg="#DFF6FE", fg='#05283C', width=18)
entry_año_final.grid(row=0, column=2, padx=5, pady=10)

entry_año_final.insert(tk.END, "2019")

# Etiqueta y entrada para numero de juegos 
label_nrojuegos = tk.Label(frame_entrada, text="Nro de juegos:", font=font_style, bg=ventana["bg"], fg='#DFF6FE', highlightthickness=0)
label_nrojuegos.grid(row=2, column=0, padx=10, pady=10)
entry_nrojuegos = tk.Entry(frame_entrada, font=font_style, bg="#DFF6FE", fg='#05283C', width=40)
entry_nrojuegos.grid(row=2, column=1, padx=10, pady=10)

# Botón para obtener las recomendaciones
boton_obtener_recomendaciones = tk.Button(frame_entrada, text="Obtener Recomendaciones", command=obtener_recomendaciones, font=font_style, bg="#46B6FE", fg='#05283C', highlightthickness=0, width=30)
boton_obtener_recomendaciones.grid(row=3, column=1, padx=10, pady=(6, 20))

boton_obtener_recomendaciones = tk.Button(frame_entrada, text="Obtener Grafo", command=obtener_Grafico, font=font_style, bg="#46B6FE", fg='#05283C', highlightthickness=0, width=30)
boton_obtener_recomendaciones.grid(row=4, column=1, padx=10, pady=(2, 10))

boton_obtener_recomendaciones = tk.Button(frame_entrada, text="Cerrar app", command=cerrar_app, font=font_style, bg="#46B6FE", fg='#05283C', highlightthickness=0, width=30)
boton_obtener_recomendaciones.grid(row=6, column=1, padx=10, pady=(10, 10))

# Etiqueta para mostrar el gráfico
# etiqueta_grafico = tk.Label(frame_entrada, bg="#f1d4af")
# etiqueta_grafico.grid(row=6, column=0, padx=10, pady=10)

# Crear el Frame contenedor para el Canvas y el Scrollbar
frame_canvas = tk.Frame(frame_entrada, bg="#1461E1")
frame_canvas.grid(row=1, column=2,padx=20, pady=10, rowspan=10, columnspan=2)

for widget in frame_canvas.winfo_children():
        widget.destroy()
    
canvas = tk.Canvas(frame_canvas, bg="#DFF6FE", height=600, width=550)
canvas.pack(side="left", fill="both", expand=True)
scrollbar = tk.Scrollbar(frame_canvas, command=canvas.yview)
scrollbar.pack(side="right", fill="y")

    # Configurar el Canvas para que funcione con el Scrollbar
canvas.configure(yscrollcommand=scrollbar.set)
# Ejecutar el bucle principal de la interfaz
ventana.mainloop()