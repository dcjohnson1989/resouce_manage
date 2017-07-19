drop table if exists resource_list;
create table import_list (
	id integer primary key autoincrement,
	name char not null,
	brand char not null,
	quantity integer not null,
	import_date datetime not null,
	expire_date datetime not null,
	storage char not null,
	total_price real not null
);
create table resource_list (
	id integer primary key autoincrement,
	name char not null,
	brand char not null,
	quantity integer not null,
	-- import_date datetime not null,
	expire_date datetime not null,
	storage char not null,
	total_price real not null
);
create table recipe_list (
	dessert char not null,
	resource_id integer not null,
	quantity integer not null
);