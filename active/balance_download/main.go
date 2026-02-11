// Disclaimer: I'm not running a PCDN, just be afraid of being mistakenly banned by ISP.

package main

import (
	"context"
	"errors"
	"fmt"
	"io"
	"log/slog"
	"net/http"
	"time"

	"github.com/dustin/go-humanize"
	"golang.org/x/time/rate"
)

const (
	DOWNLOAD_URL       = "https://d.o0o0o0o.cn/Other/speedtest.bin"
	DOWNLOAD_SIZE      = 10 * 1024 * 1024 * 1024 // 10 GB, unit is bytes
	RATE_LIMIT_PER_SEC = 1024 * 1024             // 1 MB/s, unit is bytes/sec
)

var ErrDownloadReachedSize = errors.New("download reached target size")

func main() {
	f := NewRateLimitedWriter()
	for {
		resp, err := http.Get(DOWNLOAD_URL)
		if err != nil {
			slog.Error("error get", "err", err)
			continue
		}

		_, err = io.Copy(f, resp.Body)
		if err != nil {
			if errors.Is(err, ErrDownloadReachedSize) {
				slog.Info("download reached target size")
				break
			} else {
				slog.Error("error get", "err", err)
				continue
			}
		}
	}
}

type RateLimitedWriter struct {
	limiter    *rate.Limiter
	downloaded uint64 // bytes
	lastReport time.Time
}

func NewRateLimitedWriter() *RateLimitedWriter {
	return &RateLimitedWriter{
		limiter:    rate.NewLimiter(RATE_LIMIT_PER_SEC, RATE_LIMIT_PER_SEC*10),
		lastReport: time.Now(),
	}
}

func (w *RateLimitedWriter) Write(p []byte) (n int, err error) {
	remain := len(p)
	w.downloaded += uint64(remain)
	for remain > 0 {
		chuck := min(remain, RATE_LIMIT_PER_SEC)
		remain -= chuck
		if err := w.limiter.WaitN(context.Background(), chuck); err != nil {
			return 0, err
		}
	}

	if w.downloaded > DOWNLOAD_SIZE {
		return 0, ErrDownloadReachedSize
	}

	if time.Since(w.lastReport) > time.Second {
		now := time.Now()
		fmt.Printf("%s %s/%s\n", now.Format(time.RFC1123), humanize.IBytes(w.downloaded), humanize.IBytes(DOWNLOAD_SIZE))
		w.lastReport = now
	}

	return len(p), nil
}
