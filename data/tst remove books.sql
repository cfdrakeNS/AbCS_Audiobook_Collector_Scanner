SELECT count( * ) 
FROM books
 WHERE books.collection_id = 1 AND
       books.read_date is null;

Delete 
  FROM books
 WHERE books.collection_id = 1 AND
       books.read_date is null
limit 2133;

SELECT count( * ) 
FROM books
WHERE books.collection_id = 1; 
