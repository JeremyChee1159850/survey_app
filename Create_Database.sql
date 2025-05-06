-- CREATE SCHEMA IF NOT EXISTS `project693` DEFAULT CHARACTER SET utf8 ;
-- USE `project693` ;

SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS `competition_themes`;
CREATE TABLE `competition_themes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `description` varchar(255) NOT NULL,  
  `application_id` int NOT NULL,
  `donation_status` enum('enabled','disabled') NOT NULL,    
  `donation_app_id` int DEFAULT NULL,
  PRIMARY KEY (`id`)
) ;

DROP TABLE IF EXISTS `theme_applications`;
CREATE TABLE `theme_applications` (
  `id` int NOT NULL AUTO_INCREMENT,
  `theme_name` varchar(50) NOT NULL,
  `theme_description` varchar(255) NOT NULL,
  `applicant_id` int NOT NULL,
  `applicant` varchar(20) NOT NULL,
  `applying_time` timestamp NOT NULL,  
  `status` enum('pending','approved','rejected') NOT NULL,  
  `rejection_reason` varchar(255) DEFAULT NULL,
  `operator_id` int DEFAULT NULL,
  `operator` varchar(20) DEFAULT NULL,
  `operation_time` timestamp DEFAULT NULL,
  PRIMARY KEY (`id`)
) ;

DROP TABLE IF EXISTS `user_theme_role`;
CREATE TABLE `user_theme_role` (
  `id` int NOT NULL AUTO_INCREMENT,
  `theme_id` int NOT NULL,
  `user_id` int NOT NULL,
  `role` enum('scrutineer','admin') NOT NULL,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`),
  FOREIGN KEY (`theme_id`) REFERENCES `competition_themes`(`id`)
);

DROP TABLE IF EXISTS `user_community_role`;
CREATE TABLE `user_community_role` (
  `id` int NOT NULL AUTO_INCREMENT,
  `theme_id` int NOT NULL,
  `user_id` int NOT NULL,
  `role` enum('moderator') NOT NULL,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`),
  FOREIGN KEY (`theme_id`) REFERENCES `competition_themes`(`id`)
);

DROP TABLE IF EXISTS `competitions`;
CREATE TABLE `competitions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `voting_start_date` date NOT NULL,
  `voting_end_date` date NOT NULL,
  `status` enum('pending','ongoing','ended','published') NOT NULL,
  `theme_id` int NOT NULL,
  `theme_name` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ;

DROP TABLE IF EXISTS `competitors`;
CREATE TABLE `competitors` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `description` varchar(255) NOT NULL,
  `image` varchar(64) NOT NULL,
  `location` json DEFAULT NULL,
  `invasiveness` enum('invasive', 'non-invasive') NOT NULL DEFAULT 'non-invasive',
  PRIMARY KEY (`id`)
) ;

DROP TABLE IF EXISTS `survey_results`;
CREATE TABLE `survey_results` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT DEFAULT NULL,               -- NULL if anonymous user
  `question_number` INT NOT NULL,           -- 1 to 10
  `selected_competitor_id` INT NOT NULL,    -- which plant they chose
  `reasoning` VARCHAR(50) DEFAULT NULL,     -- only filled on final question (Q10)
  `submission_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- auto logs each click time
);

DROP TABLE IF EXISTS `competition_competitors`;
CREATE TABLE `competition_competitors` (
  `id` int NOT NULL AUTO_INCREMENT,
  `competition_id` int NOT NULL,
  `competitor_id` int NOT NULL,
  `vote_count` int DEFAULT NULL,
  `vote_ratio` DECIMAL(4,3) DEFAULT NULL,
  `is_winner` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `competition_competitors_competitions` (`competition_id`),
  CONSTRAINT `competition_competitors_competitions` FOREIGN KEY (`competition_id`) REFERENCES `competitions` (`id`)
);

DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(20) NOT NULL,
  `password_hash` varchar(64) NOT NULL,
  `email` varchar(255) NOT NULL,
  `first_name` varchar(50) DEFAULT NULL,
  `last_name` varchar(50) DEFAULT NULL,
  `location` json DEFAULT NULL,
  `description` varchar(255) DEFAULT NULL,
  `avatar` varchar(64) NOT NULL,
  `role` enum('voter','siteadmin') NOT NULL,
  `status` enum('active','inactive') NOT NULL,
  `voting_permission` enum('allowed','banned') NOT NULL,
  `appeal_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username_UK` (`username`),
  UNIQUE KEY `email_UK` (`email`)
);

DROP TABLE IF EXISTS `votes`;
CREATE TABLE `votes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `competition_competitor_id` int NOT NULL,
  `voter_id` int NOT NULL,
  `voting_time` timestamp NOT NULL,
  `voting_ip` varchar(50) NOT NULL,
  `status` enum('valid','invalid') NOT NULL,
  PRIMARY KEY (`id`),
  KEY `votes_users` (`voter_id`),
  CONSTRAINT `votes_users` FOREIGN KEY (`voter_id`) REFERENCES `users` (`id`)
);


