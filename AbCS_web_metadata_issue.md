the application uses 2 modules web_metadata.py & web_book_api.py to retrieve book plot and metadata from the web. Is there a better way of doing this or is there improvements to the process. Put suggestion/improvement in the doc called abcs_Web_fetch_improvement  in the abcs folders

web_metadata is not working correctly. see the test cases below. Review the code to find out why this is not working correctly. Build a plan to fix this issue.

**Fixed June 3, 2026:** `get_book_metadata` no longer runs title-only fallback for every book with an author (`use_title_only` only). See `test/test_web_book_api_matching.py` Deaver regression tests.
It should be checking -
1. title 50% of words in db title should exist in web title 
2. author last name from db should be in web author. 
issue 
test 1 Search for db title "Cause Of Death" author "Jeffery Deaver" web metadata returns web title "Cause Of Death" web author "Patricia Cornwell"
test 2 Search for db title "Date Night" db author "Jeffery Deaver" 
metadata returns web title "Date Night Club" web author "Saxon Bennett"
test 3 Search for db title "Dodge" db author "Jeffery Deaver"
metadata returns web title "Fall; or, Dodge in Hell" web author "Neal Stephenson, Malcolm Hillgartner"

web metadata is still not working correctly as the below book used to return data --- do a full review of the web metadata and web_book_api 
test Search for db title "Pride And Prejudice" db author "Jane Austen"
nothing is being returned 