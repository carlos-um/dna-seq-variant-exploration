import csv  # Import CSV library for reading CSV files
from pathlib import Path  # Import Path for handling file and directory paths

class Fenotipo:
    """Structures phenotype information including its code, label, and URI. 
       Also stores genes associated with this phenotype"""
    
    def __init__(self, codigo, label, uri):  # Constructor that initializes the main attributes of the phenotype
        self.codigo = codigo
        self.label = label
        self.uri = uri
        self.genes = set()

    def add_gene(self, gene):
        """Adds a gene to the set of genes associated with this phenotype"""
        self.genes.add(gene)

    def gene_count(self):
        """Returns the total number of genes associated with this phenotype"""
        return len(self.genes)

class Paciente:
    """Represents a patient identified by their record, including associated phenotypes and variants"""
    
    def __init__(self, expediente):
        self.expediente = expediente
        self.fenotipos = []  # List of phenotypes associated with the patient
        self.variantes = []  # List of genetic variants associated with the patient

    def add_fenotipo(self, fenotipo):
        """Adds a phenotype to the patient's phenotype list"""
        self.fenotipos.append(fenotipo)

    def add_variante(self, variante):
        """Adds a variant to the patient's variant list"""
        self.variantes.append(variante)

    def variante_count(self):
        """Returns the number of variants associated with the patient"""
        return len(self.variantes)

class Variante:
    """Represents a genetic variant with its specific characteristics"""
    
    def __init__(self, paciente_id, chr, pos_start, pos_end, reference, genotype, gene_symbol):
        self.paciente_id = paciente_id
        self.chr = chr
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.reference = reference
        self.genotype = genotype
        self.gene_symbol = gene_symbol

class DataManager:
    """Class to manage loading and manipulation of phenotype, patient, and variant data"""
    
    def __init__(self, fenotipos_path, pacientes_path, variantes_dir):
        self.fenotipos = {}
        self.pacientes = {}
        self.variantes = []
        self.load_fenotipos(fenotipos_path)
        self.load_pacientes(pacientes_path)
        self.load_variantes(variantes_dir)

    def load_fenotipos(self, file_path):
        """Loads phenotypes from a CSV file"""
        
        try:  # Try to load the data, catch any errors
            with open(file_path, mode='r') as csv_file:  # Open the file in read mode
                csv_reader = csv.DictReader(csv_file, delimiter=';')  # Read the file as a dictionary
                for row in csv_reader:  # Iterate over each row in the file
                    codigo = row["codigo"]  # Extract the phenotype code
                    if codigo not in self.fenotipos:  # If the phenotype is not already in the dictionary
                        fenotipo = Fenotipo(codigo, row["label"], row["uri"])  # Create a new Fenotipo instance
                        self.fenotipos[codigo] = fenotipo  # Add the phenotype to the dictionary
                    self.fenotipos[codigo].add_gene(row["gene"])  # Add the associated gene to the phenotype
        except FileNotFoundError:  # Error handling if file is not found
            print(f"File {file_path} not found. Please verify the path.")
        except Exception as e:  # Handle other loading errors
            print(f"Error loading phenotypes: {e}")

    def load_pacientes(self, file_path):
        """Loads patients from a CSV file"""
        
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
            print(f"File {file_path} not found. Please verify the path.")
        except Exception as e:
            print(f"Error loading patients: {e}")

    def load_variantes(self, directory_path):
        """Loads variants from CSV files in a directory"""
        
        directory = Path(directory_path)  # Define the directory
        for file_path in directory.glob("PAC*.csv"):  # Find files starting with PAC and ending with .csv
            try:
                with file_path.open(mode='r') as csv_file:
                    csv_reader = csv.DictReader(csv_file, delimiter=';')
                    paciente_id = file_path.stem  # Get the filename without extension as patient ID
                    for row in csv_reader:
                        variante = Variante(
                            paciente_id, row["chr"], int(row["pos_start"]),
                            int(row["pos_end"]), row["reference"], row["genotype"],
                            row["gene_symbol"])
                        self.variantes.append(variante)
                        if paciente_id in self.pacientes:
                            self.pacientes[paciente_id].add_variante(variante)
            except FileNotFoundError:
                print(f"File {file_path.name} not found. Please verify the folder and file names.")
            except Exception as e:
                print(f"Error loading variants for patient {file_path.stem}: {e}")

def mostrar_menu(data_manager):
    """Displays the main menu and manages user interaction"""
    
    while True:  # Loop that keeps the menu open until the user decides to exit
        print("\n1. List patients")
        print("2. List genes")
        print("3. List phenotypes")
        print("4. Exit program")
        opcion = input("Choose an option (1-4): ")  # Prompt the user for an option
        
        # Call functions based on the chosen option
        if opcion == "1":
            listar_pacientes(data_manager)
        elif opcion == "2":
            listar_genes(data_manager)
        elif opcion == "3":
            listar_fenotipos(data_manager)
        elif opcion == "4":
            print("Program terminated")
            break
        else:
            print("ERROR. You must enter a number between 1 and 4.")

