drop table if exists resource_list;
create table resource_list (
	id integer primary key autoincrement,
	name char not null,
	brand char not null,
	quantity integer not null,
	expire_date datetime not null,
	storage char not null,
	price real not null
);
-- create table resource_price (
-- 	id integer not null,
-- 	price real not null
-- );