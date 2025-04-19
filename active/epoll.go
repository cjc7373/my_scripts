package main

import (
	"fmt"
	"syscall"
)

func main() {
	var event syscall.EpollEvent
	var events [32]syscall.EpollEvent

	epfd, e := syscall.EpollCreate1(0)
	if e != nil {
		panic(e)
	}
	defer syscall.Close(epfd)

	event.Events = syscall.EPOLLIN
	event.Fd = 0

	if err := syscall.EpollCtl(epfd, syscall.EPOLL_CTL_ADD, 0, &event); err != nil {
		panic(err)
	}

	var buf [10]byte
	for {
		fmt.Println("\nepoll_wait for new events...")
		n, err := syscall.EpollWait(epfd, events[:], 30000)
		if err != nil {
			panic(err)
		}

		fmt.Printf("received %v event(s)\n", n)
		for i := 0; i < n; i++ {
			nbytes, err := syscall.Read(int(events[i].Fd), buf[:])
			if err != nil {
				panic(err)
			}
			fmt.Printf("%v bytes read from fd %v\n", nbytes, events[i].Fd)
			fmt.Printf("read '%v'\n", string(buf[:]))

			if string(buf[:]) == "stop\n" {
				break
			}
		}
	}
}
