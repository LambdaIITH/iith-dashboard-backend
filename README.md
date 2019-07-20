# DASHBOARD BACKEND

Online now on http://13.233.90.143

## API REFERENCE

The API features 3 endpoints. 
1. Publish - /publish - This is used to register a cab booking. 
```
curl -X POST -d '{"Name": "that", "RollNo": "that", "StartTime": "2011-02-01T09:28:56.321+05:30", "EndTime": "2015-02-01T09:28:56.321+05:30", "RouteID": 9}' http://13.233.90.143/publish
```
The StartTime and EndTime timestamps indicate the time period in which the booker is conducive to a third party(the sharer) sharing the ride. These should conform to the ISO 8601 format and must be suffixed with +05:30 to indicate IST. The RouteID integer indicates the specific route (combination of destination and )