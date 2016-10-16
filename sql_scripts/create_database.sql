DROP TABLE Invoices;
--DROP TABLE ORDER_DISCOUNTS;

--DROP TABLE Bonus_Service_Prices;
DROP TABLE Orders;

DROP TABLE Bonuses;
DROP TABLE Service_Types;
DROP TABLE Users;
DROP TABLE Roles;
DROP TABLE Discount_Types;
DROP TABLE Offices;
DROP TABLE Clients;


CREATE TABLE Clients(
  ID INTEGER GENERATED AS IDENTITY,
  First_Name VARCHAR2(50) NOT NULL,
  Last_Name VARCHAR2(100) NOT NULL,
  Best_Client NUMBER(1) NOT NULL,
  CONSTRAINT Clients_Primary_Key PRIMARY KEY (ID)
);

CREATE TABLE Roles(
  ID INTEGER GENERATED AS IDENTITY,
  Name VARCHAR2(50) NOT NULL ,
  CONSTRAINT Roles_Primary_Key PRIMARY KEY (ID)
);

CREATE TABLE Users(
  Login VARCHAR2(50) NOT  NULL,
  Password VARCHAR2(50) NOT NULL,
  Client_ID INTEGER NULL,
  Role_ID INTEGER NOT NULL,

  CONSTRAINT Users_Primary_Key PRIMARY KEY (Login),
  FOREIGN KEY (Role_ID) REFERENCES Roles(ID),
  FOREIGN KEY (Client_ID) REFERENCES Clients(ID)
);

CREATE TABLE Offices(
  ID INTEGER GENERATED AS IDENTITY,
  Address VARCHAR2(150) NOT NULL ,
  Info VARCHAR2(500) NOT NULL ,
  CONSTRAINT Offices_Primary_Key PRIMARY KEY (ID)
);


CREATE TABLE Service_Types(
  ID INTEGER GENERATED AS IDENTITY,
  Name VARCHAR2(50) NOT NULL ,
  Base_Cost NUMBER(10,2) NOT NULL ,
  CONSTRAINT Service_Types_Primary_Key PRIMARY KEY (ID)
);

CREATE TABLE Bonuses(
  ID INTEGER GENERATED AS IDENTITY,
  Type VARCHAR2(20) NOT NULL ,
  Value DECIMAL(5,2) NOT NULL ,

  CONSTRAINT Bonuses_Primary_Key PRIMARY KEY (ID)
);

--CREATE TABLE Bonus_Service_Prices(
--  Service_Type_ID INTEGER NOT NULL ,
--  Bonus_ID INTEGER NOT NULL ,
--
--  FOREIGN KEY (Service_Type_ID) REFERENCES Service_Types(ID),
--  FOREIGN KEY (Bonus_ID) REFERENCES Bonuses(ID)
--);




CREATE TABLE Discount_Types(
  ID NUMBER GENERATED AS IDENTITY,
  Description VARCHAR2(150) NOT NULL ,
  Value DECIMAL(5,2) NOT NULL ,

  CONSTRAINT Discount_Types_Primary_Key PRIMARY KEY (ID)
);

CREATE TABLE Orders(
  ID INTEGER GENERATED AS IDENTITY,
  Client_ID INTEGER NOT NULL ,
  Service_Type_ID INTEGER NOT NULL ,
  Service_Bonus_ID Integer NULL,
  
  Office_ID INTEGER NOT NULL,
  Worker_Login VARCHAR2(50) NOT NULL ,

  Amount Number(10,0) NOT NULL,
  Total_Price NUMBER(10,2) NOT NULL ,
  
  Discount_Type_ID Integer NULL,
  
  Acceptance_Date Timestamp NOT NULL,
  Return_Date timestamp NULL ,
  Is_Ready NUMBER(1) NOT NULL ,

  CONSTRAINT Orders_Primary_Key PRIMARY KEY (ID),

  FOREIGN KEY (Client_ID) REFERENCES Clients(ID),
  FOREIGN KEY (Service_Type_ID) REFERENCES Service_Types(ID),
  FOREIGN KEY (Office_ID) REFERENCES Offices(ID),
  FOREIGN KEY (Worker_Login) REFERENCES Users(Login),
  FOREIGN KEY (Discount_Type_ID) REFERENCES Discount_Types(ID),
  FOREIGN KEY (Service_Bonus_ID) REFERENCES BONUSES(ID)
);


--CREATE TABLE Order_Discounts(
--  Order_ID INTEGER NOT NULL ,
--  Discount_Type_ID INTEGER NOT NULL ,
--
--  FOREIGN KEY (Discount_Type_ID) REFERENCES Discount_Types(Id),
--  FOREIGN KEY (Order_ID) REFERENCES Orders(ID)
--);


CREATE TABLE Invoices(
  ID INTEGER GENERATED AS IDENTITY,
  Order_ID INTEGER NOT NULL ,
  Time timestamp NOT NULL,

  CONSTRAINT  Invoices_Primary_Key PRIMARY KEY (ID),
  FOREIGN KEY (Order_ID) REFERENCES Orders(ID)
);
