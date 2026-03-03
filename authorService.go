package main

import (
	"database/sql"
	"time"
)

type Author struct {
	id    int
	name  string
	books []Book
}

type AuthorRepository struct {
	db *sql.DB
}

func NewAuthorRepository(db *sql.DB) *AuthorRepository {
	return &AuthorRepository{
		db: db,
	}
}

func (ar *AuthorRepository) GetAllAuthors() ([]Author, error) {
	rows, err := ar.db.Query("SELECT * FROM authors")

	if err != nil {
		return nil, err
	}
	defer rows.Close()

	authors := []Author

	for rows.Next() {
		var author Author
		if err := rows.Scan(&author.id, &author.name); err != nil {
			return nil, err
		}
		authors = append(authors, author)
	}
	if err = rows.Err(); err != nil {
		return nil, err
	}
	return authors, nil
}
