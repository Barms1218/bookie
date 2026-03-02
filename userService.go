package main

import (
	"database/sql"
	"time"
)

type User struct {
	ID             int
	Username       string
	password       string
	dateJoined     time.Time
	numBooks       int
	favoriteAuthor string
}

type UserRepository struct {
	db *sql.DB
}

func NewUserRepository(db *sql.DB) *UserRepository {
	return &UserRepository{
		db: db,
	}
}

func (repo *UserRepository) GetUserByName(Username string) (User, error) {
	var u User
	if err := repo.db.QueryRow("SELECT id, userName FROM users WHERE userName = ?", Username).Scan(
		&u.ID,
		&u.Username,
	); err != nil {
		if err == sql.ErrNoRows {
			return u, err
		}
	}

	return u, nil
}
