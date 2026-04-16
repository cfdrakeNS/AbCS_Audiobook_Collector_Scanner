in order to reduces some complexity app and that is really not much value and add just confusion I want to remove the below listed preferences

build a plan to remove from preferences the Options and Auto-correct section and there option. refactor the code as required. crate a doc outlining the changes and a practical approach to change to permit effective testing.

# preferences Options \& Auto-correct removal and code refactoring

## 1\. Review clean books before adding;

modules: preferences, import \& import progress window
changes remove  "add valid"  button and logic update status bar messages f1 shortcuts and shortcuts.py following standardized centralization

## 2\. flip author name; book_list_import, web_metadat remove this completely

logic around comparison and normalization of author

## 3\. Move leading 'the', 'a', 'an' to end of title: remove this completely

modules: book_list_import, web_metadata,
change logic around comparison and normalization of title



## 4\. remove these 4 preferences: Apply Proper case, trim whitespace, Trim leading Punctuation, and Remove Special Characters:

All of the above always should be applied throughout the app before saving to db. 

update note: still maintain the correction C: flag in import window errors for Trim leading Punctuation and Special Characters this will let the user know that there is issues in the metadata tag.


modules:  book_list_import, web_metadat, book_detail,  import_detail, name_list, collection, update

these module may also need changes.
validato, import_rules.py, import_scanner.py, validator.py











