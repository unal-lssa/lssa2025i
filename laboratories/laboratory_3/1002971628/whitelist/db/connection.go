package db

import (
	"ddaniel27/whitelist/models"
	"fmt"
	"log"
	"os"

	"gorm.io/driver/postgres"
	"gorm.io/gorm"
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

	err = db.AutoMigrate(&models.Whitelist{})
	if err != nil {
		log.Fatal("Error in migrations: ", err)
	}

	var count int64
	if err := db.Model(&models.Whitelist{}).Count(&count).Error; err != nil {
		panic("error counting")
	}

	if count == 0 {
		whitelists := []models.Whitelist{
			{
				IP: "172.30.0.1",
			},
		}

		if err := db.Create(&whitelists).Error; err != nil {
			panic("error creating")
		}
	}

	DB = db
}
