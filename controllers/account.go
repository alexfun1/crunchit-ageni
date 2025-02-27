package controllers

import (
	"html/template"
	"net/http"
	"strconv"
)

func ShowAccountPage(w http.ResponseWriter, r *http.Request) {
	user := getLoggedInUser(r)
	if user == nil {
		http.Redirect(w, r, "/?error=Please+login", http.StatusFound)
		return
	}
	tmpl := template.Must(template.ParseFiles(
		"templates/layout.html",
		"templates/account.html",
	))
	tmpl.ExecuteTemplate(w, "layout", user)
}

func AddManaHandler(w http.ResponseWriter, r *http.Request) {
	user := getLoggedInUser(r)
	if user == nil {
		http.Redirect(w, r, "/?error=Please+login", http.StatusFound)
		return
	}
	// Add 100 mana
	user.Mana += 100
	saveUserToRedis(*user)
	http.Redirect(w, r, "/account?success=Added+100+mana", http.StatusFound)
}
