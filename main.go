package main

import (
	"github.com/alexfun1/crunchit-ageni/controllers"
	gin "github.com/gin-gonic/gin"
	log "github.com/sirupsen/logrus"
)

func main() {
	router := gin.Default()
	router.Use(gin.Logger())
	router.Use(gin.Recovery())
	router.LoadHTMLGlob("templates/*.html")

	router.GET("/ping", func(c *gin.Context) {
		c.JSON(200, gin.H{
			"message": "pong",
		})
	})
	router.GET("/", controller.ShowLoginPage)
	router.POST("/login", controller.LoginHandler)
	router.GET("/logout", controller.LogoutHandler)
	router.GET("/main", controller.ShowMainPage)
	router.GET("/account", controller.ShowAccountPage)
	router.POST("/add_mana", controller.AddManaHandler)
	router.GET("/register", controller.ShowRegisterPage)
	router.POST("/register", controller.RegisterHandler)
	if err := router.Run(":8080"); err != nil {
		log.Fatal("Error starting server")
	}
}
