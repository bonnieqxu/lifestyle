-- USE LLCMS;

-- Drop tables with dependencies
DROP TABLE IF EXISTS payment;
DROP TABLE IF EXISTS booking;
DROP TABLE IF EXISTS workshop;
DROP TABLE IF EXISTS lesson;

-- Drop tables with dependencies on user
DROP TABLE IF EXISTS staff;
DROP TABLE IF EXISTS member;
-- DROP TABLE IF EXISTS image;

-- Drop tables with no dependencies
DROP TABLE IF EXISTS workshop_info;
DROP TABLE IF EXISTS lesson_info;

-- Drop other tables
DROP TABLE IF EXISTS location;
DROP TABLE IF EXISTS subscription;
DROP TABLE IF EXISTS news;

DROP TABLE IF EXISTS user;


CREATE TABLE IF NOT EXISTS user(
	user_id int NOT NULL auto_increment,
	username varchar(20) NOT NULL,
	passwordHash varchar(255) NOT NULL,
    userrole char(2) NOT NULL,
    status char(1) NOT NULL,
	PRIMARY KEY (user_id)
);

CREATE TABLE IF NOT EXISTS member (
	member_id int NOT NULL,
    member_title char(3) DEFAULT NULL,
    member_firstname varchar(50) NOT NULL,
    member_familyname varchar(50) NOT NULL,
	member_position varchar(50) DEFAULT NULL,
	member_phonenumber varchar(20) DEFAULT NULL,
    member_email varchar(50) DEFAULT NULL,
	member_address varchar(120) DEFAULT NULL,
	member_dob date DEFAULT NULL,
    member_profile text default NULL,
    member_subscription_type char(2) DEFAULT NULL,
    member_subscription_expiry_date date default NULL,
	PRIMARY KEY (member_id),
	FOREIGN KEY (member_id) REFERENCES user(user_id)
);

CREATE TABLE IF NOT EXISTS staff (
	staff_id int NOT NULL,
	staff_title char(3) DEFAULT NULL,
    staff_firstname varchar(50) NOT NULL,
    staff_familyname varchar(50) NOT NULL,
	staff_position varchar(50) DEFAULT NULL,
	staff_phonenumber varchar(20) DEFAULT NULL,
    staff_email varchar(50) DEFAULT NULL,
    staff_profile text default NULL,
	PRIMARY KEY (staff_id),
	FOREIGN KEY (staff_id) REFERENCES user(user_id)
);

CREATE TABLE IF NOT EXISTS image(
	image_id int NOT NULL auto_increment,
    user_id int NOT NULL,
    image varchar(255) default NULL,
    primary key (image_id),
    foreign key (user_id) references user(user_id)
);

CREATE TABLE IF NOT EXISTS workshop_info(
	workshop_info_id int NOT NULL auto_increment,
    workshop_info_topic varchar(100) default NULL,
    workshop_info_desc TEXT default NULL,
    primary key (workshop_info_id)
);

CREATE TABLE IF NOT EXISTS lesson_info(
	lesson_info_id int NOT NULL auto_increment,
    lesson_info_type varchar(100) default NULL,
    lesson_info_desc TEXT default NULL,
    primary key (lesson_info_id)
);

CREATE TABLE IF NOT EXISTS workshop(
	workshop_id int NOT NULL auto_increment,
    workshop_tutor_id int not null,
    workshop_title_id int not NULL,
    workshop_detail text default NULL,
	workshop_date date default NULL,
    workshop_time time default NULL,
    workshop_location int not Null,
    workshop_cost decimal default NULL,
    workshop_cap_limit int default NULL,
	workshop_attendance int default NULL,
    primary key (workshop_id),
    foreign key (workshop_tutor_id) references staff(staff_id),
    foreign key (workshop_title_id) references workshop_info(workshop_info_id)
);

CREATE TABLE IF NOT EXISTS lesson(
	lesson_id int NOT NULL auto_increment,
    lesson_title_id int not NULL,
    lesson_tutor_id int not NULL,
	lesson_location int not Null,
    lesson_date date default NULL,
    lesson_start_time time default NULL,
    lesson_booked boolean default false,
	lesson_detail text default NULL,
	lesson_attendance int default NULL,
    primary key (lesson_id),
    foreign key (lesson_tutor_id) references staff(staff_id),
    foreign key (lesson_title_id) references lesson_info(lesson_info_id)
);

CREATE TABLE IF NOT EXISTS booking(
	booking_id int NOT NULL auto_increment,
    booking_member_id int not NULL,
    booking_workshop_id int default NULL,
	booking_lesson_id int default NULL,
    booking_staff_id int not NULL,
    booking_attended boolean default NULL,
    booking_date date default Null,
    primary key (booking_id),
    foreign key (booking_member_id) references member(member_id),
    foreign key (booking_workshop_id) references workshop(workshop_id),
    foreign key (booking_lesson_id) references lesson(lesson_id)
);

CREATE TABLE IF NOT EXISTS location(
	location_id int NOT NULL auto_increment,
    location_name varchar(12) default NULL,
    location_description text default NULL,
    location_map varchar(255) default NULL,
    location_limit int default NULL,
    primary key (location_id)
);

CREATE TABLE IF NOT EXISTS subscription(
	subscription_id int NOT NULL auto_increment,
    subscription_type char(1) default NULL,
    subscription_cost decimal default NULL,
    subscription_discount decimal default NULL,
    primary key (subscription_id)
);

CREATE TABLE IF NOT exists payment(
	payment_id int NOT NULL auto_increment,
    payment_type char(1) default NULL,
    payment_workshop_id int default NULL,
    payment_lesson_id int default NULL,
    payment_subscription_id int default NULL,
    payment_date date default NULL,
    payment_payor_id int default NULL,
    payment_amount decimal(5,2) default NULL,
    primary key (payment_id),
    foreign key (payment_workshop_id) references workshop(workshop_id),
    foreign key (payment_lesson_id) references lesson(lesson_id),
    foreign key (payment_subscription_id) references subscription(subscription_id),
    foreign key (payment_payor_id) references member(member_id)
);

CREATE TABLE IF NOT EXISTS news(
	news_id int NOT NULL auto_increment,
    new_title varchar(120) default NULL,
    news_text longtext default NULL,
    news_image varchar(255) default NULL,
    news_uploaded datetime default NULL,
    primary key (news_id)
);


