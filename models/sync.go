package models

import (
	"encoding/json"
	"fmt"
	"os"
)

// These constants match your plan for storing data in Redis
const (
	UsersDB   = 0
	ConfigDB  = 1
	SessionDB = 15
)

func SyncUsers(rc *RedisClient) error {
	// 1. Load users.json
	fileData, err := os.ReadFile("users.json")
	if err != nil {
		// If file doesn't exist, skip or handle differently
		return nil
	}
	var raw struct {
		Users []User `json:"users"`
		Roles []Role `json:"roles"`
	}
	if err := json.Unmarshal(fileData, &raw); err != nil {
		return err
	}

	// 2. Check if Redis db0 is empty
	keys, err := rc.client.Keys(ctx, "*").Result()
	if err != nil {
		return err
	}
	if len(keys) == 0 {
		// 3. Populate from file
		for _, u := range raw.Users {
			key := fmt.Sprintf("user:%d", u.ID)
			data, _ := json.Marshal(u)
			rc.Set(UsersDB, key, string(data))
		}
		for _, r := range raw.Roles {
			key := fmt.Sprintf("role:%d", r.ID)
			data, _ := json.Marshal(r)
			rc.Set(UsersDB, key, string(data))
		}
	} else {
		// If Redis has data, read from Redis and possibly update the file
		// This is a placeholder. In practice, you'd read all keys, compare, merge, etc.
		// Then rewrite users.json.
	}

	return nil
}

func SyncConfig(rc *RedisClient) error {
	fileData, err := os.ReadFile("config.json")
	if err != nil {
		return nil
	}
	var cfg Config
	if err := json.Unmarshal(fileData, &cfg); err != nil {
		return err
	}

	// If config in Redis is empty, store from file
	keys, err := rc.client.Keys(ctx, "*").Result()
	if err != nil {
		return err
	}
	if len(keys) == 0 {
		data, _ := json.Marshal(cfg)
		if err := rc.Set(ConfigDB, "config_json", string(data)); err != nil {
			return err
		}
	} else {
		// Compare & possibly update file from DB
	}
	return nil
}
