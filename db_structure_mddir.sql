-- MySQL dump 10.13  Distrib 5.7.21, for Linux (x86_64)
--
-- Host: localhost    Database: md_directory
-- ------------------------------------------------------
-- Server version	5.7.21

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Current Database: `md_directory`
--

/*!40000 DROP DATABASE IF EXISTS `md_directory`*/;

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `md_directory` /*!40100 DEFAULT CHARACTER SET latin1 */;

USE `md_directory`;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(80) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_group_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `group_id` (`group_id`,`permission_id`),
  KEY `auth_group_permissions_425ae3c4` (`group_id`),
  KEY `auth_group_permissions_1e014c8f` (`permission_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `auth_message`
--

DROP TABLE IF EXISTS `auth_message`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_message` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `message` longtext NOT NULL,
  PRIMARY KEY (`id`),
  KEY `auth_message_403f60f` (`user_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `content_type_id` (`content_type_id`,`codename`),
  KEY `auth_permission_1bb8f392` (`content_type_id`)
) ENGINE=MyISAM AUTO_INCREMENT=184 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `auth_user`
--

DROP TABLE IF EXISTS `auth_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(30) NOT NULL,
  `first_name` varchar(30) NOT NULL,
  `last_name` varchar(30) NOT NULL,
  `email` varchar(75) NOT NULL,
  `password` varchar(128) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `last_login` datetime NOT NULL,
  `date_joined` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=MyISAM AUTO_INCREMENT=1205 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `auth_user_groups`
--

DROP TABLE IF EXISTS `auth_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user_groups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`,`group_id`),
  KEY `auth_user_groups_403f60f` (`user_id`),
  KEY `auth_user_groups_425ae3c4` (`group_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `auth_user_user_permissions`
--

DROP TABLE IF EXISTS `auth_user_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user_user_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`,`permission_id`),
  KEY `auth_user_user_permissions_403f60f` (`user_id`),
  KEY `auth_user_user_permissions_1e014c8f` (`permission_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `action_time` datetime NOT NULL,
  `user_id` int(11) NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_403f60f` (`user_id`),
  KEY `django_admin_log_1bb8f392` (`content_type_id`)
) ENGINE=MyISAM AUTO_INCREMENT=6 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `app_label` (`app_label`,`model`)
) ENGINE=MyISAM AUTO_INCREMENT=62 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime NOT NULL,
  PRIMARY KEY (`session_key`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `django_site`
--

DROP TABLE IF EXISTS `django_site`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_site` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `domain` varchar(100) NOT NULL,
  `name` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `md_directory_brightsightoffice`
--

DROP TABLE IF EXISTS `md_directory_brightsightoffice`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `md_directory_brightsightoffice` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `struct_id` int(11) NOT NULL,
  `add1` varchar(200) NOT NULL,
  `add2` varchar(200) NOT NULL,
  `add3` varchar(200) NOT NULL,
  `add4` varchar(200) NOT NULL,
  `add5` varchar(200) NOT NULL,
  `po_code` varchar(20) NOT NULL,
  `postal1` varchar(200) NOT NULL,
  `postal2` varchar(200) NOT NULL,
  `postal3` varchar(200) NOT NULL,
  `postal4` varchar(200) NOT NULL,
  `postal5` varchar(200) NOT NULL,
  `tel` varchar(35) NOT NULL,
  `fax` varchar(50) NOT NULL,
  `email` varchar(75) NOT NULL,
  `contact_person` varchar(200) NOT NULL,
  `website` varchar(200) NOT NULL,
  `manager_email` varchar(200) DEFAULT NULL,
  `manager` varchar(200) DEFAULT NULL,
  `manager_cell_ph` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `md_directory_brightsightoffice_408cafa9` (`struct_id`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `md_directory_club`
--

DROP TABLE IF EXISTS `md_directory_club`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `md_directory_club` (
  `id` int(11) NOT NULL,
  `parent_id` int(11) DEFAULT NULL,
  `struct_id` int(11) NOT NULL,
  `prev_struct_id` int(11) DEFAULT NULL,
  `name` varchar(100) NOT NULL,
  `type` int(11) NOT NULL,
  `meet_time` varchar(200) NOT NULL,
  `add1` varchar(200) NOT NULL,
  `add2` varchar(200) NOT NULL,
  `add3` varchar(200) NOT NULL,
  `add4` varchar(200) NOT NULL,
  `add5` varchar(200) NOT NULL,
  `po_code` varchar(20) NOT NULL,
  `postal1` varchar(200) NOT NULL,
  `postal2` varchar(200) NOT NULL,
  `postal3` varchar(200) NOT NULL,
  `postal4` varchar(200) NOT NULL,
  `postal5` varchar(200) NOT NULL,
  `charter_year` int(11) DEFAULT NULL,
  `website` varchar(200) NOT NULL,
  `suspended_b` tinyint(1) NOT NULL,
  `zone_id` int(11) NOT NULL,
  `closed_b` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `mddir_club_63f17a16` (`parent_id`),
  KEY `mddir_club_408cafa9` (`struct_id`),
  KEY `mddir_club_2957a812` (`zone_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `md_directory_clubmerge`
--

DROP TABLE IF EXISTS `md_directory_clubmerge`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `md_directory_clubmerge` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `club_id` int(11) NOT NULL,
  `new_struct_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `club_id` (`club_id`),
  UNIQUE KEY `club_id_2` (`club_id`,`new_struct_id`)
) ENGINE=InnoDB AUTO_INCREMENT=350 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `md_directory_clubofficer`
--

DROP TABLE IF EXISTS `md_directory_clubofficer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `md_directory_clubofficer` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `club_id` int(11) NOT NULL,
  `year` int(11) NOT NULL,
  `member_id` int(11) DEFAULT NULL,
  `email` varchar(200) NOT NULL,
  `add1` varchar(200) NOT NULL,
  `add2` varchar(200) NOT NULL,
  `add3` varchar(200) NOT NULL,
  `add4` varchar(200) NOT NULL,
  `po_code` varchar(20) NOT NULL,
  `office_id` int(11) NOT NULL,
  `phone` varchar(25) NOT NULL,
  `fax` varchar(25) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `mddir_clubofficer_1985cacc` (`club_id`),
  KEY `mddir_clubofficer_56e38b98` (`member_id`),
  KEY `mddir_clubofficer_43edbc56` (`office_id`)
) ENGINE=MyISAM AUTO_INCREMENT=12362 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `md_directory_clubofficer_email`
--

DROP TABLE IF EXISTS `md_directory_clubofficer_email`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `md_directory_clubofficer_email` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `club_id` int(11) NOT NULL,
  `email` varchar(200) NOT NULL,
  `office_id` smallint(6) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `club_id` (`club_id`)
) ENGINE=InnoDB AUTO_INCREMENT=28 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `md_directory_clubofficer_temp`
--

DROP TABLE IF EXISTS `md_directory_clubofficer_temp`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `md_directory_clubofficer_temp` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `club_id` int(11) NOT NULL,
  `year` int(11) NOT NULL,
  `member_id` int(11) DEFAULT NULL,
  `email` varchar(200) NOT NULL,
  `add1` varchar(200) NOT NULL,
  `add2` varchar(200) NOT NULL,
  `add3` varchar(200) NOT NULL,
  `add4` varchar(200) NOT NULL,
  `po_code` varchar(20) NOT NULL,
  `office_id` int(11) NOT NULL,
  `phone` varchar(25) NOT NULL,
  `fax` varchar(25) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `mddir_clubofficer_1985cacc` (`club_id`) USING BTREE,
  KEY `mddir_clubofficer_43edbc56` (`office_id`) USING BTREE,
  KEY `mddir_clubofficer_56e38b98` (`member_id`) USING BTREE
) ENGINE=MyISAM AUTO_INCREMENT=5620 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `md_directory_clubtype`
--

DROP TABLE IF EXISTS `md_directory_clubtype`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `md_directory_clubtype` (
  `id` int(11) NOT NULL,
  `type` varchar(40) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `md_directory_clubzone`
--

DROP TABLE IF EXISTS `md_directory_clubzone`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `md_directory_clubzone` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `year` mediumint(9) NOT NULL,
  `club_id` int(11) NOT NULL,
  `zone_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `club_id_2` (`club_id`,`zone_id`,`year`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=829 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `md_directory_districtoffice`
--

DROP TABLE IF EXISTS `md_directory_districtoffice`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `md_directory_districtoffice` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `struct_id` int(11) NOT NULL,
  `add1` varchar(200) NOT NULL,
  `add2` varchar(200) NOT NULL,
  `add3` varchar(200) NOT NULL,
  `add4` varchar(200) NOT NULL,
  `add5` varchar(200) NOT NULL,
  `po_code` varchar(20) NOT NULL,
  `postal1` varchar(200) NOT NULL,
  `postal2` varchar(200) NOT NULL,
  `postal3` varchar(200) NOT NULL,
  `postal4` varchar(200) NOT NULL,
  `postal5` varchar(200) NOT NULL,
  `tel` varchar(35) NOT NULL,
  `fax` varchar(50) NOT NULL,
  `email` varchar(75) NOT NULL,
  `contact_person` varchar(200) NOT NULL,
  `website` varchar(200) NOT NULL,
  `hours` varchar(200) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `mddir_districtoffice_408cafa9` (`struct_id`)
) ENGINE=MyISAM AUTO_INCREMENT=3 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `md_directory_eventattendance`
--

DROP TABLE IF EXISTS `md_directory_eventattendance`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `md_directory_eventattendance` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `event` varchar(200) NOT NULL,
  `member_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `md_directory_eventattendance_56e38b98` (`member_id`)
) ENGINE=MyISAM AUTO_INCREMENT=272 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `md_directory_meetings`
--

DROP TABLE IF EXISTS `md_directory_meetings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `md_directory_meetings` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `club_id` int(11) NOT NULL,
  `day` int(11) NOT NULL,
  `week` int(11) NOT NULL,
  `time` time NOT NULL,
  `spec_ins` varchar(200) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `mddir_meetings_1985cacc` (`club_id`)
) ENGINE=MyISAM AUTO_INCREMENT=196 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `md_directory_member`
--

DROP TABLE IF EXISTS `md_directory_member`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `md_directory_member` (
  `id` int(11) NOT NULL,
  `first_name` varchar(100) NOT NULL,
  `last_name` varchar(100) NOT NULL,
  `deceased_b` tinyint(1) NOT NULL,
  `resigned_b` tinyint(1) NOT NULL,
  `partner` varchar(100) NOT NULL,
  `partner_lion_b` tinyint(1) NOT NULL,
  `join_date` int(11) DEFAULT NULL,
  `home_ph` varchar(50) NOT NULL,
  `bus_ph` varchar(50) NOT NULL,
  `fax` varchar(50) NOT NULL,
  `cell_ph` varchar(50) NOT NULL,
  `email` varchar(75) NOT NULL,
  `club_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `mddir_member_1985cacc` (`club_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `md_directory_mentor`
--

DROP TABLE IF EXISTS `md_directory_mentor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `md_directory_mentor` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `struct_id` int(11) NOT NULL,
  `year` int(11) NOT NULL,
  `member_id` int(11) DEFAULT NULL,
  `email` varchar(75) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `md_directory_mentor_408cafa9` (`struct_id`),
  KEY `md_directory_mentor_56e38b98` (`member_id`)
) ENGINE=MyISAM AUTO_INCREMENT=10 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `md_directory_merchcentre`
--

DROP TABLE IF EXISTS `md_directory_merchcentre`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `md_directory_merchcentre` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `struct_id` int(11) NOT NULL,
  `add1` varchar(200) NOT NULL,
  `add2` varchar(200) NOT NULL,
  `add3` varchar(200) NOT NULL,
  `add4` varchar(200) NOT NULL,
  `add5` varchar(200) NOT NULL,
  `po_code` varchar(20) NOT NULL,
  `tel` varchar(35) NOT NULL,
  `fax` varchar(50) NOT NULL,
  `email` varchar(75) NOT NULL,
  `manager_id` int(11) DEFAULT NULL,
  `fin_advisor_id` int(11) DEFAULT NULL,
  `contact_person` varchar(200) NOT NULL,
  `website` varchar(200) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `mddir_merchcentre_408cafa9` (`struct_id`),
  KEY `mddir_merchcentre_501a2222` (`manager_id`),
  KEY `mddir_merchcentre_6600a14d` (`fin_advisor_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `md_directory_merlcoordinators`
--

DROP TABLE IF EXISTS `md_directory_merlcoordinators`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `md_directory_merlcoordinators` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `struct_id` int(11) NOT NULL,
  `year` int(11) NOT NULL,
  `member_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `mddir_merlcoordinators_408cafa9` (`struct_id`),
  KEY `mddir_merlcoordinators_56e38b98` (`member_id`)
) ENGINE=MyISAM AUTO_INCREMENT=4 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `md_directory_officertitle`
--

DROP TABLE IF EXISTS `md_directory_officertitle`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `md_directory_officertitle` (
  `id` int(11) NOT NULL,
  `title` varchar(100) NOT NULL,
  `ip_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `mddir_officertitle_352b58db` (`ip_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `md_directory_profile`
--

DROP TABLE IF EXISTS `md_directory_profile`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `md_directory_profile` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `is_club` tinyint(1) NOT NULL,
  `club_id` int(11) DEFAULT NULL,
  `is_dist` tinyint(1) NOT NULL,
  `struct_id` int(11) DEFAULT NULL,
  `is_md` tinyint(1) NOT NULL,
  `all_access` tinyint(1) NOT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `rel_id` (`user_id`),
  KEY `mddir_profile_1985cacc` (`club_id`),
  KEY `mddir_profile_408cafa9` (`struct_id`)
) ENGINE=MyISAM AUTO_INCREMENT=1196 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `md_directory_region`
--

DROP TABLE IF EXISTS `md_directory_region`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `md_directory_region` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `struct_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `mddir_region_408cafa9` (`struct_id`)
) ENGINE=MyISAM AUTO_INCREMENT=12 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `md_directory_regionchair`
--

DROP TABLE IF EXISTS `md_directory_regionchair`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `md_directory_regionchair` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `parent_id` int(11) NOT NULL,
  `member_id` int(11) DEFAULT NULL,
  `year` int(11) NOT NULL,
  `email` varchar(75) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `mddir_regionchair_9574fce` (`parent_id`),
  KEY `mddir_regionchair_56e38b98` (`member_id`)
) ENGINE=MyISAM AUTO_INCREMENT=62 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `md_directory_struct`
--

DROP TABLE IF EXISTS `md_directory_struct`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `md_directory_struct` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `website` varchar(200) NOT NULL,
  `type_id` int(11) DEFAULT NULL,
  `parent_id` int(11) DEFAULT NULL,
  `in_use_b` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`id`),
  KEY `md_directory_struct_777d41c8` (`type_id`),
  KEY `md_directory_struct_63f17a16` (`parent_id`)
) ENGINE=MyISAM AUTO_INCREMENT=13 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `md_directory_structchair`
--

DROP TABLE IF EXISTS `md_directory_structchair`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `md_directory_structchair` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `struct_id` int(11) NOT NULL,
  `year` int(11) NOT NULL,
  `member_id` int(11) DEFAULT NULL,
  `email` varchar(75) NOT NULL,
  `office` varchar(150) NOT NULL,
  `committee_members` varchar(200) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `mddir_structchair_408cafa9` (`struct_id`),
  KEY `mddir_structchair_56e38b98` (`member_id`)
) ENGINE=MyISAM AUTO_INCREMENT=1134 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `md_directory_structmerge`
--

