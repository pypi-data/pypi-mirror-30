"""

Description:
The program will run in about 45 min when all options are selected without debugging mode
=> 22 min producing cell counts files
=> 19 min for Fisher exact test execution and adding p-values in slow mode
=> 5 min plotting cell count frequencies between exvivo and the rest of samples, pvalues vs pvalues
=> min plotting heatmap of reproducibility between repeats exvivo cell counts and expansion (pvalues)

Update version 1.1:
1- Change sample info title column 'sequencing ID' by 'file name'
2- Check presence of fisher python modules and run a Fisher exact test according to it (fast or slow version)
3- Correcting nucleotide clonotype counts for each of CDR3 amino acid clonotype when adding p-values
4- Correct zero counts file for amino acid clonotypes

Update version 1.2:
1- Correct zero cell counts file
2- Zero count file was reformatted in two columns

Update version 1.3 (02/08/2016):
1- Pulling NucleotideClonotypes class from Clonotypes class.
2- Creating excel files with xlsxwriter modules in addition of csv files to fix the string sorting bug of very low p-values found after loading csv files in excel softwa
3- Fix the upper case peptide sequence in the header of files.
4- Improving memory managment by calling the garbage collector.
5- Changing the figure legend to single dot.

Update version 1.4 (09/08/2016):
1- Fixing p-values vs p-values name bug, changed were applied to different files.
2- Changing p-values < 2.2251E-308 to 0 to fix excel sorting bug due to lower number precision limit.
(source: https://support.office.com/en-us/article/Excel-specifications-and-limits-1672b34d-7043-467e-8e27-269d656771c3?ui=en-US&rs=en-US&ad=US&fromAR=1#bmcalculation)
3- Importing only methods and class useful for program execution
4- Improving managment of memory usage for get_df_general_info method.

Update version 1.5 (16/08/2016):
1- Adding negctrl vs pep stim pvalues plot
2- Adding validation bar plot
3- Making heatmaps of reproducibility rate between repeats

Update version 1.6 (01/11/2016):
1- Automatic antigen specific threshold identification
2- Producing data csv file for validation of methodology

Update version 1.7 (17/11/2016):
1- Correction of ex vivo vs other samples clonotype frequencies (axis limits and breaks)
2- Adding comparison of p-values from medium only and peptide exposed clonotypes

Update version 1.8 (08/12/2016):
1- calculate MCC for expansion thresholds identification
2- addition of breaks and 3 by 2 subplot for expansion thresholds identification figure
3- addition of breaks and 2 by 2 subplot for p-values versus p-values figure

Update version 1.9 (05/01/2017):
1- correction of heatmaps

Update version 1.10 (02/02/2017):
1- Averaging MCC according to the # of donors.
2- Adding sensitivity and specificity for each donors for each tested irrelevant and relevant threshold.

Update version 1.11 (06/29/2017):
1- Adding V, D and J gene usage.

Update version 1.12 (07/25/2017):
1- Adding V, D and J gene name columns to clonotype CDR3s.

Update version 1.13 (09/19/2017):
1- Development of a method considering expanded clonotypes in 2 repeats as positive controls to determine expansion thresholds

Update version 1.14 (11/09/2017):
1- Cross validation Leave-one-out implementation todo

Update version 1.15 (30/01/2018):
1- Format checking

Update version 1.16 (1/02/2018):
1- Improving arguments parser by using dedicated module argparse.

Update version 0.3.0 (21/03/2018):
1- Adding time point analysis.

Update version 0.3.1 (10/04/2018):
1- fixing bugs including dot plot for optimization step

Update version 0.3.2 (10/04/2018):
1- checking that files in the input folder are also found in the metadata file sample_info.csv

Update version 0.3.3 (12/04/2018):
1- Added a logger

Update version 0.3.4 (13/04/2018):
1- Added compression option

NOTE: Program requires modules:
- memory_profiler
- rpy2, conda install --channel https://conda.anaconda.org/r rpy2
- seaborn
- scikit-learn, conda install scikit-learn

"""

from controller import pepbox

if __name__ == '__main__':
    pepbox()
