package controllers

import (
	"encoding/json"
	"net/http"
	"os"
	"strconv"
	"strings"

	"github.com/gin-gonic/gin"

	"github.com/alexfun1/crunchit-ageni/models"
)

// ShowLoginPage renders the login page via Gin's HTML templating.
func ShowLoginPage(c *gin.Context) {
	c.HTML(http.StatusOK, "login.html", gin.H{
		// Optionally pass data to template here
	})
}

// LoginHandler processes the login form submission.
func LoginHandler(c *gin.Context) {
	username := c.PostForm("username")
	password := c.PostForm("password")

	// Find user by login
	user := findUserByLogin(username)
	if user == nil || user.Password != password {
		c.Redirect(http.StatusFound, "/?error=Invalid+credentials")
		return
	}

	// Create a session ID in Redis or otherwise
	sessionID := createSessionInRedis(user.ID)

	// Set a session cookie for the user (30-min expiry)
	c.SetCookie("session_id", sessionID, 1800, "/", "", false, true)
	c.Redirect(http.StatusFound, "/main")
}

// LogoutHandler invalidates the session and clears the cookie.
func LogoutHandler(c *gin.Context) {
	// Clear session cookie
	c.SetCookie("session_id", "", -1, "/", "", false, true)
	c.Redirect(http.StatusFound, "/?info=Logged+out")
}

// ShowRegisterPage renders the registration page.
func ShowRegisterPage(c *gin.Context) {
	c.HTML(http.StatusOK, "register.html", gin.H{})
}

// RegisterHandler processes registration submissions.
func RegisterHandler(c *gin.Context) {
	email := c.PostForm("email")
	pass1 := c.PostForm("password")
	pass2 := c.PostForm("confirm_password")

	if pass1 != pass2 {
		c.Redirect(http.StatusFound, "/register?error=Passwords+do+not+match")
		return
	}

	// Load config to check blocked names, default role, etc.
	cfg := getConfigFromRedis()
	localPart := strings.Split(email, "@")[0]

	// Check if localPart is in blocked list
	for _, b := range cfg.Registration.BlockedLoginsNames {
		if b == localPart {
			c.Redirect(http.StatusFound, "/register?error=Blocked+username")
			return
		}
	}

	user := models.User{
		ID:       getNextUserID(),
		Login:    localPart,
		Password: pass1,
		Email:    email,
		Role:     cfg.Registration.DefaultRole,
		Mana:     100,
	}

	saveUserToRedis(user)
	c.Redirect(http.StatusFound, "/?success=Registration+successful")
}

///////////////////////////////////////////////////////////////////////////////
// Below are placeholder helper functions that you would adapt to your codebase.
///////////////////////////////////////////////////////////////////////////////

func findUserByLogin(login string) *models.User {
	data, _ := os.ReadFile("users.json")
	var raw struct {
		Users []models.User `json:"users"`
		Roles []models.Role `json:"roles"`
	}
	json.Unmarshal(data, &raw)
	for _, u := range raw.Users {
		if u.Login == login {
			return &u
		}
	}
	return nil
}

func getNextUserID() int {
	data, _ := os.ReadFile("users.json")
	var raw struct {
		Users []models.User `json:"users"`
		Roles []models.Role `json:"roles"`
	}
	json.Unmarshal(data, &raw)
	maxID := 0
	for _, u := range raw.Users {
		if u.ID > maxID {
			maxID = u.ID
		}
	}
	return maxID + 1
}

func saveUserToRedis(u models.User) {
	// For simplicity, store new user in users.json
	data, _ := os.ReadFile("users.json")
	var raw struct {
		Users []models.User `json:"users"`
		Roles []models.Role `json:"roles"`
	}
	json.Unmarshal(data, &raw)

	raw.Users = append(raw.Users, u)
	newBytes, _ := json.MarshalIndent(raw, "", "  ")
	os.WriteFile("users.json", newBytes, 0644)

	// Also push to Redis if needed
	// ...
}

func createSessionInRedis(userID int) string {
	// In real code, generate a UUID or random token
	// and store it in Redis db15
	return strconv.Itoa(userID) + "-session"
}

func getConfigFromRedis() models.Config {
	// For simplicity, read config.json instead of actual Redis
	fileData, _ := os.ReadFile("config.json")
	var c models.Config
	json.Unmarshal(fileData, &c)
	return c
}
