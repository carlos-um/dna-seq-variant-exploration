import csv  # Import CSV library for reading CSV files
from pathlib import Path  # Import Path for handling file and directory paths

class Phenotype:
    """Structures phenotype information including its code, label, and URI. 
       Also stores genes associated with this phenotype"""
    
    def __init__(self, code, label, uri):  # Constructor that initializes the main attributes of the phenotype
        self.code = code
        self.label = label
        self.uri = uri
        self.genes = set()

    def add_gene(self, gene):
        """Adds a gene to the set of genes associated with this phenotype"""
        self.genes.add(gene)

    def gene_count(self):
        """Returns the total number of genes associated with this phenotype"""
        return len(self.genes)

class Patient:
    """Represents a patient identified by their record, including associated phenotypes and variants"""
    
    def __init__(self, record):
        self.record = record
        self.phenotypes = []  # List of phenotypes associated with the patient
        self.variants = []  # List of genetic variants associated with the patient

    def add_phenotype(self, phenotype):
        """Adds a phenotype to the patient's phenotype list"""
        self.phenotypes.append(phenotype)

    def add_variant(self, variant):
        """Adds a variant to the patient's variant list"""
        self.variants.append(variant)

    def variant_count(self):
        """Returns the number of variants associated with the patient"""
        return len(self.variants)

class Variant:
    """Represents a genetic variant with its specific characteristics"""
    
    def __init__(self, patient_id, chr, pos_start, pos_end, reference, genotype, gene_symbol):
        self.patient_id = patient_id
        self.chr = chr
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.reference = reference
        self.genotype = genotype
        self.gene_symbol = gene_symbol

class DataManager:
    """Class to manage loading and manipulation of phenotype, patient, and variant data"""
    
    def __init__(self, phenotypes_path, patients_path, variants_dir):
        self.phenotypes = {}
        self.patients = {}
        self.variants = []
        self.load_phenotypes(phenotypes_path)
        self.load_patients(patients_path)
        self.load_variants(variants_dir)

    def load_phenotypes(self, file_path):
        """Loads phenotypes from a CSV file"""
        
        try:  # Try to load the data, catch any errors
            with open(file_path, mode='r') as csv_file:  # Open the file in read mode
                csv_reader = csv.DictReader(csv_file, delimiter=';')  # Read the file as a dictionary
                for row in csv_reader:  # Iterate over each row in the file
                    code = row["codigo"]  # Extract the phenotype code
                    if code not in self.phenotypes:  # If the phenotype is not already in the dictionary
                        phenotype = Phenotype(code, row["label"], row["uri"])  # Create a new Phenotype instance
                        self.phenotypes[code] = phenotype  # Add the phenotype to the dictionary
                    self.phenotypes[code].add_gene(row["gene"])  # Add the associated gene to the phenotype
        except FileNotFoundError:  # Error handling if file is not found
            print(f"File {file_path} not found. Please verify the path.")
        except Exception as e:  # Handle other loading errors
            print(f"Error loading phenotypes: {e}")

    def load_patients(self, file_path):
        """Loads patients from a CSV file"""
        
        try:
            with open(file_path, mode='r') as csv_file:
                csv_reader = csv.DictReader(csv_file, delimiter=';')
                for row in csv_reader:
                    record = row["expediente"]
                    if record not in self.patients:
                        self.patients[record] = Patient(record)
                    phenotype = self.phenotypes.get(row["fenotipo"])
                    if phenotype:
                        self.patients[record].add_phenotype(phenotype)
        except FileNotFoundError:
            print(f"File {file_path} not found. Please verify the path.")
        except Exception as e:
            print(f"Error loading patients: {e}")

    def load_variants(self, directory_path):
        """Loads variants from CSV files in a directory"""
        
        directory = Path(directory_path)  # Define the directory
        for file_path in directory.glob("PAC*.csv"):  # Find files starting with PAC and ending with .csv
            try:
                with file_path.open(mode='r') as csv_file:
                    csv_reader = csv.DictReader(csv_file, delimiter=';')
                    patient_id = file_path.stem  # Get the filename without extension as patient ID
                    for row in csv_reader:
                        variant = Variant(
                            patient_id, row["chr"], int(row["pos_start"]),
                            int(row["pos_end"]), row["reference"], row["genotype"],
                            row["gene_symbol"])
                        self.variants.append(variant)
                        if patient_id in self.patients:
                            self.patients[patient_id].add_variant(variant)
            except FileNotFoundError:
                print(f"File {file_path.name} not found. Please verify the folder and file names.")
            except Exception as e:
                print(f"Error loading variants for patient {file_path.stem}: {e}")

