package main

import (
	"fmt"
	// "math/rand/v2"
	"sync"
	"time"
)

type Limiter interface {
	Allow() bool // reports whether an event may happen now. If true, it will consume an token.
	Wait()       // blocks until an event can happen. It will consume an token.
}

type tokenBucket struct {
	mu    sync.Mutex
	token int // if token is negative, there's some events waiting to happen (i.e. in the queue)
	size  int // bucket size, which allows burst events
	rate  int // token refill rate per second
}

var _ Limiter = &tokenBucket{}

func NewTokenBucket(rate int, size int) *tokenBucket {
	t := &tokenBucket{size: size, rate: rate}
	go func() {
		// refill process
		c := time.Tick(time.Second)
		for range c {
			t.mu.Lock()
			r := t.token + t.rate
			if r > t.size {
				r = t.size
			}
			t.token = r
			t.mu.Unlock()
		}
	}()
	return t
}

func (t *tokenBucket) Allow() bool {
	t.mu.Lock()
	defer t.mu.Unlock()
	if t.token > 0 {
		t.token--
		return true
	} else {
		return false
	}
}

func (t *tokenBucket) Wait() {
	t.mu.Lock()
	if t.token > 0 {
		t.token--
		return
	}
	// the token will be reserved in the future
	var waitMilli uint
	if t.token < 0 {
		waitMilli = uint(float64(-t.token) / float64(t.size) * 1000)
	}
	// min waiting time is 1s
	if waitMilli < 1000 {
		waitMilli = 1000
	}
	t.token--
	t.mu.Unlock()

	time.Sleep(time.Duration(waitMilli * uint(time.Millisecond)))

	// a token has already been consumed, so just return
	return
}

func consumer(id int, lim Limiter) {
	consumed := 0
	now := time.Now()
	for {
		if !lim.Allow() {
			lim.Wait()
		}
		consumed++
		if time.Now().Sub(now) >= time.Second {
			fmt.Printf("id %v consumed %v tokens in the past second\n", id, consumed)
			// s := rand.Int() % 10
			// fmt.Printf("id %v sleeping %v second(s)\n", id, s)
			// time.Sleep(time.Duration(s) * time.Second)
			now = time.Now()
			consumed = 0
		}
	}
}

func main() {
	lim := NewTokenBucket(100, 200)
	for i := range 1 {
		go consumer(i, lim)
	}
	select {}
}
