package main

import (
	"database/sql"
	"log"
	"time"
)

type BookRepository struct {
	db *sql.DB
}

type Book struct {
	id            int
	title         string
	author        string
	isbn          string
	datePublished time.Time
}

type UserBook struct {
	title         string
	author        string
	datePublished time.Time
	user          User
}

func NewBookRepository(db *sql.DB) *BookRepository {
	return &BookRepository{
		db: db,
	}
}

func (r *BookRepository) GetAllBooks() ([]Book, error) {

	rows, err := r.db.Query("SELECT id, title FROM books")

	if err != nil {
		return nil, err
	}
	defer rows.Close()

	books := make([]Book, 0)

	for rows.Next() {
		var book Book
		if err := rows.Scan(&book.id, &book.title); err != nil {
			return nil, err
		}
		books = append(books, book)
	}
	if err = rows.Err(); err != nil {
		return nil, err
	}
	return books, nil
}

func (r *BookRepository) GetBooksByAuthor(authorStr string) ([]Book, error) {
	rows, err := r.db.Query("SELECT id, title FROM books WHERE LOWER(author) = LOWER(?)", authorStr)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var books []Book

	for rows.Next() {
		var book Book
		if err := rows.Scan(&book.id, &book.title); err != nil {
			return nil, err
		}
		books = append(books, book)
	}
	if err = rows.Err(); err != nil {
		return nil, err
	}
	return books, nil
}

//func (r *BookRepository) GetBooksInYear(dateStr string) ([]Book, err) {
//	rows, err := r.db.Query("SELECT id, title FROM books WHERE datePublished >= datestr")
//
//	return rows, err
//}

func (r *BookRepository) AddBook(title string, author string)
