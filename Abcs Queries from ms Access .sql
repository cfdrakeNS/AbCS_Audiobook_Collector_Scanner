-- Query: qryFrmAddToDbAuthortP1                                                                        Page: 1

         SELECT DISTINCT import.name, import.lErrors
         FROM import LEFT JOIN authors ON import.[name] = authors.name
         WHERE(((import.lErrors)=False))
         ORDER BY import.name;

-- Query: qryFrmAddToDbAuthortP2

         INSERT INTO authors(name)
         SELECT qryFrmAddToDbAuthortP1.name
         FROM qryFrmAddToDbAuthortP1 LEFT JOIN authors ON
         qryFrmAddToDbAuthortP1.[name] = authors.name;

-- Query: qryFrmAddToDbDupsFindP1
  SELECT authors.name,
         books.title,
         books.year,
         books.author_id,
         genres.name,
         books.collection_id,
         books.tracks,
         books.size_mb,
         books.time_hours,
         books.time_minutes,
         books.bitrate,
         books.path,
         books.date_added,
         books.reader,
         books.source,
         books.file_format,
         books.book_id,
         books.comments
    FROM genres
         RIGHT JOIN
         (
             authors
             INNER JOIN
             books ON authors.author_id = books.author_id
         )
         ON genres.genre_id = books.genre_id
   WHERE ( ( (books.title) IN (
             SELECT title
               FROM books AS Tmp
              GROUP BY title,
                       year,
                       author_id,
                       collection_id
             HAVING Count( * ) > 1 AND
                    year = books.year AND
                    author_id = books.author_id AND
                    collection_id = books.collection_id
         )
         ) ) 
   ORDER BY books.title,
            books.year,
            books.author_id,
            books.collection_id;

-- Query: qryFrmAddToDbDupsMoveP2

         PARAMETERS pbook_id Long;
         INSERT INTO import(title, name, name, year, tracks, size_mb, time_hours,
         bitrate, path, reader, sComment, sError, lErrors, collection_id, file_format)
         SELECT qryFrmAddToDbDupsFindP1.title, qryFrmAddToDbDupsFindP1.name,
         qryFrmAddToDbDupsFindP1.name, qryFrmAddToDbDupsFindP1.year,
         qryFrmAddToDbDupsFindP1.tracks, qryFrmAddToDbDupsFindP1.size_mb,
         qryFrmAddToDbDupsFindP1.time_hours, qryFrmAddToDbDupsFindP1.time_minutes, qryFrmAddToDbDupsFindP1.bitrate,
         qryFrmAddToDbDupsFindP1.path, qryFrmAddToDbDupsFindP1.reader,
         qryFrmAddToDbDupsFindP1.comments, "Duplicate Already Exists in database" AS Msg1,
         1+1 AS Flag, qryFrmAddToDbDupsFindP1.collection_id,
         qryFrmAddToDbDupsFindP1.file_format AS Expr5
         FROM qryFrmAddToDbDupsFindP1
         WHERE(((qryFrmAddToDbDupsFindP1.book_id) > [pbook_id]));

-- Query: qryFrmAddToDbDupsRmv

         PARAMETERS pbook_id Long;
         DELETE *
         FROM books
         WHERE(books.book_id) > [pbook_id]
           and books.book_id IN(
                SELECT qryFrmAddToDbDupsFindP1.book_id FROM qryFrmAddToDbDupsFindP1);


-- Query: qryFrmAddToDbGenreP1

  SELECT import.name,
         import.title,
         genres.genre_id,
         import.lErrors
    FROM (
             import
             LEFT JOIN
             genre ON import.name = genres.name
         )
         INNER JOIN
         collections ON import.collection_id = collections.collection_id
   WHERE ( ( (import.name) > " ") AND
           ( (import.lErrors) = false) );

-- Query: qryFrmAddToDBGenreP2

         INSERT INTO genre(name)
         SELECT qryFrmAddToDbGenreP1.name
         FROM qryFrmAddToDbGenreP1 LEFT JOIN genre ON qryFrmAddToDbGenreP1.name =


-- Query: qryFrmAddToDbGenreToTitles

         UPDATE qryFrmAddToDbGenreP1 LEFT JOIN books ON qryFrmAddToDbGenreP1.[title] =
         books.title SET books.genre_id = [qryFrmAddToDbGenreP1].[genre_id]
         WHERE(((books.genre_id) Is Null));


-- Query: qryFrmAddToDbTitleP1

         SELECT import.lErrors, authors.name, authors.author_id, import.title,
         import.year, import.tracks, import.time_hours, import.time_minutes, import.size_mb, import.bitrate,
         import.sComment, import.path, import.source, import.collection_id,
         import.reader, import.file_format
         FROM import LEFT JOIN authors ON import.[name] = authors.name
         WHERE(((import.lErrors)=False));


