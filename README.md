# python-bucketlist-app

This is my second application that using flask framework. This application is an case that I use to learn flask. This application can create user, login user, logout, display all user and add bucket list for every user. I am referring from this tutorial : https://code.tutsplus.com/tutorials/creating-a-web-app-from-scratch-using-python-flask-and-mysql--cms-22972 

# Database Structure
```mysql
CREATE DATABASE BucketList;
```

```mysql
CREATE TABLE `user` (
  `id` BIGINT NULL AUTO_INCREMENT,
  `name` VARCHAR(45) NULL,
  `username` VARCHAR(45) NULL,
  `password` VARCHAR(45) NULL,
  `bio` VARCHAR(255) NULL,
PRIMARY KEY (`user_id`));
```

```mysql
CREATE TABLE `wish` (
  `wish_id` int(11) NOT NULL AUTO_INCREMENT,
  `wish_title` varchar(45) DEFAULT NULL,
  `wish_description` varchar(5000) DEFAULT NULL,
  `wish_user_id` int(11) DEFAULT NULL,
  `wish_date` datetime DEFAULT NULL,
  PRIMARY KEY (`wish_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1;
```