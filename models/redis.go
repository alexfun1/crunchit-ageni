package models

import (
	"context"
	"fmt"

	"github.com/redis/go-redis/v9"
)

var ctx = context.Background()

type RedisClient struct {
	client *redis.Client
}

func NewRedisClient(addr, password string, db int) *RedisClient {
	rdb := redis.NewClient(&redis.Options{
		Addr:     addr,
		Password: password,
		DB:       db,
	})
	return &RedisClient{client: rdb}
}

func (rc *RedisClient) Ping() error {
	_, err := rc.client.Ping(ctx).Result()
	return err
}

// Example method
func (rc *RedisClient) Set(dbIndex int, key string, value string) error {
	oldDB := rc.client.Options().DB
	rc.client.Options().DB = dbIndex
	defer func() { rc.client.Options().DB = oldDB }()
	return rc.client.Set(ctx, key, value, 0).Err()
}

// and so on...
func (rc *RedisClient) Get(dbIndex int, key string) (string, error) {
	oldDB := rc.client.Options().DB
	rc.client.Options().DB = dbIndex
	defer func() { rc.client.Options().DB = oldDB }()

	val, err := rc.client.Get(ctx, key).Result()
	if err != nil {
		return "", err
	}
	return val, nil
}

// Additional methods for HGET/HSET, etc.
