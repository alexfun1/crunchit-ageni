package controllers

import (
	"fmt"
	"net/http"

	"github.com/gin-gonic/gin"
)

// ShowAccountPage renders the account.html template if the user is logged in.
func ShowAccountPage(c *gin.Context) {
	user := getLoggedInUser(c)
	if user == nil {
		c.Redirect(http.StatusFound, "/?error=Please+login")
		return
	}

	c.HTML(http.StatusOK, "account.html", gin.H{
		"User": user,
	})
}

// AddManaHandler simulates adding 100 mana to the user account.
func AddManaHandler(c *gin.Context) {
	user := getLoggedInUser(c)
	if user == nil {
		c.Redirect(http.StatusFound, "/?error=Please+login")
		return
	}
	user.Mana += 100

	// Save user changes back to Redis / JSON
	saveUserToRedis(*user)

	msg := fmt.Sprintf("Added 100 mana. New total: %d", user.Mana)
	c.Redirect(http.StatusFound, "/account?success="+msg)
}
