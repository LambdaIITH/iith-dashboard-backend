# DASHBOARD BACKEND

Online now on http://13.233.90.143

## API REFERENCE

The API features 3 endpoints. 
### Publish 
/publish - This is used to register a cab booking. 
```
curl -X POST -d '{"Name": "that", "RollNo": "that", "StartTime": "2011-02-01T09:28:56.321+05:30", "EndTime": "2015-02-01T09:28:56.321+05:30", "RouteID": 9}' http://13.233.90.143/publish
```
The StartTime and EndTime timestamps indicate the time period in which the booker is conducive to a third party(the sharer) sharing the ride. These should conform to the ISO 8601 format and must be suffixed with +05:30 to indicate IST. The RouteID integer indicates the specific route. 

### Update 
/update - This is used to check whether an update is required from the server. If the user suscribes to a QueryTime, the app keeps querying this endpoint at specific intervals, to see whether a booking which contains that QueryTime has been registered. 
```
curl -X POST -d '{"QueryTime": "2012-02-01T09:27:56.321+05:30"}' http://13.233.90.143/update
```
If a booking containing that QueryTime has been registered: 
```
{"IsUpdateReqd":true}
```

### Query 
/query - Returns a JSON object with all the bookings registered on the server. Just visit http://13.233.90.143/query and you should see all the bookings on the database. 