DROP TABLE IF EXISTS `md_directory_structmerge`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `md_directory_structmerge` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `previous_struct_id` smallint(6) NOT NULL,
  `current_struct_id` smallint(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `md_directory_structofficer`
--

DROP TABLE IF EXISTS `md_directory_structofficer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `md_directory_structofficer` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `struct_id` int(11) NOT NULL,
  `year` int(11) NOT NULL,
  `member_id` int(11) DEFAULT NULL,
  `end_month` int(11) NOT NULL,
  `email` varchar(75) NOT NULL,
  `office_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `mddir_structofficer_408cafa9` (`struct_id`),
  KEY `mddir_structofficer_56e38b98` (`member_id`),
  KEY `mddir_structofficer_43edbc56` (`office_id`)
) ENGINE=MyISAM AUTO_INCREMENT=543 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `md_directory_structtype`
--

DROP TABLE IF EXISTS `md_directory_structtype`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `md_directory_structtype` (
  `id` int(11) NOT NULL,
  `type` varchar(40) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `md_directory_zone`
--

DROP TABLE IF EXISTS `md_directory_zone`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `md_directory_zone` (
  `id` int(11) NOT NULL,
  `in_region_b` tinyint(1) NOT NULL,
  `region_id` int(11) DEFAULT NULL,
  `name` varchar(100) NOT NULL,
  `struct_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `mddir_zone_9574fce` (`region_id`),
  KEY `mddir_zone_408cafa9` (`struct_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `md_directory_zonechair`
--

DROP TABLE IF EXISTS `md_directory_zonechair`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `md_directory_zonechair` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `parent_id` int(11) NOT NULL,
  `member_id` int(11) DEFAULT NULL,
  `year` int(11) NOT NULL,
  `email` varchar(75) NOT NULL,
  `assistant_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `mddir_zonechair_2957a812` (`parent_id`),
  KEY `mddir_zonechair_56e38b98` (`member_id`),
  KEY `md_directory_zonechair_dc37fb91` (`assistant_id`)
) ENGINE=MyISAM AUTO_INCREMENT=349 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `south_migrationhistory`
--

DROP TABLE IF EXISTS `south_migrationhistory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `south_migrationhistory` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app_name` varchar(255) NOT NULL,
  `migration` varchar(255) NOT NULL,
  `applied` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=23 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2021-07-06  7:20:38
