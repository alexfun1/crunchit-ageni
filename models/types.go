package models

type User struct {
	ID       int    `json:"id"`
	Login    string `json:"login"`
	Password string `json:"password"`
	Name     string `json:"name"`
	Email    string `json:"email"`
	Phone    string `json:"phone"`
	Address  string `json:"address"`
	Role     int    `json:"role"`
	Mana     int    `json:"mana"`
}

type Role struct {
	ID   int    `json:"id"`
	Name string `json:"name"`
}

type Config struct {
	Registration struct {
		BlockedLoginsNames []string `json:"blocked_logins_names"`
		VerifyEmail        bool     `json:"verify_email"`
		VerifyPhone        bool     `json:"verify_phone"`
		DefaultRole        int      `json:"default_role"`
	} `json:"registration"`

	FeaturesEnabled        map[string]map[string][]string `json:"features_enabled"`
	ConnectedProviders     []string                       `json:"connected_providers"`
	ProviderConfig         map[string]interface{}         `json:"provider_config"`
	ProviderFeatures       map[string][]string            `json:"provider_features"`
	ProviderFeaturesConfig map[string]interface{}         `json:"provider_features_config"`
}
