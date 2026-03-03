package main

import (
	"database/sql"
	"errors"
	"time"
)

type User struct {
	ID             int
	Email          string
	password       string
	age int
	dateJoined     time.Time
	numBooks       int
	favoriteAuthor string
}

type UserStore interface {
	GetUserByName(username string) (User, error)
	GetUserByID(ID int) (User, error)
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
	if err := repo.db.QueryRow(
		"SELECT id, userName FROM users WHERE userName = ?", Username).
		Scan(&u.ID, &u.Email); err != nil {
		if err == sql.ErrNoRows {
			return u, err
		}
	}

	return u, nil
}

func (repo *UserRepository) GetUserByID(ID int) (User, error) {
	var u User
	if err := repo.db.QueryRow(
		"SELECT id, username FROM users WHERE id = ?", ID).
		Scan(&u.ID, &u.Email); err != nil {
		if err == sql.ErrNoRows {
			return u, err
		}
	}
	return u, nil
}

func (repo *UserRepository) CreateUser(email string, password string) error {
	userName, error := GetUserByName(email) 

	if userName != nil {
		return errors.New("This username already exists.")
	}

	repo.db.QueryRow(
		"INSERT email, password INTO users"
	)
}
