CREATE TABLE cab_sharing(
	Email varchar(255) not null primary key,
  	StartTime timestamptz not null,
  	EndTime timestamptz not null,
  	RouteID int not null,
  	UID text not null
);
