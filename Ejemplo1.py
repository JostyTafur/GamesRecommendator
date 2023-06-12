import pandas as pd
import heapq
import graphviz
import tkinter as tk
from tkinter import messagebox
from tkinter import font
import networkx as nx
import matplotlib.pyplot as plt
from PIL import Image, ImageTk
from Grafo import Grafo

videojuegos_cercanos = []
inicio = None
imagen_grafico = None
nro_juegos = 0

def dijkstra(grafo, inicio, plataforma):
    
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

    # Filtrar los juegos de la plataforma especificada
    videojuegos_filtrados = [(juego, distancia) for juego, distancia in distancias.items() if grafo.nodos[juego]['platform'] == plataforma]

    return sorted(videojuegos_filtrados, key=lambda x: x[1])[1:21]

def obtener_Grafico():
    global nro_juegos
    global inicio
    grafico = graphviz.Graph()
    grafico.node('inicio', label=grafo.nodos[inicio]['name'], color='red')

    # Agregar los videojuegos cercanos como nodos y las aristas correspondientes
    for i, (juego, distancia) in enumerate(videojuegos_cercanos):
        nodo_juego = grafo.nodos[juego]
        nombre_juego = nodo_juego['name']
        peso_arista = str(distancia)
        node_juego = str(juego)
        
        # Resaltar los primeros nro_juegos nodos
        if i < nro_juegos:
            grafico.node(node_juego, label=nombre_juego, color='yellow')
        else:
            grafico.node(node_juego, label=nombre_juego)
        
        grafico.edge('inicio', node_juego, label=peso_arista)
        
        # Guardar el grafo en un archivo y generar la visualización
    grafico.format = 'png'  # Formato de salida (puedes cambiarlo a SVG, PDF, etc.)
    grafico.render('grafo_videojuegos')
    
    # Cargar la imagen del gráfico utilizando PIL
    imagen_grafico = Image.open('grafo_videojuegos.png')
    imagen_grafico = imagen_grafico.resize((800, 100))  # Ajustar el tamaño de la imagen si es necesario

    # Mostrar la imagen en la etiqueta
    imagen_tk = ImageTk.PhotoImage(imagen_grafico)
    etiqueta_grafico.configure(image=imagen_tk)
    etiqueta_grafico.image = imagen_tk  # Actualizar la referencia de la imagen para evitar 

def obtener_recomendaciones():
    global nro_juegos
    
    nombre_inicio = entry_juego_partida.get()
    plataforma_deseada = entry_plataforma.get()
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
        videojuegos_cercanos = dijkstra(grafo, inicio, plataforma_deseada)

        # Imprimir los resultados
        # texto_recomendaciones.delete(1.0, tk.END)  # Borra el contenido previo
        # texto_recomendaciones.insert(tk.END, f"Los 10 videojuegos más cercanos en relación al peso para la plataforma {plataforma_deseada}:\n")
        # for juego, distancia in videojuegos_cercanos:
        #     texto_recomendaciones.insert(tk.END, f"Videojuego {grafo.nodos[juego]['label']}: {grafo.nodos[juego]['name']}, Distancia: {distancia}\n")
            
        boton_obtener_grafico = tk.Button(frame_entrada, text="Obtener grafico", command=obtener_Grafico, font=font_style)
        boton_obtener_grafico.grid(row=6, column=1, padx=5, pady=5)
        
        mostrar_resultados(videojuegos_cercanos, plataforma_deseada, nro_juegos)
        
# Función para mostrar los juegos recomendados como "cards"
def mostrar_resultados(videojuegos_cercanos, plataforma_deseada, nro_juegos):
    # Borrar el contenido previo
    for widget in frame_canvas.winfo_children():
        widget.destroy()

    # Crear el Canvas
    canvas = tk.Canvas(frame_canvas, bg="#f1d4af", height=600, width=550)
    canvas.pack(side="left", fill="both", expand=True)

    # Crear el Scrollbar
    scrollbar = tk.Scrollbar(frame_canvas, command=canvas.yview)
    scrollbar.pack(side="right", fill="y")

    # Configurar el Canvas para que funcione con el Scrollbar
    canvas.configure(yscrollcommand=scrollbar.set)

    # Crear un Frame para el ListView dentro del Canvas
    frame_listview = tk.Frame(canvas, bg="#f1d4af")
    canvas.create_window((0, 0), window=frame_listview, anchor="nw")

    # Crear la etiqueta para el mensaje
    mensaje = tk.Label(frame_listview, text=f"Los {nro_juegos} videojuegos más cercanos en relación al peso para la plataforma {plataforma_deseada}:", font=font_style)
    mensaje.pack()

    # Mostrar los juegos en el Listbox
    colores = ["#f2e8c4", "#98d9b6", "#3ec9a7", "#2b879e", "#00FF00", "#616668"]
    num_colores = len(colores)

    for i, (juego, distancia) in enumerate(videojuegos_cercanos[:nro_juegos]):
        color = colores[i % num_colores]
        frame_juego = tk.Frame(frame_listview, bg=color, padx=10, pady=10, relief="raised")
        frame_juego.pack(padx=10, pady=10)

        # Label para mostrar el nombre del juego
        label_nombre = tk.Label(frame_juego, text=grafo.nodos[juego]['name'], font=font_style, bg=color)
        label_nombre.pack()

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

