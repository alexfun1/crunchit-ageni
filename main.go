package main

import (
	log "github.com/sirupsen/logrus"
	"time"

	"github.com/alexfun1/crunchit-ageni/controllers"
	"github.com/alexfun1/crunchit-ageni/models"
	"github.com/gin-gonic/gin"
)

func main() {
	// Initialize Redis client
	redisClient := models.NewRedisClient("localhost:6379", "", 0)
	if err := redisClient.Ping(); err != nil {
		log.Fatalf("Cannot connect to Redis: %v\n", err)
	}

	// Sync JSON files (users.json, config.json) with Redis on startup
	if err := models.SyncUsers(redisClient); err != nil {
		log.Printf("Users sync error: %v\n", err)
	}
	if err := models.SyncConfig(redisClient); err != nil {
		log.Printf("Config sync error: %v\n", err)
	}

	// Create a Gin router
	router := gin.Default()

	// Optionally, serve static files (if needed for CSS, JS, images)
	// router.Static("/static", "./static")

	// Routes:
	//------------------------------------
	// Home / Login
	router.GET("/", controllers.ShowLoginPage)
	router.POST("/login", controllers.LoginHandler)

	// Logout
	router.GET("/logout", controllers.LogoutHandler)

	// Registration
	router.GET("/register", controllers.ShowRegisterPage)
	router.POST("/register", controllers.RegisterHandler)

	// Main page
	router.GET("/main", controllers.ShowMainPage)

	// Account page
	router.GET("/account", controllers.ShowAccountPage)
	router.POST("/account/addmana", controllers.AddManaHandler)

	// Create and configure the HTTP server
	router.NoRoute(func(ctx *gin.Context) { ctx.JSON(http.StatusNotFound, gin.H{}) })

	log.Println("Starting server on :8080")
	if err := router.Run(":8080"); err != nil {
		log.Fatalf("Server failed to start: %v\n", err)
	}
}
