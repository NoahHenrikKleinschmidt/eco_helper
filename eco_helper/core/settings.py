"""
Generic settings for eco_helper
"""

# ----------------------------------------------------------------
#  Data Headers
# ----------------------------------------------------------------

state_col = "State"
"""
The data column handling the "state assignment".
"""

cell_type_col = "CellType"
"""
The data column handling the "cell type" assignment.
"""

gene_col = "Gene"
"""
The data handling the gene names or identifiers.
"""

rel_expr_col = "MaxFC"
"""
The data column handling the relative expression.
"""

ecotype_col = "Ecotype"
"""
The data column handling the ecotype assignment.
"""

ecotyper_experiment_col = "run" 
"""
The data column handling the Ecotyper experiment name.
"""

# ----------------------------------------------------------------
#  Data Files from EcoTyper
# ----------------------------------------------------------------

gene_info_file = "gene_info.txt"
"""
The file containing the gene info per celltype, including max fold change and state assignments.
"""

ecotypes_folder = "Ecotypes"
"""
The folder containing the Ecotypes from an EcoTyper experiment.
"""

ecotypes_assignment_file = "ecotype_assignment.txt"
"""
The file containing the Ecotypes assignment to samples from an EcoTyper experiment.
"""

ecotypes_composition_file = "ecotypes.txt"
"""
The file containing the composition data for Ecotypes from an EcoTyper experiment.
"""

# ----------------------------------------------------------------
#  Output files and directories
# ----------------------------------------------------------------

prerank_outdir = "gseapy_prerank"
"""
The output directory for the gseapy prerank gene sets.
"""

enrichr_outdir = "gseapy_enrichr"
"""
The output directory for the gseapy enrichr gene sets.
"""

gseapy_outdir = "gseapy_results"
"""
The output directory for the gseapy results.
"""

gene_sets_outdir = "gene_sets"
"""
The output directory for extracted gene sets files.
"""

# ----------------------------------------------------------------
#  File suffixes for output files
# ----------------------------------------------------------------

state_assignments_suffix = ".state_assignment.txt"
"""
The suffix for a celltype state assignments file.
"""

gene_sets_suffix = ".genes.txt"
"""
The suffix for a celltype gene sets file.
"""

enrichr_results_suffix = ".enrichr.txt"
"""
The suffix for gseapy enrichr results files.
"""

prerank_results_suffix = ".prerank.txt"
"""
The suffix for gseapy prerank results files.
"""