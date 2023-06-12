class Grafo:
    def __init__(self):
        self.nodos = {}
        self.aristas = {}

    def agregar_nodo(self, id, label=None, name=None, platform=None, year=None, genre=None, publisher=None):
        self.nodos[id] = {
            'label': label,
            'name': name,
            'platform': platform,
            'year': year,
            'genre': genre,
            'publisher': publisher
        }
        self.aristas[id] = {}

    def agregar_arista(self, id_origen, id_destino, peso):
        self.aristas[id_origen][id_destino] = peso
        self.aristas[id_destino][id_origen] = peso

    def obtener_nodos(self):
        return self.nodos.keys()

    def obtener_aristas(self):
        aristas = []
        for id_origen in self.aristas:
            for id_destino in self.aristas[id_origen]:
                if (id_destino, id_origen) not in aristas:
                    aristas.append((id_origen, id_destino, self.aristas[id_origen][id_destino]))
        return aristas