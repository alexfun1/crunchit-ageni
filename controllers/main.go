package controllers

import (
	"html/template"
	"myapp/models"
	"net/http"
)

func ShowMainPage(w http.ResponseWriter, r *http.Request) {
	user := getLoggedInUser(r)
	if user == nil {
		http.Redirect(w, r, "/?error=Please+login", http.StatusFound)
		return
	}

	tmpl := template.Must(template.ParseFiles(
		"templates/layout.html",
		"templates/main.html",
	))
	tmpl.ExecuteTemplate(w, "layout", nil)
}

func getLoggedInUser(r *http.Request) *models.User {
	cookie, err := r.Cookie("session_id")
	if err != nil || cookie.Value == "" {
		return nil
	}
	// Parse session from Redis, if valid
	// Placeholder to just parse out userID
	// Real code would do more robust session mgmt
	// e.g., "123-session"
	userIDStr := cookie.Value
	if userIDStr == "" {
		return nil
	}
	// We’ll just fetch from users.json again (demo)
	// In real usage, load from Redis db0
	return findUserByID(userIDStr)
}

func findUserByID(sessionVal string) *models.User {
	// This is just a placeholder
	// Typically you'd parse out the numeric user ID from the sessionVal
	return nil
}
