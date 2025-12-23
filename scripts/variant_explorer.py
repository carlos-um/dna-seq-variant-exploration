import csv # Importamos la librería CSV para leer los archivos CSV
from pathlib import Path # Importamos Path para manejar rutas de archivos y directorios

class Fenotipo:
    """Permite estructurar la información de un fenotipo, que incluye su código,label y URI. 
       También almacena los genes asociados a este fenotipo"""
    
    def __init__(self, codigo, label, uri): # Constructor que inicializa los atributos principales del fenotipo
        self.codigo = codigo
        self.label = label
        self.uri = uri
        self.genes = set()

    def add_gene(self, gene):
        """Añade un gen al conjunto de genes asociados a este fenotipo"""
        self.genes.add(gene)

    def gene_count(self):
        """Devuelve el número total de genes asociados a este fenotipo"""
        return len(self.genes)

class Paciente:
    """Representa un paciente identificado por su expediente, incluyendo sus fenotipos y variantes asociadas"""
    
    def __init__(self, expediente):
        self.expediente = expediente
        self.fenotipos = []  # Lista de fenotipos asociados al paciente
        self.variantes = []  # Lista de variantes genicas asociadas al paciente

    def add_fenotipo(self, fenotipo):
        """Añade un fenotipo a la lista de fenotipos del paciente"""
        self.fenotipos.append(fenotipo)

    def add_variante(self, variante):
        """Añade una variante a la lista de variantes del paciente"""
        self.variantes.append(variante)

    def variante_count(self):
        """Devuelve el número de variantes asociadas al paciente"""
        return len(self.variantes)

class Variante:
    """Representa una variante genica con sus características específicas"""
    
    def __init__(self, paciente_id, chr, pos_start, pos_end, reference, genotype, gene_symbol):
        self.paciente_id = paciente_id
        self.chr = chr
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.reference = reference
        self.genotype = genotype
        self.gene_symbol = gene_symbol

class DataManager:
    """Clase para gestionar la carga y manipulación de los datos de fenotipos, pacientes y variantes"""
    
    def __init__(self, fenotipos_path, pacientes_path, variantes_dir):
        self.fenotipos = {}
        self.pacientes = {}
        self.variantes = []
        self.load_fenotipos(fenotipos_path)
        self.load_pacientes(pacientes_path)
        self.load_variantes(variantes_dir)

    def load_fenotipos(self, file_path):
        """Carga los fenotipos desde un archivo CSV"""
        
        try: # Prueba a cargar los datos, excepto que de error
            with open(file_path, mode='r') as csv_file: # Abre el archivo en modo lectura
                csv_reader = csv.DictReader(csv_file, delimiter=';') # Lee el archivo como un diccionario
                for row in csv_reader: # Itera sobre cada fila del archivo
                    codigo = row["codigo"] # Extrae el código del fenotipo
                    if codigo not in self.fenotipos: # Si el fenotipo no está ya en el diccionario
                        fenotipo = Fenotipo(codigo, row["label"], row["uri"]) # Crea una nueva instancia de Fenotipo
                        self.fenotipos[codigo] = fenotipo # Añade el fenotipo al diccionario
                    self.fenotipos[codigo].add_gene(row["gene"]) # Añade el gen asociado al fenotipo
        except FileNotFoundError: # Control de errores si no se encuentra el archivo
            print(f"Archivo {file_path} no encontrado. Verifica la ruta.")
        except Exception as e: # Control del resto de errores de carga
            print(f"Error al cargar fenotipos: {e}")

    def load_pacientes(self, file_path): #La explicación es la misma que cuando he cargado los fenotipos
        """Carga los pacientes desde un archivo CSV"""
        
        try:
            with open(file_path, mode='r') as csv_file:
                csv_reader = csv.DictReader(csv_file, delimiter=';')
                for row in csv_reader:
                    expediente = row["expediente"]
                    if expediente not in self.pacientes:
                        self.pacientes[expediente] = Paciente(expediente)
                    fenotipo = self.fenotipos.get(row["fenotipo"])
                    if fenotipo:
                        self.pacientes[expediente].add_fenotipo(fenotipo)
        except FileNotFoundError:
            print(f"Archivo {file_path} no encontrado. Verifica la ruta.")
        except Exception as e:
            print(f"Error al cargar pacientes: {e}")

    def load_variantes(self, directory_path): #La carga de variantes es algo distinta porque hay que leer mas de un archivo CSV. Solo comentaré las partes que sean distintas
        """Carga las variantes desde los archivos CSV de un directorio"""
        
        directory = Path(directory_path) # Define el directorio
        for file_path in directory.glob("PAC*.csv"): # Busca archivos que comienzan con PAC y acaban por .csv
            try:
                with file_path.open(mode='r') as csv_file:
                    csv_reader = csv.DictReader(csv_file, delimiter=';')
                    paciente_id = file_path.stem # Obtiene el nombre del archivo sin extensión como ID del paciente
                    for row in csv_reader:
                        variante = Variante(
                            paciente_id, row["chr"], int(row["pos_start"]),
                            int(row["pos_end"]), row["reference"], row["genotype"],
                            row["gene_symbol"])
                        self.variantes.append(variante)
                        if paciente_id in self.pacientes:
                            self.pacientes[paciente_id].add_variante(variante)
            except FileNotFoundError:
                print(f"Archivo {file_path.name} no encontrado. Verifica la carpeta y los nombres.")
            except Exception as e:
                print(f"Error al cargar variantes del paciente {file_path.stem}: {e}")

