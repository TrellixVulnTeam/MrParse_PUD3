# MrParse
Automated Molecular Replacement decision protocol

MrParse is a [CCP4](http://www.ccp4.ac.uk) program takes a protein amino acid sequence file and searches for homologs using [PHMMER](http://hmmer.org/) (default) or [HHSEARCH](https://github.com/soedinglab/hh-suite). It can then use [PHASER](https://www.phaser.cimr.cam.ac.uk/index.php/Phaser_Crystallographic_Software) to calculate the Expected Log Likelihood Gains (eLLG) values for the homologs.

It also attempts to classifiy the sequence according to its secondary structure, and whether any regions are expected to be Coiled-Coil or Transmembrane.

It then displays the results in a simple HTML webpage that is rendered using [VUE](https://vuejs.org). The sequence graphics are created using the [PFAM graphics library](https://pfam.xfam.org/generate_graphic), a copy of which is distributed with this code.

## Notes
### Search Model Finder
The search model finder currently uses [PHMMER](http://hmmer.org/) (distributed with [CCP4](http://www.ccp4.ac.uk)) to search for homologs. The facility to use [HHSEARCH](https://github.com/soedinglab/hh-suite) is almost complete, but is waiting on the HHSEARCH parsing functionality implemented in the GitHub [pull request](https://github.com/biopython/biopython/pull/1965) to be incorporated into the BioPython release.

### Classifiers
* secondary structure classification is currently carried by submitting jobs to the [JPRED](http://www.compbio.dundee.ac.uk/jpred/) server 
* Coiled-Coil classification is carried out with [Deepcoil](https://github.com/labstructbioinf/DeepCoil). This needs to be installed locally.
* Transmembrane classification is carried out with [Topcons2](https://github.com/ElofssonLab/TOPCONS2). This functionality is currently broken as the WSDL description file for their online server http://topcons.net/ is missing (an email was sent but no response received)

