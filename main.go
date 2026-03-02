package main

import (
	"database/sql"
	"fmt"
	_ "github.com/lib/pq"
	"log"
	"os"
)

func main() {
	//fmt.Println("Hello Bookie")
	host := os.Getenv("DB_HOST")
	port := os.Getenv("DB_PORT")
	user := os.Getenv("DB_USER")
	password := os.Getenv("DB_PASSWORD")
	dbname := os.Getenv("DB_NAME")

	connString := fmt.Sprintf("host=%s port=%s user=%s password=%s dbname=%s sslmode=disable",
		host, port, user, password, dbname)

	db, err := sql.Open("postgres", connString)
	if err != nil {
		log.Fatalf("Error opening database: %q\n", err)
	}

	defer db.Close()

	err = db.Ping()

	if err != nil {
		log.Fatalf("Error connecting to the database: %q\n", err)
	}

	fmt.Println("Database connection successful.")
}