DROP TABLE IF EXISTS `ban_appeals`;
CREATE TABLE `ban_appeals` (
  `id` int NOT NULL AUTO_INCREMENT,
  `ban_scope` enum('theme','sitewide') NOT NULL,    
  `theme_id` int DEFAULT NULL,
  `appealer_id` int NOT NULL,
  `appealer` varchar(20) NOT NULL,
  `appeal_reason` varchar(255) NOT NULL,  
  `appeal_time` timestamp NOT NULL,  
  `status` enum('pending','upheld','revoked') NOT NULL,  
  `upholding_reason` varchar(255) DEFAULT NULL,
  `operator_id` int DEFAULT NULL,
  `operator` varchar(20) DEFAULT NULL,
  `operation_time` timestamp DEFAULT NULL,
  PRIMARY KEY (`id`)
) ;

DROP TABLE IF EXISTS `banned_voters`;
CREATE TABLE `banned_voters` (
  `id` int NOT NULL AUTO_INCREMENT,
  `theme_id` int NOT NULL,
  `user_id` int NOT NULL,
  `appeal_id` int DEFAULT NULL,
  PRIMARY KEY (`id`)
) ;

DROP TABLE IF EXISTS `messages`;
CREATE TABLE `messages` (
  `message_id` INT NOT NULL AUTO_INCREMENT,
  `user_id` INT NOT NULL,
  `title` VARCHAR(255) NOT NULL,
  `content` TEXT NOT NULL,
  `created_at` TIMESTAMP NOT NULL,
  `theme_id` int NOT NULL,
  PRIMARY KEY (`message_id`)
) ;

DROP TABLE IF EXISTS `replies`;
CREATE TABLE `replies` (
  `reply_id` INT NOT NULL AUTO_INCREMENT,
  `message_id` INT NOT NULL,
  `user_id` INT NOT NULL,
  `content` TEXT NOT NULL,
  `created_at` TIMESTAMP NOT NULL,
  PRIMARY KEY (`reply_id`)
) ;  

DROP TABLE IF EXISTS `conversations`;
CREATE TABLE `conversations` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `user_id_1` INT NOT NULL,
  `user_id_2` INT NOT NULL,
  `created_at` TIMESTAMP NOT NULL,
  `latest_message_time` TIMESTAMP NOT NULL,  
  PRIMARY KEY (`id`)
) ;

DROP TABLE IF EXISTS `conversation_messages`;
CREATE TABLE `conversation_messages` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `conversation_id` INT NOT NULL,
  `sender_id` INT NOT NULL,
  `content` TEXT NOT NULL,
  `created_at` TIMESTAMP NOT NULL,
  `is_read` BOOLEAN NOT NULL,
  PRIMARY KEY (`id`)
) ;  

DROP TABLE IF EXISTS `user_privacy_settings`;
CREATE TABLE `user_privacy_settings` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `user_id` INT NOT NULL,
  `show_email` BOOLEAN NOT NULL,
  `show_first_name` BOOLEAN NOT NULL,
  `show_last_name` BOOLEAN NOT NULL,
  `show_location` BOOLEAN NOT NULL,
  `show_description` BOOLEAN NOT NULL,
  `show_avatar` BOOLEAN NOT NULL,
  `show_recent_post` BOOLEAN NOT NULL,
  `show_recent_vote` BOOLEAN NOT NULL,
  `show_recent_donation` BOOLEAN NOT NULL,
  `show_in_user_list` BOOLEAN NOT NULL,  
  PRIMARY KEY (`id`)
) ;  

DROP TABLE IF EXISTS `donation_applications`;
CREATE TABLE `donation_applications` (
  `id` int NOT NULL AUTO_INCREMENT,
  `theme_id` int NOT NULL,
  `theme_name` varchar(50) NOT NULL,
  `charity_name` varchar(255) NOT NULL,
  `registration_number` varchar(50) NOT NULL,
  `bank_account` varchar(50) NOT NULL,
  `nz_ird_number` varchar(50) NOT NULL,
  `stamp_file_path` varchar(64) NOT NULL,
  `rep_first_name` varchar(50) NOT NULL,
  `rep_last_name` varchar(50) NOT NULL,
  `rep_designation` varchar(50) NOT NULL,
  `rep_signature_file_path` varchar(64) NOT NULL,
  `applicant_id` int NOT NULL,
  `applicant` varchar(20) NOT NULL,
  `applying_time` timestamp NOT NULL,  
  `status` enum('pending','approved','rejected') NOT NULL,  
  `rejection_reason` varchar(255) DEFAULT NULL,
  `operator_id` int DEFAULT NULL,
  `operator` varchar(20) DEFAULT NULL,
  `operation_time` timestamp DEFAULT NULL,
  PRIMARY KEY (`id`)
) ;

DROP TABLE IF EXISTS `donation_record`;
CREATE TABLE `donation_record` (
  `id` int NOT NULL AUTO_INCREMENT,
  `theme_id` int NOT NULL,
  `donation_app_id` int NOT NULL,
  `donor_user_id` int NOT NULL,
  `donation_amount` int NOT NULL,  
  `donation_date` date NOT NULL,  
  `credit_card` varchar(50) NOT NULL,
  `expiry_date` varchar(7) NOT NULL,
  `cvv` char(3) NOT NULL,
  `receipt_number` varchar(20) NOT NULL,
  `receipt_file_path` varchar(150) NOT NULL,
  `receipt_generation_status` enum('pending','generated','sent') NOT NULL,  
  PRIMARY KEY (`id`)
) ;

SET FOREIGN_KEY_CHECKS = 1;