-- Query: qryFrmAddToDbTitlesp2

         INSERT INTO books(author_id, collection_id, title, tracks, year, time_hours time_minutes, size_mb,
         bitrate, comments, date_added, source, reader, file_format, path)
         SELECT qryFrmAddToDbTitleP1.author_id AS Expr1, qryFrmAddToDbTitleP1.collection_id
         AS Expr2, qryFrmAddToDbTitleP1.title AS Expr3, qryFrmAddToDbTitleP1.tracks AS Expr4,
         qryFrmAddToDbTitleP1.year AS Expr5, qryFrmAddToDbTitleP1.time_hours AS Expr6,
         qryFrmAddToDbTitleP1.size_mb AS Expr7, qryFrmAddToDbTitleP1.bitrate AS Expr8,
         qryFrmAddToDbTitleP1.sComment AS Expr9, Now() AS Added,
         qryFrmAddToDbTitleP1.source AS Expr10, qryFrmAddToDbTitleP1.reader AS Expr11,
         qryFrmAddToDbTitleP1.file_format AS Expr12, qryFrmAddToDbTitleP1.path AS Expr13
         FROM qryFrmAddToDbTitleP1;

-- Query: qryFrmAuthors

  SELECT authors.author_id,
         authors.name
    FROM authors
   ORDER BY authors.name;

-- Query: qryFrmCollection

    SELECT collections.collection_id,
           collections.name,
           collections.active
    FROM collections;

-- Query: qryFrmDetail @@@ 

         SELECT books.*, series.name, authors.name, collections.name,
         genres.name
         FROM genre RIGHT JOIN(collections RIGHT JOIN(series RIGHT JOIN(authors
         RIGHT JOIN books ON authors.author_id=books.author_id) ON series.series_id=books.series_id) ON collections.[collection_id]=books.[collection_id]) ON


-- Query: qryFrmDetailDeltitle

   DELETE FROM books
        WHERE book_id = :book_id;

-- Query: qryFrmGenre

  SELECT genres.genre_id,
         genres.name
    FROM genres
   ORDER BY genres.name;


-- Query: qryFrmImport

         SELECT import.lnImportId, import.sError, import.lErrors, import.name,
         import.year, import.title, import.tracks, import.time_hours, import.time_minues, import.name,
         import.path
         FROM import
         ORDER BY import.name, import.title;


-- Query: qryFrmImportDetail

         SELECT import.lnImportId, import.lErrors, import.name, import.year,
         import.title, import.tracks, import.name, import.reader, import.path,
         import.sError, import.bitrate, import.size_mb, import.time_hours, import.time_minutes,
         import.sFileName, import.file_format, collections.name
         FROM import LEFT JOIN collections ON import.[collection_id] =
         collections.[collection_id]
         WHERE(((import.lErrors)=True))
         ORDER BY import.name, import.title;


-- Query: qryFrmImportFindDups

         SELECT import.title, import.name, import.lnImportId, import.lErrors
         FROM import
         WHERE(((import.title) In(SELECT[title] FROM[import] As Tmp GROUP BY
         [title], [name] HAVING Count(*) > 1  And[name]=[import].[name]))
          AND((import.lErrors)=False))
         ORDER BY import.title, import.name;


-- Query: qryFrmImportFindDups1

         SELECT import.title, import.name, import.lnImportId, import.lErrors
         FROM import
         WHERE(((import.title) In(SELECT[title] FROM[import] As Tmp GROUP BY
         [title], [name] HAVING Count(*) > 1  And[name]=[import].[name]))
          AND((import.lErrors)=False))
         ORDER BY import.title, import.name;


-- Query: qryFrmImportFlagDups     @ @@

         UPDATE import INNER JOIN qryFrmImportFindDups ON import.lnImportId =
         qryFrmImportFindDups.lnImportId SET import.sError = "Duplicate Import, Same Author &":

-- Query: qryFrmImportFlagErrors

         UPDATE import SET import.lErrors = True
         WHERE(((import.sError) Is Not Null));

-- Query: qryFrmIpmortExportErrors

         SELECT import.sError AS Errors, import.name AS Author, import.title AS
         Title, import.year AS RelYear, import.tracks AS Files, import.time_hours AS
         Hours, import.time_minutes AS minutes, import.size_mb AS SizeMb, import.file_format AS FileFormat,
         collections.name AS Collections, import.path AS Path, import.sFileName AS
         FileName
         FROM import LEFT JOIN collections ON import.[collection_id] =
         collections.[collection_id]
         WHERE(((import.lErrors)=True))
         ORDER BY import.name, import.title, import.year, import.tracks DESC,

