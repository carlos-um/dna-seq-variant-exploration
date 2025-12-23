# DNA-SEQ Variant Explorer

## Overview

This Python program allows loading, exploring, and analyzing DNA-SEQ variant data from CSV files. It is designed to handle:

- Patient metadata and their associated phenotypes.
- Variant information for each patient.
- Phenotype-to-gene associations.

Users can:

1. List patients with their phenotypes and the number of variants.  
2. List all genes sequenced and the variants found in each.  
3. List all phenotypes and the number of genes regulating them.  
4. Filter variants by patient, gene, chromosome, or genomic location.  
5. Recommend variants based on relevant genes for a patient's phenotypes.

## Features

- Object-oriented design with Python classes for patients, phenotypes, and variants.  
- Modular and reusable code structure.  
- Console-based menus for interactive exploration.  
- Built-in error handling for missing or inconsistent input data.  
