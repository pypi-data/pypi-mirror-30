# SBI-Python project  
## Constructing macromolecular complexes. 

*Ramon Massoni and Winona Oliveros*

### Description
A python package for macrocomplex construction given protein pairwise interactions. 

**Problem**

Given a set of interacting pairs (prot-prot), reconstruct the complete macrocomplex and return a PDB file (or files) with the possible protein macrocomplexes build. 

## General Information
### Input Files

This program needs an input of PDB files holding the protein pairwise interactions needed to reconstruct the desired macrocomplex. The program can handle those scenarios: 

* The same sequence appearing in different PDB files has not to be identical, we can handle 95% of identity. 
* The same sequence appearing in different files can have different names. 
* The user can include a file with the stoichiometry of the protein. The file has to contain the name of the chain, the file containing that chain and the number of times it has to appear on the final complex. 
