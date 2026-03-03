package main

import (
	"errors"
	"strings"
	"time"
)

type UserService struct {
	Repo UserRepository
}

func validPassword(password string) error {
	trimmedPassword := strings.TrimSpace(password)
	hasSpecialChars := strings.ContainsAny(trimmedPassword, "!@#$%^&*()_+")

	if !hasSpecialChars {
		return errors.New("Password must contain at least one special character.")
	}

}
