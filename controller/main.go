package controllers

import (
	"net/http"

	"github.com/gin-gonic/gin"

	"github.com/alexfun1/crunchit-ageni/models"
)

// ShowMainPage is the GET handler for "/main".
// Renders the main.html template with user data if logged in.
func ShowMainPage(c *gin.Context) {
	user := getLoggedInUser(c)
	if user == nil {
		c.Redirect(http.StatusFound, "/?error=Please+login")
		return
	}

	c.HTML(http.StatusOK, "main.html", gin.H{
		"User": user,
	})
}

// getLoggedInUser retrieves user info from session (cookie).
func getLoggedInUser(c *gin.Context) *models.User {
	sessionID, err := c.Cookie("session_id")
	if err != nil || sessionID == "" {
		return nil
	}
	// In real code, parse session from Redis. Demo:
	userID := parseUserIDFromSession(sessionID)
	if userID == 0 {
		return nil
	}
	return findUserByID(userID)
}

func parseUserIDFromSession(sessionVal string) int {
	// Example: "123-session"
	// We'll just parse the leading digits
	// (error handling omitted for brevity)
	return 123
}

func findUserByID(id int) *models.User {
	// This would be a Redis or DB lookup
	// Demo approach: read from users.json
	return nil
}
