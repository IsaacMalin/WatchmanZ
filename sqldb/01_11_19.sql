-- MySQL dump 10.16  Distrib 10.1.38-MariaDB, for debian-linux-gnueabihf (armv7l)
--
-- Host: localhost    Database: watchman
-- ------------------------------------------------------
-- Server version	10.1.38-MariaDB-0+deb9u1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `registeredIPCameras`
--

DROP TABLE IF EXISTS `registeredIPCameras`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `registeredIPCameras` (
  `IP` varchar(20) NOT NULL,
  `camName` varchar(100) NOT NULL,
  `active` tinyint(1) DEFAULT NULL,
  `lastSeen` datetime DEFAULT NULL,
  `regDate` datetime DEFAULT NULL,
  `camType` varchar(10) DEFAULT NULL,
  `batt` varchar(4) DEFAULT NULL,
  `deviceType` varchar(2) NOT NULL DEFAULT 'C',
  PRIMARY KEY (`IP`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `registeredNRFSensors`
--

DROP TABLE IF EXISTS `registeredNRFSensors`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `registeredNRFSensors` (
  `nodeID` smallint(5) unsigned NOT NULL,
  `sensorName` varchar(100) NOT NULL,
  `localID` varchar(10) NOT NULL,
  `globalID` mediumint(8) unsigned NOT NULL,
  `active` tinyint(1) DEFAULT NULL,
  `lastSeen` datetime DEFAULT NULL,
  `regDate` datetime DEFAULT NULL,
  `camType` varchar(10) DEFAULT NULL,
  `camIP` varchar(20) DEFAULT NULL,
  `iOrv` varchar(2) NOT NULL DEFAULT 'i',
  `vidLength` smallint(5) unsigned NOT NULL DEFAULT '5',
  `sendAlert` tinyint(1) NOT NULL DEFAULT '0',
  `sendSms` tinyint(1) NOT NULL DEFAULT '0',
  `useCam` tinyint(1) NOT NULL DEFAULT '0',
  `batt` varchar(4) DEFAULT NULL,
  PRIMARY KEY (`nodeID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `registeredWifiSensors`
--

DROP TABLE IF EXISTS `registeredWifiSensors`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `registeredWifiSensors` (
  `IP` varchar(20) NOT NULL,
  `sensorName` varchar(100) NOT NULL,
  `active` tinyint(1) DEFAULT NULL,
  `lastSeen` datetime DEFAULT NULL,
  `regDate` datetime DEFAULT NULL,
  `camType` varchar(10) DEFAULT NULL,
  `camIP` varchar(20) DEFAULT NULL,
  `iOrv` varchar(2) NOT NULL DEFAULT 'i',
  `vidLength` smallint(5) unsigned NOT NULL DEFAULT '5',
  `sendAlert` tinyint(1) NOT NULL DEFAULT '0',
  `sendSms` tinyint(1) NOT NULL DEFAULT '0',
  `useCam` tinyint(1) NOT NULL DEFAULT '0',
  `batt` varchar(4) DEFAULT NULL,
  `deviceType` varchar(2) NOT NULL DEFAULT 'S',
  PRIMARY KEY (`IP`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sensorAlertMsgs`
--

DROP TABLE IF EXISTS `sensorAlertMsgs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sensorAlertMsgs` (
  `deviceCode` varchar(10) NOT NULL,
  `openStateMsg` varchar(80) DEFAULT NULL,
  `closedStateMsg` varchar(80) DEFAULT NULL,
  PRIMARY KEY (`deviceCode`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2019-11-01 16:25:16