# Ejemplo de uso
grafo = Grafo()

df = pd.read_csv('Dataset_Videogames.csv', delimiter=';')

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

plataformas = []  # Lista para almacenar las plataformas sin repetirse

def actualizar_lista_platforms():
    # Limpiar la lista de plataformas
    lista_platform.delete(0, tk.END)
    
    # Recorrer los nodos y obtener las plataformas únicas
    for nodo in grafo.nodos:
        plataforma = grafo.nodos[nodo]['platform']
        if plataforma not in plataformas:
            plataformas.append(plataforma)
    
    # Insertar las plataformas en la lista
    for plataforma in plataformas:
        lista_platform.insert(tk.END, plataforma)

def seleccionar_platforms(event):
    # Obtener la plataforma seleccionada en la lista
    plataforma_seleccionada = lista_platform.get(lista_platform.curselection())
    
    # Establecer la plataforma seleccionada en el entry
    entry_plataforma.delete(0, tk.END)
    entry_plataforma.insert(tk.END, plataforma_seleccionada)


# Crear la ventana principal
ventana = tk.Tk()
ventana.title("Sistema de Recomendación de Juegos")

# Cargar la imagen de fondo
ventana.configure(background='#c5e0dc', height= 100)

# Cambiar el font de las letras
font_style = font.Font(family="Helvetica", size=12)

frame_entrada = tk.Frame(ventana, bg=ventana["bg"])
frame_entrada.pack(pady=10)

# Etiqueta y entrada para el juego de partida
label_juego_partida = tk.Label(frame_entrada, text="Juego de partida:", font=font_style, bg=ventana["bg"], fg='#774f38', highlightthickness=0)
label_juego_partida.grid(row=0, column=0, padx=5, pady=5)
entry_juego_partida = tk.Entry(frame_entrada, font=font_style, bg="#f1d4af", fg='#774f38', width=40)
entry_juego_partida.grid(row=0, column=1, padx=5, pady=5)

entry_juego_partida.bind("<KeyRelease>", actualizar_lista)

lista_juegos = tk.Listbox(frame_entrada, width=60)
lista_juegos.grid(row=1, column=1, padx=3,pady=3)

lista_juegos.bind("<<ListboxSelect>>", seleccionar_juego)

# Etiqueta y entrada para la plataforma
label_plataforma = tk.Label(frame_entrada, text="Plataforma:", font=font_style, bg=ventana["bg"], fg='#774f38', highlightthickness=0)
label_plataforma.grid(row=2, column=0, padx=10, pady=10)
entry_plataforma = tk.Entry(frame_entrada, font=font_style, bg="#f1d4af", fg='#774f38', width=40)
entry_plataforma.grid(row=2, column=1, padx=10, pady=10)

lista_platform = tk.Listbox(frame_entrada, width=60)
lista_platform.grid(row=3, column=1, padx=3,pady=3)

actualizar_lista_platforms()

lista_platform.bind("<<ListboxSelect>>", seleccionar_platforms)

# Etiqueta y entrada para numero de juegos 
label_nrojuegos = tk.Label(frame_entrada, text="Nro de juegos:", font=font_style, bg=ventana["bg"], fg='#774f38', highlightthickness=0)
label_nrojuegos.grid(row=4, column=0, padx=10, pady=10)
entry_nrojuegos = tk.Entry(frame_entrada, font=font_style, bg="#f1d4af", fg='#774f38', width=40)
entry_nrojuegos.grid(row=4, column=1, padx=10, pady=10)

# Botón para obtener las recomendaciones
boton_obtener_recomendaciones = tk.Button(frame_entrada, text="Obtener Recomendaciones", command=obtener_recomendaciones, font=font_style, bg="#f1d4af", fg='#774f38', highlightthickness=0)
boton_obtener_recomendaciones.grid(row=5, column=1, padx=10, pady=10)

# Etiqueta para mostrar el gráfico
etiqueta_grafico = tk.Label(frame_entrada, bg="#f1d4af")
etiqueta_grafico.grid(row=6, column=0, padx=10, pady=10)

# Crear el Frame contenedor para el Canvas y el Scrollbar
frame_canvas = tk.Frame(frame_entrada, bg="#f1d4af")
frame_canvas.grid(row=0, column=3,padx=10, pady=10, rowspan=7)

# Ejecutar el bucle principal de la interfaz
ventana.mainloop()