package main

import (
	"database/sql"
	"fmt"
	"time"
	"log"
	"encoding/json"
	_ "github.com/lib/pq"
	"github.com/gorilla/mux"
	"net/http"
)

type Booking struct {
	Name string
	RollNo string
	StartTime time.Time
	EndTime time.Time
	RouteID int
}

type UpdateQuery struct {
	QueryTimeStart time.Time
	QueryTimeEnd time.Time
}

type UpdateResponse struct {
	IsUpdateReqd bool
}

type Bookings []Booking 

const (
  host     = "localhost"
  port     = 5432
  user     = "postgres"
  password = "your-password"
  dbname   = "iith_dashboard"
)

var db *sql.DB

func InsertBooking(booking Booking) {
	var err error
	sqlStatement := `
	INSERT INTO cab_sharing (Name, RollNo, StartTime, EndTime, RouteID)
	VALUES ($1, $2, $3, $4, $5)`
	_, err = db.Exec(sqlStatement, booking.Name, booking.RollNo, booking.StartTime, booking.EndTime, booking.RouteID)
	if err != nil {
		panic(err)
	}
}

func PublishHandler (w http.ResponseWriter, request *http.Request) {
	decoder := json.NewDecoder(request.Body)
	var booking Booking
	err := decoder.Decode(&booking)
	if (err != nil) {
		panic(err)
	}
	InsertBooking(booking)
}

func QueryHandler (w http.ResponseWriter, request *http.Request) {
	query := `select * from cab_sharing ;`
	rows, err := db.Query(query)
	if err != nil {
		log.Fatal(err)
	}
	defer rows.Close()	
	var bookings Bookings
	for rows.Next() {
		var booking Booking 
		if err := rows.Scan(&booking.Name, &booking.RollNo, &booking.StartTime, &booking.EndTime, &booking.RouteID); err != nil {
			log.Fatal(err)
		}
		bookings = append(bookings, booking)
	}
	bookingsJSON, err := json.Marshal(bookings)
	if err != nil {
		log.Fatal("Cannot encode to JSON ", err)
	}
	w.Header().Set("Content-Type", "application/json")
	w.Write(bookingsJSON)
}

func isUpdateRequired(QueryTimeStart time.Time, QueryTimeEnd time.Time) bool {
	query := `select * from cab_sharing where StartTime <= $1 and EndTime >= $2;`
	rows, err := db.Query(query, QueryTimeEnd, QueryTimeStart)
	if err != nil {
		log.Fatal(err)
	}
	defer rows.Close()	
	doesExist := false
	for rows.Next() {
		doesExist = true
		break
	}
	return doesExist
}

func UpdateHandler(w http.ResponseWriter, request *http.Request) {
	decoder := json.NewDecoder(request.Body)
	var updateQuery UpdateQuery
	err := decoder.Decode(&updateQuery)
	if (err != nil) {
		panic(err)
	}
	updateResponse := UpdateResponse{isUpdateRequired(updateQuery.QueryTimeStart, updateQuery.QueryTimeEnd)}
	updateJSON, err := json.Marshal(updateResponse)
	if (err != nil) {
		panic(err)
	}
	w.Header().Set("Content-Type", "application/json")
	w.Write(updateJSON)
}

func main() {
	var err error 
	psqlInfo := fmt.Sprintf("host=%s port=%d user=%s "+
    "password=%s dbname=%s sslmode=disable",
    host, port, user, password, dbname)
	db, err = sql.Open("postgres", psqlInfo)
	if err != nil {
		panic(err)
	}
	defer db.Close()

	err = db.Ping()
	if err != nil {
		panic(err)
	}
	fmt.Println("Successfully connected to PostgreSQL Database!")
	r := mux.NewRouter()
	r.HandleFunc("/publish", PublishHandler)
	r.HandleFunc("/query", QueryHandler)
	r.HandleFunc("/update", UpdateHandler)
	fmt.Println("Set up server.")
	log.Fatal(http.ListenAndServe(":8000", r))
}