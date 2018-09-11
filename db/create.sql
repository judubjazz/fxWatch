create table Users (
  id integer primary key,
  username varchar(32) UNIQUE,
  email varchar(32) UNIQUE,
  salt varchar(32),
  hash varchar(128)
);

create table sessions (
  id integer primary key,
  id_session varchar(32),
  username varchar(32)
);


create table Rates (
  id integer primary key,
  symbol varchar(32),
  bid float,
  ask float,
  average float,
  delta varchar(32),
  date_created varchar(16)
);

create table Eurcad (
  id integer primary key,
  symbol varchar(32),
  bid float,
  ask float,
  average float,
  delta varchar(32),
  date_created varchar(16)
);

create table Eurusd (
  id integer primary key,
  symbol varchar(32),
  bid float,
  ask float,
  average float,
  delta varchar(32),
  date_created varchar(16)
);

create table Euraud (
  id integer primary key,
  symbol varchar(32),
  bid float,
  ask float,
  average float,
  delta varchar(32),
  date_created varchar(16)
);

create table Eurchf (
  id integer primary key,
  symbol varchar(32),
  bid float,
  ask float,
  average float,
  delta varchar(32),
  date_created varchar(16)
);

create table Audcad (
  id integer primary key,
  symbol varchar(32),
  bid float,
  ask float,
  average float,
  delta varchar(32),
  date_created varchar(16)
);

create table Audusd (
  id integer primary key,
  symbol varchar(32),
  bid float,
  ask float,
  average float,
  delta varchar(32),
  date_created varchar(16)
);

create table Audchf (
  id integer primary key,
  symbol varchar(32),
  bid float,
  ask float,
  average float,
  delta varchar(32),
  date_created varchar(16)
);

create table Usdchf (
  id integer primary key,
  symbol varchar(32),
  bid float,
  ask float,
  average float,
  delta varchar(32),
  date_created varchar(16)
);

create table Usdcad (
  id integer primary key,
  symbol varchar(32),
  bid float,
  ask float,
  average float,
  delta varchar(32),
  date_created varchar(16)
);

create table Cadchf (
  id integer primary key,
  symbol varchar(32),
  bid float,
  ask float,
  average float,
  delta varchar(32),
  date_created varchar(16)
);

create table DailyRates (
  id integer primary key,
  data text,
  date_created varchar(16)
);


