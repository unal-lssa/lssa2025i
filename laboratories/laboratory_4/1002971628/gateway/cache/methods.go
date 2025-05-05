package cache

import (
	"context"
	"encoding/json"
	"time"
)

func (c *Cache) GetFromCache(ctx context.Context, key string) (interface{}, error) {
	return c.rdb.Get(ctx, key).Result()
}

func (c *Cache) GetStringSliceFromCache(ctx context.Context, key string) ([]string, error) {
	data, err := c.rdb.Get(ctx, key).Result()
	if err != nil {
		return []string{}, err
	}

	var res []string
	if err := json.Unmarshal([]byte(data), &res); err != nil {
		return []string{}, err
	}

	return res, nil
}

func (c *Cache) SetInCache(ctx context.Context, key string, value interface{}) error {
	data, err := json.Marshal(value)
	if err != nil {
		return err
	}
	return c.rdb.Set(ctx, key, data, time.Minute).Err()
}
