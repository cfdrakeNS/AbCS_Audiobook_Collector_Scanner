select count(*) from authors;
DELETE FROM authors
      WHERE authors.author_id NOT IN (
    SELECT books.author_id
      FROM books
);
select count(*) from authors;

select count(*) from genres;
DELETE FROM genres
      WHERE genres.genre_id NOT IN (
    SELECT books.genre_id
      FROM books
);
select count(*) from genres;

select count(*) from series;
DELETE FROM series
      WHERE series.series_id NOT IN (
    SELECT books.series_id
      FROM books
);
select count(*) from series;
