SELECT b.*,
       a.name AS author_name,
       s.name AS series_name,
       g.name AS genre_name,
       c.name AS collection_name
  FROM books bf
       LEFT JOIN
       authors a ON b.author_id = a.author_id
       LEFT JOIN
       series s ON b.series_id = s.series_id
       LEFT JOIN
       genres g ON b.genre_id = g.genre_id
       LEFT JOIN
       collections c ON b.collection_id = c.collection_id
 WHERE 1 = 1
 order by a.name, b.year, b.title;
 
 