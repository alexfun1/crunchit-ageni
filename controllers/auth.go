package controllers

import (
	"encoding/json"
	"html/template"
	"net/http"
	"os"

	"myapp/models"
	"strconv"
	"strings"
)

func ShowLoginPage(w http.ResponseWriter, r *http.Request) {
	tmpl := template.Must(template.ParseFiles(
		"templates/layout.html",
		"templates/login.html",
	))
	tmpl.ExecuteTemplate(w, "layout", nil)
}

func LoginHandler(w http.ResponseWriter, r *http.Request) {
	r.ParseForm()
	username := r.Form.Get("username")
	password := r.Form.Get("password")

	// In a real scenario, you'd load the user from Redis db0 and compare hashed password
	user := findUserByLogin(username)
	if user == nil || user.Password != password {
		http.Redirect(w, r, "/?error=Invalid+credentials", http.StatusFound)
		return
	}

	// Create session (store in Redis or Gorilla session)
	sessionID := createSessionInRedis(user.ID)
	// Alternatively, store session in a cookie
	cookie := &http.Cookie{
		Name:     "session_id",
		Value:    sessionID,
		Path:     "/",
		HttpOnly: true,
		MaxAge:   1800, // 30 minutes
	}
	http.SetCookie(w, cookie)
	http.Redirect(w, r, "/main", http.StatusFound)
}

func LogoutHandler(w http.ResponseWriter, r *http.Request) {
	// Invalidate session
	cookie := &http.Cookie{
		Name:   "session_id",
		Value:  "",
		Path:   "/",
		MaxAge: -1, // expires
	}
	http.SetCookie(w, cookie)
	http.Redirect(w, r, "/", http.StatusFound)
}

func ShowRegisterPage(w http.ResponseWriter, r *http.Request) {
	tmpl := template.Must(template.ParseFiles(
		"templates/layout.html",
		"templates/register.html",
	))
	tmpl.ExecuteTemplate(w, "layout", nil)
}

func RegisterHandler(w http.ResponseWriter, r *http.Request) {
	r.ParseForm()
	email := r.Form.Get("email")
	pass1 := r.Form.Get("password")
	pass2 := r.Form.Get("confirm_password")
	if pass1 != pass2 {
		http.Redirect(w, r, "/register?error=Passwords+do+not+match", http.StatusFound)
		return
	}

	// Load config from Redis or file
	cfg := getConfigFromRedis()
	blocked := cfg.Registration.BlockedLoginsNames
	localPart := strings.Split(email, "@")[0]
	for _, b := range blocked {
		if b == localPart {
			http.Redirect(w, r, "/register?error=Blocked+username", http.StatusFound)
			return
		}
	}

	// Create new user
	user := models.User{
		ID:       getNextUserID(),
		Login:    localPart,
		Password: pass1,
		Email:    email,
		Role:     cfg.Registration.DefaultRole,
		Mana:     100,
	}
	saveUserToRedis(user)
	http.Redirect(w, r, "/?success=Registration+successful", http.StatusFound)
}

// Helpers - in real code, these would be in separate files or models package

func findUserByLogin(login string) *models.User {
	// Load from Redis db0
	// This is just a placeholder reading from users.json
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
	// For brevity, just appending to users.json
	data, _ := os.ReadFile("users.json")
	var raw struct {
		Users []models.User `json:"users"`
		Roles []models.Role `json:"roles"`
	}
	json.Unmarshal(data, &raw)
	raw.Users = append(raw.Users, u)
	newBytes, _ := json.MarshalIndent(raw, "", "  ")
	os.WriteFile("users.json", newBytes, 0644)
	// Also store in Redis if needed
}

func getConfigFromRedis() models.Config {
	// Just load from config.json for this example
	fileData, _ := os.ReadFile("config.json")
	var c models.Config
	json.Unmarshal(fileData, &c)
	return c
}

func createSessionInRedis(userID int) string {
	// In real code, generate a UUID and store it in Redis db15 with a timestamp
	return strconv.Itoa(userID) + "-session"
}
