-- init database

drop database if exists awesome;

create database awesome;

use awesome;

create table users (
	`id` varchar(50) not null,
	`email` varchar(50) not null,
	`password` varchar(50) not null,
	`admin` bool not null,
	`name` varchar(50) not null,
	`image` varchar(500) not null,
	`created_at` real not null,
	unique key `idx_email` (`email`),
	key `idx_created_at` (`created_at`),
	primary key (`id`)
) engine=innodb default charset=utf8;

create table blogs (
	`id` varchar(50) not null,
	`user_id` varchar(50) not null,
	`user_name` varchar(50) not null,
	`user_image` varchar(500) not null,
	`name` varchar(50) not null,
	`summary` varchar(200) not null,
	`content` mediumtext not null,
	`created_at` real not null,
	key `idx_created_at` (`created_at`),
	primary key(`id`)
) engine=innodb default charset=utf8;

create table comments (
	`id` varchar(50) not null,
	`blog_id` varchar(50) not null,
	`user_name` varchar(50) not null,
	`user_image` varchar(500) not null,
	`content` mediumtext not null,
	`created_at` real not null,
	key `idx_created_at` (`created_at`),
	primary key(`id`)
) engine=innodb default charset=utf8;

insert into users values('001','test1@example.com','password',0,'name1','test.jpg',1479286841);
insert into users values('002','test2@example.com','password',0,'name2','test.jpg',1479286841);
insert into users values('003','test3@example.com','password',0,'name3','test.jpg',1479286841);
insert into users values('004','test4@example.com','password',0,'name4','test.jpg',1479286841);
insert into users values('005','test5@example.com','password',0,'name5','test.jpg',1479286841);
insert into users values('006','test6@example.com','password',0,'name6','test.jpg',1479286841);
insert into users values('007','test7@example.com','password',0,'name7','test.jpg',1479286841);
insert into users values('008','test8@example.com','password',0,'name8','test.jpg',1479286841);
insert into users values('009','test9@example.com','password',0,'name9','test.jpg',1479286841);
insert into users values('010','test10@example.com','password',0,'name10','test.jpg',1479286841);


