# Import Test #1 Mass Standard Import

## test files directory :E:/test Mass Standard Import

Preferences

* scenario- mass import
* author fallback folder
* Title fallback folder
* Fuzzy Duplicates 85%

I created a short list of books for testing. Change the folder and file name of the books to reflect the issue.

## test #1 thru 4 are on multi-file books

1. author missing all files
Folder ...\\Abert Thornhill\\No author
works as expected F: Author fallback from folder used

2. author missing in 2nd file title missing in 3rd file 4 files in total 
Folder: ...\\Robert R. McCammon\\No Author file 2

3. album book title missing all files
Folder ...\\Michael Finkel\\    no album
works as expected F: Title fallback from file used

4. album book title missing in 2nd file
Folder: ...\Ryk Brown\No Album in file 2
works as expected added book 

# these folder are all single files per book
Folder: ...\\Michael R. Stern\\Quantum Touch\

5. Storm Portal (Quantum Touch 1) album book title is blank
working F: Title fallback from file used

6. test fuzzy duplicate - sightly differences in author and book titles
book title Sand Storm (Quantum Touch 02) author is Michael R. Stern
book title Sand Storm (Quantum Touch 2) author is Michael R. Stern
working Duplicate 

## Auto-Correction:

7. all lower case - shadow storm (quantum touch 3)
works as expected

8. leading white - Storm Surge Quantum Touch, 5
works as expected

9. skip punctuation /\& special characters
book title @"Storm Unleashed" author #Michael R. Stern! genre (Audiobook)
works as expected