def mostrar_menu(data_manager):
    """Muestra el menú principal y gestiona la interacción con el usuario"""
    
    while True: # Bucle que mantiene el menú abierto hasta que el usuario decida salir
        print("\n1. Listar pacientes")
        print("2. Listar genes")
        print("3. Listar fenotipos")
        print("4. Salir del programa")
        opcion = input("Elija una opción (1-4): ") # Solicita al usuario una opción
        
        # Llama a funciones según la opción elegida
        if opcion == "1":
            listar_pacientes(data_manager)
        elif opcion == "2":
            listar_genes(data_manager)
        elif opcion == "3":
            listar_fenotipos(data_manager)
        elif opcion == "4":
            print("Programa finalizado")
            break
        else:
            print("ERROR. Debe definir un número entre 1 y 4.")

def listar_pacientes(data_manager):
    """Lista los pacientes indicando el numero de variantes genicas que presentan y sus fenotipos""" 
    
    for paciente in data_manager.pacientes.values(): # Itera sobre cada paciente en el diccionario
        print(f"{paciente.expediente} (Variantes: {paciente.variante_count()})") # Imprime el expediente y el número de variantes
        for fenotipo in paciente.fenotipos: # Para cada fenotipo asociado al paciente
            print(f"  - {fenotipo.label} ({fenotipo.codigo}) [Nº Genes: {fenotipo.gene_count()}]") # Imprime información del fenotipo
        print() # Imprime una línea en blanco para separar cada paciente
    submenu_pacientes(data_manager) # Llama al submenú de opciones específicas para pacientes

def submenu_pacientes(data_manager):
    """Submenú para opciones de pacientes que permite buscar y recomendar variantes"""
    
    while True: # Bucle para mantener el submenú activo hasta que se elija "Volver atrás"
        print("\n1. Buscar variantes")
        print("2. Recomendar variantes")
        print("3. Volver atrás")
        opcion = input("Elija una opción (1-3): ") # Solicita al usuario una opción
        
        # Llama a funciones según la opción elegida
        if opcion == "1":
            buscar_variantes(data_manager)
        elif opcion == "2":
            recomendar_variantes(data_manager)
        elif opcion == "3":
            break  # Volver al menú principal
        else:
            print("ERROR. Debe definir un número entre 1 y 3 del submenú.")

