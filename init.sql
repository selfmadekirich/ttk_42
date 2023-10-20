create schema dev;


create  table dev.user(
	tb_login bigint not null,
	pass_hash text not null,
	email text not null,
	PRIMARY KEY(tb_login, pass_hash, email)
);


 create  table dev.train(
    train_id serial primary key,
    train varchar(10) not null,
	wagon int not null,
	place int not null
);


 create  table dev.ride(
    ride_id serial primary key,
	tg_login bigint not null,
	train_id bigint not null,
	create_dttm timestamp
);


create  table dev.order(
	order_id SERIAL PRIMARY key,
	item_id bigint not null,
	comment text null
);


create  table dev.passport_x_train(
	train_id bigint not null,
	user_name text not null,
	pass_num int not null,
	pass_ser text not null
);


create  table dev.item(
	item_id serial primary key,
	name varchar(50) not null,
	price int not null,
	img text not null,
    description text
);


create  table dev.ride_x_item(
	train_id bigint not null,
	wagon bigint not null,
	item_id bigint not null,
	quantity int not null	
);