def show_menu(data_manager):
    """Displays the main menu and manages user interaction"""
    
    while True:  # Loop that keeps the menu open until the user decides to exit
        print("\n1. List patients")
        print("2. List genes")
        print("3. List phenotypes")
        print("4. Exit program")
        option = input("Choose an option (1-4): ")  # Prompt the user for an option
        
        # Call functions based on the chosen option
        if option == "1":
            list_patients(data_manager)
        elif option == "2":
            list_genes(data_manager)
        elif option == "3":
            list_phenotypes(data_manager)
        elif option == "4":
            print("Program terminated")
            break
        else:
            print("ERROR. You must enter a number between 1 and 4.")

def list_patients(data_manager):
    """Lists patients indicating the number of genetic variants they have and their phenotypes"""
    
    for patient in data_manager.patients.values():  # Iterate over each patient in the dictionary
        print(f"{patient.record} (Variants: {patient.variant_count()})")  # Print record and variant count
        for phenotype in patient.phenotypes:  # For each phenotype associated with the patient
            print(f"  - {phenotype.label} ({phenotype.code}) [Gene Count: {phenotype.gene_count()}]")  # Print phenotype info
        print()  # Print a blank line to separate each patient
    patient_submenu(data_manager)  # Call the submenu for patient-specific options

def patient_submenu(data_manager):
    """Submenu for patient options that allows searching and recommending variants"""
    
    while True:  # Loop to keep the submenu active until "Go back" is chosen
        print("\n1. Search variants")
        print("2. Recommend variants")
        print("3. Go back")
        option = input("Choose an option (1-3): ")  # Prompt the user for an option
        
        # Call functions based on the chosen option
        if option == "1":
            search_variants(data_manager)
        elif option == "2":
            recommend_variants(data_manager)
        elif option == "3":
            break  # Return to main menu
        else:
            print("ERROR. You must enter a number between 1 and 3 in the submenu.")

def list_genes(data_manager):
    """Lists all genes associated with variants"""
    
    gene_count = {}  # Dictionary to count the number of occurrences of each gene
    for variant in data_manager.variants:  # Iterate over each variant in the variant list
        if variant.gene_symbol in gene_count:  # If the gene is already in the dictionary, increment counter
            gene_count[variant.gene_symbol] += 1
        else:  # If the gene is not in the dictionary, add it with initial count of 1
            gene_count[variant.gene_symbol] = 1
    for gene, count in gene_count.items():  # Iterate over each gene and its count in the dictionary
        print(f"{gene} ({count})")  # Print the gene name and number of occurrences

def list_phenotypes(data_manager):
    """Function to list all phenotypes with their gene count"""
    
    for phenotype in data_manager.phenotypes.values():  # Iterate over each phenotype in the dictionary
        print(f"{phenotype.label} ({phenotype.code}) [Gene Count: {phenotype.gene_count()}]")  # Print label, code, and gene count

def search_variants(data_manager):
    """Searches for variants based on patient code, chromosome, start and end position, and gene"""
    
    patient_code = input("Patient code: ")
    chromosome = input("Chromosome: ")
    pos_start = input("Start position: ")
    pos_end = input("End position: ")
    gene = input("Gene: ")

    for variant in data_manager.variants:  # Iterate over each variant in the variant list
        # Check each criterion entered by the user, if it doesn't match continue to the next
        if (patient_code and variant.patient_id != patient_code) or \
           (chromosome and variant.chr != chromosome) or \
           (pos_start and variant.pos_start < int(pos_start)) or \
           (pos_end and variant.pos_end > int(pos_end)) or \
           (gene and variant.gene_symbol != gene):
            continue
        print(f"{variant.chr}:{variant.pos_start}:{variant.pos_end}:{variant.reference}:{variant.genotype} ({variant.gene_symbol})")

def recommend_variants(data_manager):
    """Recommends variants based on a patient's phenotypes"""
    
    patient_code = input("Patient code: ")  # Prompt for patient code
    patient = data_manager.patients.get(patient_code)  # Look up the patient in the dictionary

    if not patient:  # If patient is not found, display a message and return to submenu
        print("Patient not found")
        return

    relevant_genes = set()  # Create a set to store relevant genes based on the patient's phenotypes

    for phenotype in patient.phenotypes:  # Iterate over each phenotype of the patient
        relevant_genes.update(phenotype.genes)  # Add genes from each phenotype to the relevant genes set

    for variant in patient.variants:  # Iterate over each variant of the patient
        if variant.gene_symbol in relevant_genes:  # If the variant's gene is in the relevant genes, display it
            print(f"{variant.chr}:{variant.pos_start}:{variant.pos_end}:{variant.reference}:{variant.genotype} ({variant.gene_symbol})")

def main():
    """Loads data and calls the main menu"""
    
    # File paths (generic paths for accessibility)
    phenotypes_path = "path/to/your/phenotypes_metadata.csv"
    patients_path = "path/to/your/patients_metadata.csv"
    variants_dir = "path/to/your/VCFS"
    
    # Create a DataManager instance with the specified files and directory
    data_manager = DataManager(phenotypes_path, patients_path, variants_dir)
    show_menu(data_manager)
    
# Call main() if the script is executed directly
if __name__ == "__main__":
    main()  # Call the main function to start the program