def listar_genes(data_manager):
    """Lista todos los genes asociados a variantes"""
    
    gene_count = {}  # Diccionario para contar la cantidad de ocurrencias de cada gen
    for variante in data_manager.variantes: # Itera sobre cada variante en la lista de variantes
        if variante.gene_symbol in gene_count: # Si el gen ya está en el diccionario, incrementa el contador
            gene_count[variante.gene_symbol] += 1
        else: # Si el gen no está en el diccionario, lo añade con un contador inicial de 1
            gene_count[variante.gene_symbol] = 1
    for gene, count in gene_count.items(): # Itera sobre cada gen y su cantidad en el diccionario
        print(f"{gene} ({count})") # Imprime el nombre del gen y la cantidad de ocurrencias

def listar_fenotipos(data_manager):
    """Función para listar todos los fenotipos con su número de genes"""
    
    for fenotipo in data_manager.fenotipos.values(): # Itera sobre cada fenotipo en el diccionario
        print(f"{fenotipo.label} ({fenotipo.codigo}) [Nº Genes: {fenotipo.gene_count()}]") # Imprime label, código y número de genes

def buscar_variantes(data_manager):
    """Busca variantes en base al código del paciente, cromosoma, posición de inicio y fin y gene"""
    
    codigo_paciente = input("Código de paciente: ")
    cromosoma = input("Cromosoma: ")
    pos_start = input("Posición Inicio: ")
    pos_end = input("Posición Fin: ")
    gene = input("Gene: ")

    for variante in data_manager.variantes:  # Itera sobre cada variante en la lista de variantes
        # Comprueba cada criterio introducido por el usuario, si no coincide continúa al siguiente
        if (codigo_paciente and variante.paciente_id != codigo_paciente) or \
           (cromosoma and variante.chr != cromosoma) or \
           (pos_start and variante.pos_start < int(pos_start)) or \
           (pos_end and variante.pos_end > int(pos_end)) or \
           (gene and variante.gene_symbol != gene):
            continue
        print(f"{variante.chr}:{variante.pos_start}:{variante.pos_end}:{variante.reference}:{variante.genotype} ({variante.gene_symbol})")

def recomendar_variantes(data_manager):
    """Recomienda variantes basadas en los fenotipos de un paciente"""
    
    codigo_paciente = input("Código de paciente: ") # Solicita el código de paciente
    paciente = data_manager.pacientes.get(codigo_paciente) # Busca el paciente en el diccionario

    if not paciente: # Si el paciente no se encuentra, muestra un mensaje y vuelve al submenu
        print("Paciente no encontrado")
        return

    genes_relevantes = set() # Crea un conjunto para almacenar genes relevantes según los fenotipos del paciente

    for fenotipo in paciente.fenotipos:  # Itera sobre cada fenotipo del paciente
        genes_relevantes.update(fenotipo.genes) # Añade los genes de cada fenotipo al conjunto de genes relevantes

    for variante in paciente.variantes: # Itera sobre cada variante del paciente
        if variante.gene_symbol in genes_relevantes:  # Si el gen de la variante está en los genes relevantes, la muestra
            print(f"{variante.chr}:{variante.pos_start}:{variante.pos_end}:{variante.reference}:{variante.genotype} ({variante.gene_symbol})")

def main():
    """Carga los datos y llama al menú principal"""
    
    # Rutas de los archivos
    fenotipos_path = "/home/alumno25/SistemasBioinformaticos/Bloque3/data_practica1/fenotipos_metadatos.csv"
    pacientes_path = "/home/alumno25/SistemasBioinformaticos/Bloque3/data_practica1/pacientes_metadatos.csv"
    variantes_dir = "/home/alumno25/SistemasBioinformaticos/Bloque3/data_practica1/VCFS"
    
    # Crea una instancia de DataManager con los archivos y directorio especificados
    data_manager = DataManager(fenotipos_path, pacientes_path, variantes_dir)
    mostrar_menu(data_manager)
    
# Llamada a main() si el script se ejecuta directamente
if __name__ == "__main__":
    main() # Llama a la función principal para iniciar el programa
