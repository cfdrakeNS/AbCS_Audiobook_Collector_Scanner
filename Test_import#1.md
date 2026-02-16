Import Test #1

Preferences 
* scenario- mass import 
* author fallback folder 
* Title fallback folder 
* Fuzzy Duplicates 100%

I created a short list of books for testing. Change the folder and file name of the books to reflect the issue.

## test #1 thru 4 are on multi-file books 

1 author missing all files 
Folder E:\\test books\\Abert Thornhill\\No author 
not working picking up author from current folder.
Suggestion: If we have an author and author folder hasn't change use that for author

2 author missing in 2nd file 
Folder: E:\\test books\\Robert R. McCammon\\No Author file 2
works as expected

#3 album book title missing all files
Folder E:\\test books\\Michael Finkel\\no album
works as expected

#4 album book title missing in 2nd file
Folder: E:\\test books\\Robert R. McCammon\\No Author file 2
works as expected

these folder are all single files per book 
Folder: E:\\test books\\Michael R. Stern\\Quantum Touch

#5 Storm Portal (Quantum Touch 1) album book title is blank 
not working picking up current folder

#6 test fuzzy duplicate - sightly differences in author and book titles 
book title Sand Storm (Quantum Touch 02) author is Michael R. Stern
book title Sand Storm (Quantum Touch 2) author is Michael Stern
not working they should be dups 

## Auto-Correction: 
#7 all lower case - shadow storm (quantum touch 3) 
works as expected

#8 leading white - Storm Surge Quantum Touch, 5
works as expected

#9 skip punctuation \& special characters 
book title @"Storm Unleashed" author #Michael R. Stern! genre (Audiobook)
works as expected

my test file directory structure is in Test\_import\_dir\_list.md

&nbsp;











