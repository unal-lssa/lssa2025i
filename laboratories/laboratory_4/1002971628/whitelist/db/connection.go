package db

import (
	"fmt"
	"log"
	"os"

	"gorm.io/driver/postgres"
	"gorm.io/gorm"

	"ddaniel27/whitelist/models"
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

	if err := db.AutoMigrate(&models.Whitelist{}); err != nil {
		fmt.Printf("Error in migration: %s", err.Error())
	}

	var count int64
	if err := db.Model(&models.Whitelist{}).Count(&count).Error; err != nil {
		fmt.Printf("Error creating model: %s", err.Error())
	}

	if count == 0 {
		whitelists := []models.Whitelist{
			{
				IP: "172.30.0.1",
			},
		}

		if err := db.Create(&whitelists).Error; err != nil {
			fmt.Printf("Error inserting in model: %s", err.Error())
		}
	}

	DB = db
}
