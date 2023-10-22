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
	train_id bigint not null
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
	img text not null
);


create  table dev.ride_x_item(
	train_id bigint not null,
	wagon bigint not null,
	item_id bigint not null,
	quantity int not null	
);


 CREATE OR REPLACE FUNCTION dev.register (
    tg_id bigint,
    pass text,
    email text
)
RETURNS text
AS $$
DECLARE
    tb_lgn bigint;
BEGIN
    tb_lgn := coalesce((select 1 from dev.user u where u.tb_login = tg_id),0);
    if tb_lgn <> 0 then 
    	return 'User already exists';
    end if;

    insert into dev.user(tb_login,pass_hash,email) values(tg_id,pass,email);
   return 'ok';
END;
$$ 
LANGUAGE plpgsql VOLATILE SECURITY DEFINER;

drop function dev.login(text,text);
 CREATE OR REPLACE FUNCTION dev.login (
    pass text,
    ml text
)
RETURNS text
AS $$
DECLARE
    tb_lgn bigint;
BEGIN
    tb_lgn := coalesce((select 1 from dev.user u where u.pass_hash = pass and u.email = ml),0);
    if tb_lgn = 0 then 
    	return 'User not found. Check login or password';
    end if;

   return 'ok';
END;
$$ 
LANGUAGE plpgsql VOLATILE SECURITY DEFINER;

drop function if exists dev.add_ride(text,integer,integer,bigint);
   CREATE OR REPLACE FUNCTION dev.add_ride (
    tr text,
    w int,
    p int,
    tg_id bigint
)
RETURNS text
AS $$
DECLARE
    tr_id bigint;
    us_id bigint;
BEGIN
    tr_id := coalesce((select t.train_id from dev.train t where t.train = tr and t.wagon = w and t.place = p),0);
    if tr_id = 0 then 
    	return 'Train not found. Check train information';
    end if;
    us_id := coalesce((select 1 from dev.user u where u.tb_login = tg_id),0);
   if us_id = 0 then 
    	return 'User not found';
    end if;
   insert into dev.ride(tg_login,train_id) values (tg_id,tr_id);
   return 'ok';
END;
$$ 
LANGUAGE plpgsql VOLATILE SECURITY DEFINER;


INSERT INTO dev.item (name, price, img, description) VALUES
('Кола', 100, 'Кола.jpg', 'Газированный напиток с колой'),
('Апельсиновый сок',100, 'Апельсиновый сок.jpg', 'Свежевыжатый апельсиновый сок'),
('Чипсы', 150, 'Чипсы.jpg', 'Соленые чипсы'),
('Попкорн', 160, 'Попкорн.jpg', 'Сладкий попкорн'),
('Шоколад', 300, 'Шоколад.jpg', 'Молочный шоколад'),
('Мармелад', 150, 'Мармелад.jpg', 'Разноцветный мармелад'),
('Пицца', 120, 'Пицца.jpg', 'Пицца с разнообразными начинками'),
('Бургер', 180, 'Бургер.jpg', 'Сочный бургер с картофелем фри');


iNSERT INTO dev.train (train, wagon, place)
SELECT
'001А'::text AS train,
1 as  wagon,
1 AS place

insert into dev.ride_x_item(train_id,wagon,item_id,quantity) values (1,1,1,10);

drop function if exists dev.get_items_for_user(bigint);
 CREATE OR REPLACE FUNCTION dev.get_items_for_user (
    tg_id bigint
)
RETURNS text
AS $$
DECLARE
    tr_id bigint;
    w int;
begin
	tr_id := coalesce((select 1 from dev.user u where u.tb_login = tg_id),0);
   if tr_id = 0 then 
    	return 'User not found';
    end if;
    tr_id := coalesce((select r.train_id from dev.ride r where r.tg_login = tg_id),0);
   if tr_id = 0 then 
    	return 'Ride not found';
    end if;
   
   return json_build_object('item_name',name,
                            'price',price,
                            'img_src',img,
                            'quantity',quantity) item_info from(
                            select name , price , img, quantity from dev.item i join 
                            dev.ride_x_item x on i.item_id = x.item_id
                            join dev.train t on t.train_id = x.train_id 
                            where t.train_id = tr_id and x.wagon = (select wagon from dev.train t1 where t1.train_id = tr_id)
                            ) a;
                            
END;
$$ 
LANGUAGE plpgsql VOLATILE SECURITY DEFINER;



drop function if exists dev.add_ride_by_passport(text,integer,bigint);
 CREATE OR REPLACE FUNCTION dev.add_ride_by_passport (
    s text,
    n int,
    tg_id bigint
)
RETURNS text
AS $$
DECLARE
    tr_id bigint;
    us_id bigint;
BEGIN
    tr_id := coalesce((select t.train_id from dev.passport_x_train t where t.pass_num = n and t.pass_ser = s),0);
    if tr_id = 0 then 
    	return 'Train not found. Check train information';
    end if;
    us_id := coalesce((select 1 from dev.user u where u.tb_login = tg_id),0);
   if us_id = 0 then 
    	return 'User not found';
    end if;
   insert into dev.ride(tg_login,train_id) values (tg_id,tr_id);
   return 'ok';
END;
$$ 
LANGUAGE plpgsql VOLATILE SECURITY DEFINER;

insert into dev.passport_x_train(train_id,pass_ser ,pass_num ,user_name) values (1,'0000','000000','Иванов Иван Иваныч')
