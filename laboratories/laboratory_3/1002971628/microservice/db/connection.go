package db

import (
	"fmt"
	"log"
	"os"

	"gorm.io/driver/postgres"
	"gorm.io/gorm"

	"ddaniel27/microservice/models"
)

var DB *gorm.DB

func Init() {
	dsn := fmt.Sprintf(
		"host=%s user=%s password=%s dbname=%s port=%s sslmode=disable",
		os.Getenv("DB_HOST"),
		os.Getenv("DB_USER"),
		os.Getenv("DB_PASSWORD"),
		os.Getenv("DB_NAME"),
		os.Getenv("DB_PORT"),
	)

	db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{})
	if err != nil {
		log.Fatal("Error connecting to the DB: ", err)
	}

	err = db.AutoMigrate(&models.Book{})
	if err != nil {
		log.Fatal("Error in migrations: ", err)
	}

	var count int64
	if err := db.Model(&models.Book{}).Count(&count).Error; err != nil {
		panic("error counting")
	}

	if count == 0 {
		books := []models.Book{
			{
				Title:  "Test title",
				Author: "me",
			},
			{
				Title:  "Second title",
				Author: "you",
			},
		}

		if err := db.Create(&books).Error; err != nil {
			panic("error creating")
		}
	}

	DB = db
}
