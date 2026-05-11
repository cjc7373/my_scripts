// A Read Write Lock implementation which only uses sync.Mutex

package main

import (
	"fmt"
	"log"
	"math/rand"
	"os"
	"sync"
	"time"
)

type RWLock struct {
	mu            sync.Mutex
	reader_cnt    int
	writer_cnt    int
	readRequests  []*sync.Mutex
	writeRequests []*sync.Mutex
}

func (rw *RWLock) ReaderLock(logger *log.Logger) {
	rw.mu.Lock()
	if rw.writer_cnt != 0 || len(rw.writeRequests) != 0 {
		var mu sync.Mutex
		rw.readRequests = append(rw.readRequests, &mu)
		logger.Printf("added to reader queue, rw.writer_cnt: %v\n", rw.writer_cnt)
		mu.Lock()
		rw.mu.Unlock()
		mu.Lock() // block!
		rw.mu.Lock()
	}
	logger.Println("aquired read lock")
	rw.reader_cnt += 1
	rw.mu.Unlock()
}

func (rw *RWLock) ReaderUnlock(logger *log.Logger) {
	rw.mu.Lock()
	defer rw.mu.Unlock()
	rw.reader_cnt -= 1
	logger.Println("released read lock")
	if rw.reader_cnt == 0 && len(rw.writeRequests) != 0 {
		logger.Println("unblock one writer")
		w := rw.writeRequests[0]
		w.Unlock()
		rw.writeRequests = rw.writeRequests[1:]
	}
}

func (rw *RWLock) WriterLock(logger *log.Logger) {
	rw.mu.Lock()
	if rw.reader_cnt != 0 || rw.writer_cnt != 0 {
		// have readers or other writers
		var mu sync.Mutex
		rw.writeRequests = append(rw.writeRequests, &mu)
		logger.Printf("added to writer queue, rw.reader_cnt: %v, rw.writer_cnt: %v\n", rw.reader_cnt, rw.writer_cnt)
		mu.Lock()
		rw.mu.Unlock()
		mu.Lock() // block!
		rw.mu.Lock()
	}
	logger.Println("aquired write lock")
	rw.writer_cnt += 1
	rw.mu.Unlock()
}

func (rw *RWLock) WriterUnlock(logger *log.Logger) {
	rw.mu.Lock()
	defer rw.mu.Unlock()
	rw.writer_cnt -= 1
	logger.Println("released write lock")
	logger.Printf("Unblocking all the readers, len(rw.readRequests): %v", len(rw.readRequests))
	for len(rw.readRequests) != 0 {
		r := rw.readRequests[0]
		r.Unlock()
		rw.readRequests = rw.readRequests[1:]
	}
}

var rw RWLock

func reader(id int) {
	log_prefix := fmt.Sprintf("Reader %v ", id)
	logger := log.New(os.Stdout, log_prefix, log.Lshortfile)
	for {
		rw.ReaderLock(logger)
		time.Sleep(time.Duration(100*rand.Intn(10)) * time.Millisecond)
		logger.Println("successfully read!")
		rw.ReaderUnlock(logger)
		time.Sleep(time.Duration(100*rand.Intn(10)) * time.Millisecond)
	}
}

func writer(id int) {
	log_prefix := fmt.Sprintf("Writer %v ", id)
	logger := log.New(os.Stdout, log_prefix, log.Lshortfile)
	for {
		rw.WriterLock(logger)
		time.Sleep(time.Duration(100*rand.Intn(10)) * time.Millisecond)
		logger.Println("successfully wrote!")
		rw.WriterUnlock(logger)
		time.Sleep(time.Duration(rand.Intn(1000)) * time.Millisecond)
	}
}

func main() {
	for i := 1; i <= 10; i++ {
		go reader(i)
	}

	for i := 1; i <= 10; i++ {
		go writer(i)
	}

	for {
		rw.mu.Lock()
		fmt.Printf("---------------\nStatistics:\n")
		fmt.Printf("reader_cnt: %v\n", rw.reader_cnt)
		fmt.Printf("writer_cnt: %v\n", rw.writer_cnt)
		fmt.Printf("len(rw.readRequests): %v\n", len(rw.readRequests))
		fmt.Printf("len(rw.writeRequests): %v\n", len(rw.writeRequests))
		fmt.Printf("---------------\n")
		rw.mu.Unlock()
		time.Sleep(1 * time.Second)
	}
}