def listar_pacientes(data_manager):
    """Lists patients indicating the number of genetic variants they have and their phenotypes"""
    
    for paciente in data_manager.pacientes.values():  # Iterate over each patient in the dictionary
        print(f"{paciente.expediente} (Variants: {paciente.variante_count()})")  # Print record and variant count
        for fenotipo in paciente.fenotipos:  # For each phenotype associated with the patient
            print(f"  - {fenotipo.label} ({fenotipo.codigo}) [Gene Count: {fenotipo.gene_count()}]")  # Print phenotype info
        print()  # Print a blank line to separate each patient
    submenu_pacientes(data_manager)  # Call the submenu for patient-specific options

def submenu_pacientes(data_manager):
    """Submenu for patient options that allows searching and recommending variants"""
    
    while True:  # Loop to keep the submenu active until "Go back" is chosen
        print("\n1. Search variants")
        print("2. Recommend variants")
        print("3. Go back")
        opcion = input("Choose an option (1-3): ")  # Prompt the user for an option
        
        # Call functions based on the chosen option
        if opcion == "1":
            buscar_variantes(data_manager)
        elif opcion == "2":
            recomendar_variantes(data_manager)
        elif opcion == "3":
            break  # Return to main menu
        else:
            print("ERROR. You must enter a number between 1 and 3 in the submenu.")

def listar_genes(data_manager):
    """Lists all genes associated with variants"""
    
    gene_count = {}  # Dictionary to count the number of occurrences of each gene
    for variante in data_manager.variantes:  # Iterate over each variant in the variant list
        if variante.gene_symbol in gene_count:  # If the gene is already in the dictionary, increment counter
            gene_count[variante.gene_symbol] += 1
        else:  # If the gene is not in the dictionary, add it with initial count of 1
            gene_count[variante.gene_symbol] = 1
    for gene, count in gene_count.items():  # Iterate over each gene and its count in the dictionary
        print(f"{gene} ({count})")  # Print the gene name and number of occurrences

def listar_fenotipos(data_manager):
    """Function to list all phenotypes with their gene count"""
    
    for fenotipo in data_manager.fenotipos.values():  # Iterate over each phenotype in the dictionary
        print(f"{fenotipo.label} ({fenotipo.codigo}) [Gene Count: {fenotipo.gene_count()}]")  # Print label, code, and gene count

def buscar_variantes(data_manager):
    """Searches for variants based on patient code, chromosome, start and end position, and gene"""
    
    codigo_paciente = input("Patient code: ")
    cromosoma = input("Chromosome: ")
    pos_start = input("Start position: ")
    pos_end = input("End position: ")
    gene = input("Gene: ")

    for variante in data_manager.variantes:  # Iterate over each variant in the variant list
        # Check each criterion entered by the user, if it doesn't match continue to the next
        if (codigo_paciente and variante.paciente_id != codigo_paciente) or \
           (cromosoma and variante.chr != cromosoma) or \
           (pos_start and variante.pos_start < int(pos_start)) or \
           (pos_end and variante.pos_end > int(pos_end)) or \
           (gene and variante.gene_symbol != gene):
            continue
        print(f"{variante.chr}:{variante.pos_start}:{variante.pos_end}:{variante.reference}:{variante.genotype} ({variante.gene_symbol})")

def recomendar_variantes(data_manager):
    """Recommends variants based on a patient's phenotypes"""
    
    codigo_paciente = input("Patient code: ")  # Prompt for patient code
    paciente = data_manager.pacientes.get(codigo_paciente)  # Look up the patient in the dictionary

    if not paciente:  # If patient is not found, display a message and return to submenu
        print("Patient not found")
        return

    relevant_genes = set()  # Create a set to store relevant genes based on the patient's phenotypes

    for fenotipo in paciente.fenotipos:  # Iterate over each phenotype of the patient
        relevant_genes.update(fenotipo.genes)  # Add genes from each phenotype to the relevant genes set

    for variante in paciente.variantes:  # Iterate over each variant of the patient
        if variante.gene_symbol in relevant_genes:  # If the variant's gene is in the relevant genes, display it
            print(f"{variante.chr}:{variante.pos_start}:{variante.pos_end}:{variante.reference}:{variante.genotype} ({variante.gene_symbol})")

def main():
    """Loads data and calls the main menu"""
    
    # File paths (generic paths for accessibility)
    fenotipos_path = "path/to/your/fenotipos_metadatos.csv"
    pacientes_path = "path/to/your/pacientes_metadatos.csv"
    variantes_dir = "path/to/your/VCFS"
    
    # Create a DataManager instance with the specified files and directory
    data_manager = DataManager(fenotipos_path, pacientes_path, variantes_dir)
    mostrar_menu(data_manager)
    
# Call main() if the script is executed directly
if __name__ == "__main__":
    main()  # Call the main function to start the program
