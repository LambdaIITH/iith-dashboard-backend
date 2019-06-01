package main

import (
	"log"
	"net/http"

	"github.com/gorilla/mux"
)

func FirstHandler(w http.ResponseWriter, r *http.Request) {
	w.Write([]byte("Hello\n"))
}

func main() {
	WebRouter := mux.NewRouter()
	WebRouter.HandleFunc("/", FirstHandler)
	log.Fatal(http.ListenAndServe(":8000", WebRouter))
}
