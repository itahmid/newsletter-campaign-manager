CREATE TABLE `newsletter`
(
    `newsletter_id` INT(11) UNSIGNED AUTO_INCREMENT,
    `code` VARCHAR(50) NOT NULL,
    `subject` VARCHAR(255) NOT NULL,
    `author` INT UNSIGNED NOT NULL,
    `company` INT(11) NOT NULL DEFAULT '0',
    `from_name` VARCHAR(80) NOT NULL,
    `from_email` VARCHAR(50) NOT NULL,
    `replyto_email` VARCHAR(50) NOT NULL,
    `unsub` TINYINT(1) NOT NULL DEFAULT '0',
    `date_added` INT(11) UNSIGNED NOT NULL,
    `date_sent` INT(11) UNSIGNED NOT NULL DEFAULT '0',
    `list_ids` VARCHAR(255) NOT NULL DEFAULT '0',
    PRIMARY KEY(`newsletter_id`)
);


CREATE TABLE `list`
(
    `list_id` INT(11) UNSIGNED AUTO_INCREMENT,
    `name` VARCHAR(255) NOT NULL,
    `description` VARCHAR(255) NOT NULL,
    `date_added` INT(11) UNSIGNED NOT NULL,
    `author` VARCHAR(50) NOT NULL,
    PRIMARY KEY(`list_id`)
);


CREATE TABLE `company`
(
    `company_id` INT(11) UNSIGNED AUTO_INCREMENT,
    `name` VARCHAR(50) NOT NULL,
    PRIMARY KEY(`company_id`)
);


CREATE TABLE `recipient`
(
    `recipient_id` INT(11) UNSIGNED AUTO_INCREMENT,
    `first_name` VARCHAR(50) NOT NULL,
    `last_name` VARCHAR(50) NOT NULL,
    `email` VARCHAR(100) NOT NULL,
    `list_ids` VARCHAR(255) NOT NULL DEFAULT '0,',
    `date_added` INT(11) UNSIGNED NOT NULL,
    PRIMARY KEY(`recipient_id`)
);


CREATE TABLE `staff`
(
    `staff_id` INT(11) UNSIGNED AUTO_INCREMENT,
    `name` VARCHAR(100) NOT NULL,
    `email` VARCHAR(100) NOT NULL,
    PRIMARY KEY(`staff_id`)
);


CREATE TABLE `user`
(
    `user_id` INT(11) UNSIGNED AUTO_INCREMENT,
    `name` VARCHAR(100) NOT NULL,
    `email` VARCHAR(100) NOT NULL,
    `password` VARCHAR(255) NOT NULL,
    `date_added` INT(11) UNSIGNED NOT NULL,
    `last_login` INT(11) NOT NULL default '0',
    PRIMARY KEY(`user_id`)
);


CREATE TABLE `template`
(
    `staff_id` INT(11) UNSIGNED AUTO_INCREMENT,
    `first_name` VARCHAR(50) NOT NULL,
    `last_name` VARCHAR(50) NOT NULL,
    `email` VARCHAR(100) NOT NULL,
    PRIMARY KEY(`staff_id`)
);


CREATE TABLE `article`
(
    `article_id` INT(11) UNSIGNED AUTO_INCREMENT,
    `title` VARCHAR(255) NOT NULL,
    `snippet` TEXT NOT NULL, #may be able to change to body[split:]+'read more...' etc
    `body` VARCHAR(100) NOT NULL,
    `sort_order` int(11),
    `newsletter_id` int(11)
    PRIMARY KEY(`article_id`)
);


CREATE TABLE `section`
(
    `article_id` INT(11) UNSIGNED AUTO_INCREMENT,
    `title` VARCHAR(255) NOT NULL,
    `company_id` INT(11) DEFAULT 0
    PRIMARY KEY(`section_id`)
);


CREATE TABLE `article_order`
(
    `article_order_id` INT(11) UNSIGNED AUTO_INCREMENT,
    `
);


CREATE TABLE `section_order`
(
    `section_order_id` INT(11) UNSIGNED AUTO_INCREMENT,
    `sort_order` INT(11) NOT NULL default 0,
    `section_id` int(11),
    `newsletter_id` INT(11),
    PRIMARY KEY(`section_order_id`)
;