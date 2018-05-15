create table Users (
  id integer primary key,
  username varchar(32) UNIQUE,
  name varchar(32),
  family_name varchar(32),
  phone varchar(32),
  address varchar(128),
  email varchar(32) UNIQUE,
  salt varchar(32),
  hash varchar(128)
);

create table Animal (
  id integer primary key,
  name varchar(64),
  type varchar(32),
  race varchar(32),
  age integer,
  date_creation date,
  description varchar(512),
  pic_id varchar(32),
  owner_id integer,
  FOREIGN KEY (owner_id) REFERENCES Users(id)
  ON DELETE NO ACTION
  ON UPDATE CASCADE
);

create table sessions (
  id integer primary key,
  id_session varchar(32),
  username varchar(32)
);

create table Account (
  id integer primary key,
  username varchar(32) UNIQUE,
  email varchar(32) UNIQUE,
  token varchar(32),
  date_sent text
);

create table Pictures (
  pic_id varchar(32) primary key,
  img_data blob
);



