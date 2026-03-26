#### This folder contains the files submitted as solutions for the exercises of the $4^{th}$ ROOT module's hands-on session, titled "TMVA"

#### The description of each exercise and its task can be found in:
### "sda-nsnp-lab-tutorial-2024-25-4.pdf"

## Content 
- **outputs/**:
  * plots/: folder containing all the plots and graphs produced by the script
  * weights/: folder containing the _.C_ files for the classifiers used to conduct the analysis
  * atlas-higgs-challenge-2014-v2-bkg.root: _.root_ file with the information concerning the background data
  * atlas-higgs-challenge-2014-v2-sig.root: _.root_ file with the information concerning the signal data
- **input_variables_dist.png**: picture containing the graphs with initial variables' distributions
- **prep.cpp**: script used to create the _.root_ files and to read the input dataset
- **tmva_training.cpp**: main script used for the analysis
  
## Note
#### Some files could not be uploaded due to their excessive size, in particular:

- **atlas-higgs-challenge-2014-v2.csv**: the dataset used for this exercise (~200MB)
- **TMVA_output.root**: the output _.root_ file (~27MB)
