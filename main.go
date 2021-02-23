package main

import (
	"database/sql"
	"encoding/json"
	firebase "firebase.google.com/go"
	"fmt"
	"github.com/gorilla/mux"
	_ "github.com/lib/pq"
	"golang.org/x/net/context"
	"google.golang.org/api/option"
	"log"
	"net/http"
	"os"
	"strconv"
	"time"
)

type BookingWithToken struct {
	Email     string
	StartTime time.Time
	EndTime   time.Time
	RouteID   int
	Token     string
}

type UpdateQuery struct {
	QueryTimeStart time.Time
	QueryTimeEnd   time.Time
	RouteID        int
}

type UpdateResponse struct {
	IsUpdateReqd bool
}

type Bookings []BookingWithToken

var db *sql.DB
var app *firebase.App

func InsertBooking(booking BookingWithToken) {
	var err error
	sqlStatement := `
	INSERT INTO cab_sharing (Email, StartTime, EndTime, RouteID, UID)
	VALUES ($1, $2, $3, $4, $5)`
	_, err = db.Exec(sqlStatement, booking.Email, booking.StartTime, booking.EndTime, booking.RouteID, booking.Token)
	if err != nil {
		panic(err)
	}
}

func PublishHandler(w http.ResponseWriter, request *http.Request) {
	decoder := json.NewDecoder(request.Body)
	var booking BookingWithToken
	err := decoder.Decode(&booking)
	if err != nil {
		panic(err)
	}
	client, err := app.Auth(context.Background())
	if err != nil {
		fmt.Printf("error getting Auth client: %v\n", err)
		return
	}
	token, err := client.VerifyIDToken(request.Context(), booking.Token)

	if err != nil {
		fmt.Printf("error verifying ID token: %v\n", err)
		return
	}
	UID := token.UID
	fmt.Printf("Verified ID token: %v\n", token)
	var bookingWithUid = BookingWithToken{booking.Email, booking.StartTime, booking.EndTime, booking.RouteID, UID}
	InsertBooking(bookingWithUid)
}

func QueryHandler(w http.ResponseWriter, request *http.Request) {
	query := `select * from cab_sharing ;`
	rows, err := db.Query(query)
	if err != nil {
		fmt.Println(err)
		return
	}
	defer rows.Close()
	var bookings Bookings
	for rows.Next() {
		var booking BookingWithToken
		if err := rows.Scan(&booking.Email, &booking.StartTime, &booking.EndTime, &booking.RouteID); err != nil {
			fmt.Println(err)
			return
		}
		bookings = append(bookings, booking)
	}
	bookingsJSON, err := json.Marshal(bookings)
	if err != nil {
		fmt.Println("Cannot encode to JSON ", err)
		return
	}
	w.Header().Set("Content-Type", "application/json")
	w.Write(bookingsJSON)
}

func isUpdateRequired(QueryTimeStart time.Time, QueryTimeEnd time.Time, RouteID int) bool {
	query := `select * from cab_sharing where StartTime <= $1 and EndTime >= $2 and RouteID = $3;`
	rows, err := db.Query(query, QueryTimeEnd, QueryTimeStart, RouteID)
	if err != nil {
		fmt.Println(err)
		return false
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
	if err != nil {
		panic(err)
	}
	updateResponse := UpdateResponse{isUpdateRequired(updateQuery.QueryTimeStart, updateQuery.QueryTimeEnd, updateQuery.RouteID)}
	updateJSON, err := json.Marshal(updateResponse)
	if err != nil {
		panic(err)
	}
	w.Header().Set("Content-Type", "application/json")
	w.Write(updateJSON)
}

func DeleteHandler(w http.ResponseWriter, request *http.Request) {
	decoder := json.NewDecoder(request.Body)
	var booking BookingWithToken
	err := decoder.Decode(&booking)
	if err != nil {
		panic(err)
	}
	client, err := app.Auth(context.Background())
	if err != nil {
		fmt.Printf("error getting Auth client: %v\n", err)
		return
	}
	token, err := client.VerifyIDToken(request.Context(), booking.Token)

	if err != nil {
		fmt.Printf("error verifying ID token: %v\n", err)
		return
	}
	UID := token.UID
	fmt.Printf("Verified ID token: %v\n", token)
	sqlStatement := `
	DELETE FROM cab_sharing
	WHERE Email = $1 AND StartTime = $2 AND EndTime = $3 AND RouteID = $4 AND UID = $5;`
	_, err = db.Exec(sqlStatement, booking.Email, booking.StartTime, booking.EndTime, booking.RouteID, UID)
	if err != nil {
		fmt.Println("Error deleting record ", err)
	}
}

func DiningHandler(w http.ResponseWriter, r *http.Request) {
	http.ServeFile(w, r, "static/dining.json")
}

func BusHandler(w http.ResponseWriter, r *http.Request) {
	http.ServeFile(w, r, "static/bus.json")
}

func main() {
	PORT, err := strconv.Atoi(os.Getenv("POSTGRES_PORT"))
	psqlInfo := fmt.Sprintf("host=%s port=%d user=%s "+
		"password=%s dbname=%s sslmode=disable",
		os.Getenv("POSTGRES_HOST"), PORT, os.Getenv("POSTGRES_USER"), os.Getenv("POSTGRES_PASS"), os.Getenv("POSTGRES_DB"))
	db, err = sql.Open("postgres", psqlInfo)
	if err != nil {
		panic(err)
	}
	defer db.Close()

	err = db.Ping()
	if err != nil {
		panic(err)
	}
	opt := option.WithCredentialsFile("aims-helper-247320-fd071f06e365.json")
	app, _ = firebase.NewApp(context.Background(), nil, opt)
	fmt.Println("Successfully connected to PostgreSQL Database!")
	r := mux.NewRouter()
	r.HandleFunc("/publish", PublishHandler)
	r.HandleFunc("/query", QueryHandler)
	r.HandleFunc("/update", UpdateHandler)
	r.HandleFunc("/delete", DeleteHandler)
	r.HandleFunc("/dining", DiningHandler)
	r.HandleFunc("/v2/bus", BusHandler)
	r.Handle("/curriculum", http.FileServer(http.Dir("./static/curriculum")))
	fmt.Println("Set up server.")
	log.Fatal(http.ListenAndServe(":8000", r))
}