-- Query: qryfrmMainRmvAuthorsP1                                                                       Page: 30

  SELECT authors.author_id
    FROM authors
         LEFT JOIN
         books ON authors.author_id = books.author_id
   WHERE ( ( (books.author_id) IS NULL) );

-- Query: qryFrmMainRmvGenreP1                                                                         Page: 31

  SELECT genres.genre_id
    FROM genres
         LEFT JOIN
         books ON genres.genre_id = books.genre_id
   WHERE ( ( (books.genre_id) is NULL) );

-- Query: qryFrmMainRmvSeriesP1                                                                        Page: 32

  SELECT series.series_id
    FROM series
         LEFT JOIN
         books ON series.series_id = books.series_id
 WHERE ( ( (books.series_id) IS NULL) );

-- Query: qryFrmMainShowDups         

         PARAMETERS pcollection_id Long;
         SELECT qryFrmMain.*
         FROM qryFrmMain
         WHERE(((qryFrmMain.title) In(SELECT[title] FROM[qryFrmMain] As Tmp GROUP BY
         [title], [year], [name], [collection_id] HAVING Count(*) > 1
                 And[year]=[qryFrmMain].[year]
                 And[name]=[qryFrmMain].[name]
                 And[collection_id]=[qryFrmMain].[collection_id])) AND
         ((qryFrmMain.collection_id)=[pcollection_id]))
         ORDER BY qryFrmMain.title, qryFrmMain.year, qryFrmMain.tracks,
         qryFrmMain.time_hours, qryFrmMain.date_added;

-- Query: qryFrmSeries               

  SELECT series.series_id,
         series.name
    FROM series;

-- Query: qryFrmUpdateAddCollection  @@ lgSelect

         UPDATE books SET books.collection_id=[%1]
         WHERE(((books.lgSelect)=True));

-- Query: qryFrmUpdateAddGenre ## lgSelect       

         PARAMETERS pgenre_id Long;
         UPDATE books SET books.genre_id=[pgenre_id]
         WHERE(((books.lgSelect)=True));

-- Query: qryFrmUpdateAddSeries   ## lgSelect    

         PARAMETERS pSeriesId Long;
         UPDATE books SET books.series_id=[pSeriesId]
         WHERE(((books.lgSelect)=True));

-- Query: qryFrmUpdateSelect    ## lgSelect      

  SELECT books.title,
         books.year,
         series.name,
         genres.name,
         collections.name,
         books.lgSelect,
         books.book_id,
         genres.genre_id,
         series.series_id,
         collections.collection_id
    FROM (
             (
                 books
                 LEFT JOIN
                 series ON books.series_id = series.series_id
             )
             LEFT JOIN
             genre ON books.genre_id = genres.genre_id
         )
         LEFT JOIN
         collections ON books.collection_id = collections.collection_id
   WHERE ( ( (books.lgSelect) = true) ) 
   ORDER BY books.title;

-- Query: qryInsAuthor   

  INSERT INTO authors (
                          name
                      )
                      VALUES (
                          :author_name
                      );

-- Query: qryInname    

  INSERT INTO genre (
                        name
                    )
                    VALUES (
                        :genre_name
                    );

-- Query: qryInname   

  INSERT INTO series (
                         name
                     )
                     VALUES (
                         :SeriesName
                     );

-- Query: qryLuAuthor    

  SELECT authors.author_id,
         authors.name,
         Count(books.title) AS TitlesCnt
    FROM books
         RIGHT JOIN
         authors ON books.author_id = authors.author_id
   GROUP BY authors.author_id,
            authors.name
   ORDER BY authors.name;

-- Query: qryLuCollections   

  SELECT collections.collection_id,
         collections.name,
         Count(books.title) AS Titles
    FROM books
         RIGHT JOIN
         collections ON books.collection_id = collections.collection_id
   WHERE ( ( (collections.active) = true) ) 
   GROUP BY collections.collection_id,
            collections.name
   ORDER BY collections.name;

-- Query: qryLuGenre         

  SELECT genres.genre_id,
         genres.name,
         Count(books.title) AS TitlesCnt
    FROM genres
         LEFT JOIN
         books ON genres.genre_id = books.genre_id
   GROUP BY genres.genre_id,
            genres.name
   ORDER BY genres.name;

-- Query: qryLuSeries        

  SELECT series.series_id,
         series.name,
         Count(books.title) AS TitlesCnt
    FROM books
         RIGHT JOIN
         series ON books.series_id = series.series_id
   GROUP BY series.series_id,
            series.name
   ORDER BY series.name;
