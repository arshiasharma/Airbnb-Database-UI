from flask import Flask, render_template, request, redirect, url_for, session
from flask.helpers import flash
from flaskext.mysql import MySQL
import mysql.connector
import csv
import atexit
import random

app = Flask(__name__)


# creating a connection to the mysql database --- MAY HAVE TO CHANGE THE PASSWORD FOR TESTING/GRADING
connection = mysql.connector.connect(host="localhost",
                                     user="root",
                                     password="Arsh&*121sq(l",
                                     auth_plugin="mysql_native_password")

cursor = connection.cursor()

cursor.execute("DROP database IF EXISTS airbnb;")

# creating the new airbnb database
mydb = "CREATE database airbnb;"
cursor.execute(mydb)

query = "use airbnb;"
cursor.execute(query)

# Creating the 11 tables for the database

# Neighbourhood table
query = '''CREATE TABLE Neighbourhood(
                Neighbourhood_Id INTEGER PRIMARY KEY AUTO_INCREMENT,
                Neighbourhood_Name VARCHAR(75) UNIQUE NOT NULL
);  '''

cursor.execute(query)

# Room Type table
query = '''CREATE TABLE RoomType(
                RoomType_Id INTEGER NOT NULL PRIMARY KEY AUTO_INCREMENT,
                RoomType_Name VARCHAR(50) UNIQUE
);  '''

cursor.execute(query)

# Bed Type table
query = '''CREATE TABLE BedType(
                BedType_Id INTEGER NOT NULL PRIMARY KEY AUTO_INCREMENT,
                BedType_Name VARCHAR(50) UNIQUE
);  '''

cursor.execute(query)

# Cancellation table
query = '''CREATE TABLE Cancellation(
                Cancellation_Id INTEGER NOT NULL PRIMARY KEY AUTO_INCREMENT,
                CancellationType VARCHAR(50) UNIQUE
);  '''

cursor.execute(query)

# Reviewer table
query = '''CREATE TABLE Reviewer(
                Reviewer_Id INTEGER NOT NULL,
                Reviewer_Name VARCHAR(50),
                PRIMARY KEY(Reviewer_Id)
    );  '''

cursor.execute(query)

# Location table
query = '''CREATE TABLE Location(
                Location_Id INTEGER NOT NULL PRIMARY KEY AUTO_INCREMENT,
                Street VARCHAR(250) UNIQUE,
                Neighbourhood_Id INTEGER,
                FOREIGN KEY (Neighbourhood_Id) REFERENCES Neighbourhood(Neighbourhood_Id)
                ON DELETE CASCADE
                ON UPDATE CASCADE
);  '''

cursor.execute(query)

# Room table
query = '''CREATE TABLE Room(
                Room_Id INTEGER NOT NULL PRIMARY KEY AUTO_INCREMENT,
                RoomType_ID INTEGER,
                Accomadations INTEGER,
                Bathrooms INTEGER,
                Bedrooms INTEGER,
                Beds INTEGER,
                BedType_Id INTEGER,
                isDeleted VARCHAR(1),
                FOREIGN KEY (RoomType_ID) REFERENCES RoomType(RoomType_ID)
                    ON DELETE CASCADE
                    ON UPDATE CASCADE,
                FOREIGN KEY (BedType_Id) REFERENCES BedType(BedType_ID)
                    ON DELETE CASCADE
                    ON UPDATE CASCADE
);  '''

cursor.execute(query)

# Host table
query = '''CREATE TABLE Host(
                Host_Id INTEGER NOT NULL PRIMARY KEY,
                Host_Name VARCHAR(50),
                Host_Since Date,
                Host_About VARCHAR(500),
                Host_Response VARCHAR(50),
                Host_Acceptance_Rate VARCHAR(5),
                Superhost VARCHAR(5),
                Host_Neighbourhood INTEGER,
                Host_Listing_Count INTEGER,
                Host_Identity_Verified VARCHAR(200),
                isDeleted VARCHAR(1),
                FOREIGN KEY (Host_Neighbourhood) REFERENCES Neighbourhood(Neighbourhood_ID)
                    ON DELETE CASCADE
                    ON UPDATE CASCADE
);  '''

cursor.execute(query)

# Listing table 
query = '''CREATE TABLE Listing(
                Listing_Id INTEGER NOT NULL PRIMARY KEY,
                URL VARCHAR(50),
                Name VARCHAR(50),
                Summary VARCHAR(1000),
                Notes VARCHAR(1000),
                Transit VARCHAR(1000),
                Host_Id INTEGER,
                Location_Id INTEGER, 
                Room_Id INTEGER,
                Price DECIMAL(10,2),
                Cancellation_Policy INTEGER,
                FOREIGN KEY (Host_Id) REFERENCES Host(Host_Id),
                FOREIGN KEY (Location_Id) REFERENCES Location(Location_Id),
                FOREIGN KEY (Room_Id) REFERENCES Room(Room_Id),
                isDeleted VARCHAR(1),
                FOREIGN KEY (Cancellation_Policy) REFERENCES Cancellation(Cancellation_Id)
                    ON DELETE CASCADE
                    ON UPDATE CASCADE
);  '''

cursor.execute(query)

# Review table
query = '''CREATE TABLE Review(
                Review_Id INTEGER NOT NULL PRIMARY KEY,
                Listing_Id INTEGER,
                Date DATE,
                Reviewer_Id INTEGER NOT NULL,
                Comments VARCHAR(5000),
                isDeleted VARCHAR(1),
                FOREIGN KEY (Listing_ID) REFERENCES Listing(Listing_Id)
                    ON DELETE CASCADE
                    ON UPDATE CASCADE,
                FOREIGN KEY (Reviewer_Id) REFERENCES Reviewer(Reviewer_Id) 
                    ON DELETE CASCADE
                    ON UPDATE CASCADE
    );  '''

cursor.execute(query)

# Creating the Database Indexes for the tables that have more than 3 attributes

query = '''CREATE INDEX Host_Name ON Host(Host_Name);'''
cursor.execute(query)

query = '''CREATE INDEX Beds ON Room(Beds);'''
cursor.execute(query)

query = '''CREATE INDEX Name ON Listing(Name);'''
cursor.execute(query)

query = '''CREATE INDEX Reviewer_Id ON Review(Reviewer_Id);'''
cursor.execute(query)

# importing the data into the tables - Reviewer
with open("excel/reviews.csv") as csv_file:
    csv_data = csv.reader(csv_file, delimiter=',')
    count = 0

    for row in csv_data:
        if count == 0:
            count = 1
            continue

        else:
            # adding to the reviewer table
            records = tuple(row[3:5])
            query = "INSERT IGNORE INTO Reviewer(Reviewer_Id, Reviewer_Name) VALUES(%s,%s);"
            cursor.execute(query, records)
connection.commit()

# importing the data into the rest of the tables
with open("excel/listings.csv") as csv_file:
    csv_data = csv.reader(csv_file, delimiter=',')
    count = 0
    tempList = []

    for row in csv_data:
        if count == 0:
            count = 1
            continue
        else:
            # adding to the neighbourhood table
            records = (row[28],)
            query = "INSERT IGNORE INTO Neighbourhood(Neighbourhood_Name) VALUES(%s);"
            cursor.execute(query, records)

            # adding to the room type table
            records = (row[49],)
            query = "INSERT IGNORE INTO RoomType(RoomType_Name) VALUES(%s);"
            cursor.execute(query, records)

            # adding to the bed type table
            records = (row[54],)
            query = "INSERT IGNORE INTO BedType(BedType_Name) VALUES(%s);"
            cursor.execute(query, records)

            # adding to the cancellation type table
            records = (row[87],)
            query = "INSERT IGNORE INTO Cancellation(CancellationType) VALUES(%s);"
            cursor.execute(query, records)

            # adding to the location table
            records = (row[34],)
            records = records + (row[28],)
            query = '''INSERT IGNORE INTO Location(Street, Neighbourhood_Id) 
             VALUES(%s, (SELECT Neighbourhood_Id FROM Neighbourhood WHERE Neighbourhood_Name = %s));'''
            cursor.execute(query, records)

            # adding to the room table
            records = tuple(row[49:55])
            query = '''INSERT IGNORE INTO Room(RoomType_Id, Accomadations, Bathrooms, Bedrooms, Beds, BedType_Id, isDeleted) VALUES
             ((SELECT RoomType_Id FROM RoomType WHERE RoomType_Name = %s),%s, %s, %s, %s, (SELECT BedType_Id FROM BedType WHERE BedType_Name = %s),0);'''
            cursor.execute(query, records)

            # adding to the host table
            records = (row[16],)
            records = records + tuple(row[18:20])
            records = records + tuple(row[21:23])
            records = records + tuple(row[24:26])
            records = records + tuple(row[28:29])
            records = records + tuple(row[30:31])
            records = records + (row[33],)

            query = '''INSERT IGNORE INTO Host(Host_Id, Host_Name, Host_Since, Host_About, Host_Response, Host_Acceptance_Rate, Superhost, 
             Host_Neighbourhood, Host_Listing_Count, Host_Identity_Verified, isDeleted) VALUES(%s,%s,STR_TO_DATE(%s, '%m/%d/%Y'),%s,%s,%s,%s,
             (SELECT Neighbourhood_Id FROM Neighbourhood WHERE Neighbourhood_Name = %s),%s, %s,0);'''
            cursor.execute(query, records)

            # adding to the listing table
            records = tuple(row[0:2])
            records = records + tuple(row[4:7])
            records = records + tuple(row[10:11])
            records = records + (row[16],)
            records = records + (row[34],)
            records = records + (row[49],)
            records = records + (row[57],)
            records = records + (row[87],)
            query = '''INSERT INTO Listing VALUES(%s,%s,%s,%s,%s,%s,(SELECT Host_Id FROM Host WHERE Host_Id = %s),(SELECT Location_Id FROM Location WHERE Street = %s),
             (SELECT RoomType_Id FROM RoomType WHERE RoomType_Name = %s), REPLACE(REPLACE(%s, '$', ''),',',''), (SELECT Cancellation_Id FROM Cancellation WHERE CancellationType = %s),0);'''
            cursor.execute(query, records)
            count = count + 1

connection.commit()

# importing the data into the tables - Review - couldn't make before due to foreign keys restrictions
with open("excel/reviews.csv") as csv_file:
    csv_data = csv.reader(csv_file, delimiter=',')
    count = 0

    for row in csv_data:
        if count == 0:
            count = 1
            continue
        else:
            # adding to the reviews table
            records = tuple(row[0:4])
            records = records + (row[5],)
            query = '''INSERT INTO Review(Listing_Id, Review_Id, Date, Reviewer_Id, Comments, isDeleted) 
             VALUES((SELECT Listing_Id FROM Listing WHERE Listing_Id = %s),%s,STR_TO_DATE(%s, '%m/%d/%Y'),%s, %s,0);'''
            cursor.execute(query, records)
            count = count + 1
connection.commit()

# home page - main page users will come too
@app.route('/')
def main():
    return render_template('index.html')


# Neighbourhood page that shows all the attributes & rows for this table
@app.route('/neighbourhoodRecords')
def neighbourhoodRecords():
    query = "SELECT * FROM Neighbourhood WHERE Neighbourhood_Id != 13 ORDER BY Neighbourhood_Id;"
    cursor.execute(query)
    results = cursor.fetchall()
    return render_template('neighbourhoodRecords.html', results=results)


# Room Type page that shows all the attributes & rows for this table
@app.route('/roomTypeRecords')
def roomTypeRecords():
    query = "SELECT * FROM RoomType ORDER BY RoomType_Id;"
    cursor.execute(query)
    results = cursor.fetchall()
    return render_template('roomTypeRecords.html', results=results)

# Bed Type page that shows all the attributes & rows for this table
@app.route('/bedTypeRecords')
def bedTypeRecords():
    query = "SELECT * FROM BedType ORDER BY BedType_Id;"
    cursor.execute(query)
    results = cursor.fetchall()
    return render_template('bedTypeRecords.html', results=results)

# Reviewer page that shows all the attributes & rows for this table
@app.route('/reviewerRecords')
def reviewerRecords():
    query = "SELECT * FROM Reviewer;"
    cursor.execute(query)
    results = cursor.fetchall()
    return render_template('reviewerRecords.html', results=results)

# Cancellation page that shows all the attributes & rows for this table
@app.route('/cancellationRecords')
def cancellationRecords():
    query = "SELECT * FROM Cancellation ORDER BY Cancellation_Id;"
    cursor.execute(query)
    results = cursor.fetchall()
    return render_template('cancellationRecords.html', results=results)

# Location page that shows all the attributes & rows for this table
@app.route('/locationRecords')
def locationRecords():
    query = "SELECT * FROM Location;"
    cursor.execute(query)
    results = cursor.fetchall()
    return render_template('locationRecords.html', results=results)

# Room page that shows all the attributes & rows for this table
@app.route('/roomRecords')
def roomRecords():
    query = "SELECT * FROM Room;"
    cursor.execute(query)
    results = cursor.fetchall()
    return render_template('roomRecords.html', results=results)

# Host page that shows all the attributes & rows for this table
@app.route('/hostRecords')
def hostRecords():
    query = "SELECT * FROM Host WHERE isDeleted = 0;"
    cursor.execute(query)
    results = cursor.fetchall()
    return render_template('hostRecords.html', results=results)

# Listing page that shows all the attributes & rows for this table
@app.route('/listingRecords')
def listingRecords():
    query = "SELECT * FROM Listing WHERE isDeleted = 0;"
    cursor.execute(query)
    results = cursor.fetchall()
    return render_template('listingRecords.html', results=results)

# Reviewer page that shows all the attributes & rows for this table
@app.route('/reviewRecords')
def reviewRecords():
    query = "SELECT * FROM Review;"
    cursor.execute(query)
    results = cursor.fetchall()
    return render_template('reviewRecords.html', results=results)

# host page - when the user selects the host button, it will take them to the host page
# directed from the / page
@app.route('/host')
def host():
    query = "SELECT * FROM Neighbourhood WHERE Neighbourhood_Id != 13 ORDER BY Neighbourhood_Id;"
    cursor.execute(query)
    results = cursor.fetchall()
    return render_template('host.html', results=results)

# users will go to the host Id page when they search for a Host Id and want their information 
# directed from the /host page
@app.route('/hostId', methods=['GET', 'POST'])
def hostID():
    id = request.form['id']
    results = (id,)
    print(results)
    query = '''SELECT * FROM Host 
                INNER JOIN Neighbourhood AS N on Host.Host_Neighbourhood = N.Neighbourhood_Id
                WHERE Host_Id = %s AND isDeleted = 0;'''
    cursor.execute(query, results)
    results = cursor.fetchall()
    return render_template('hostID.html', results=results)

# user will again go the host Id page when they update information 
# directed from /hostId when the user updates information
@app.route('/hostId/', methods=['GET', 'POST'])
def hostUpdate():
    id = request.form['id']
    update = request.form['update']
    item = request.form['item']
    results = (item, id)

    # starting the transaction
    try:
        if update == 'Host_Name':
            query = "UPDATE Host SET Host_Name = %s WHERE Host_Id = %s;"
        if update == 'Host_About':
            query = "UPDATE Host SET Host_About = %s WHERE Host_Id = %s;"
        if update == 'Superhost':
            query = "UPDATE Host SET Superhost = %s WHERE Host_Id = %s;"
        if update == 'Host_Listing_Count':
            query = "UPDATE Host SET Host_Listing_Count = %s WHERE Host_Id = %s;"

        cursor.execute(query, results)
        message = "Update successful"
        flash(message, "success")
        connection.commit()

    
    # In case something went wrong    
    except mysql.connector.Error as error:
        print("Database failed to update: {}".format(error))
        message = "Database failed to update: {}".format(error)
        flash(message, "danger")
        #rollback
        connection.rollback()
    finally:
        query = "SELECT * FROM Host WHERE Host_Id = %s AND isDeleted = 0;"
        cursor.execute(query, (id,))
        results = cursor.fetchall()
        return render_template('hostID.html', results=results)

# user will go to a Listings css page for certain hosts information
# directed from the /hostId page
@app.route('/hostListings', methods=['GET', 'POST'])
def hostListings():
    id = request.form['id']
    results = (id,)

    #multiple Inner joins to display the names instead of just the ID numbers
    query = '''SELECT * FROM Listing
            INNER JOIN Host as H on H.Host_Id = Listing.Host_Id
            INNER JOIN Location as L on L.Location_Id = Listing.Location_Id
            INNER JOIN Room as R on R.Room_Id = Listing.Room_Id
            INNER JOIN RoomType as R2 on R.RoomType_Id = R2.RoomType_Id
            INNER JOIN Cancellation C on Listing.Cancellation_Policy = C.Cancellation_Id
            WHERE Listing.Host_Id = %s AND Listing.isDeleted = 0;'''
    cursor.execute(query, (id,))
    results = cursor.fetchall()

    # creating a cvs to download the data for a better readability for the user
    with open("hostListings.csv", mode='w') as file:
        writer = csv.writer(file)
        writer.writerow(["Listing Id", "URL", "Name", "Summary", "Notes", "Transit", "Host Id", "Host Name", "Location Id", "Location Name", "Room Id", "Room Name", "Price", "Cancellation Types"])
        for i in results:
            # Split the categories up for readability/tracking purposes
            writer.writerow([i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[13], i[7], i[24], i[8], i[35], i[9], i[37]])

    print("CSV created under the name: hostListings.csv")
    message = "CSV created under the name: hostListings.csv for better readability, please check your file directory for the csv file"
    flash(message, "success")

    return render_template('hostListings.html', results=results)

# user will go to a Listings css page for other hosts information
# directed from the /hostComp page 
@app.route('/hostCompListings', methods=['GET', 'POST'])
def hostComListings():
    id = request.form['id']
    results = (id,)
    query = '''SELECT * FROM Listing
            INNER JOIN Host as H on H.Host_Id = Listing.Host_Id
            INNER JOIN Location as L on L.Location_Id = Listing.Location_Id
            INNER JOIN Room as R on R.Room_Id = Listing.Room_Id
            INNER JOIN RoomType as R2 on R.RoomType_Id = R2.RoomType_Id
            INNER JOIN Cancellation C on Listing.Cancellation_Policy = C.Cancellation_Id
            WHERE Listing.Host_Id = %s AND Listing.isDeleted = 0;'''
    cursor.execute(query, (id,))
    results = cursor.fetchall()

    # creating a cvs to download the data for a better readability for the user
    with open("hostCompListings.csv", mode='w') as file:
        writer = csv.writer(file)
        writer.writerow(["Listing Id", "URL", "Name", "Summary", "Notes", "Transit", "Host Id", "Host Name", "Location Id", "Location Name", "Room Id", "Room Name", "Price", "Cancellation Types"])
        for i in results:
            # Split the categories up for readability/tracking purposes
            writer.writerow([i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[13], i[7], i[24], i[8], i[35], i[9], i[37]])
        
    print("CSV created under the name: hostCompListings.csv")
    message = "CSV created under the name: hostCompListings.csv for better readability, please check your file directory for the csv file"
    flash(message, "success")
    cursor.execute(query, (id,))
    results = cursor.fetchall()
    return render_template('hostListings.html', results=results)

# user will go to a page where it will display multiple information about different hosts that meet a certain critera
# directed from the /host page
@app.route('/hostComp', methods=['GET', 'POST'])
def hostComp():
    neighbour = request.form['neighbourhood']
    listing = request.form['Host_Listing_Count']
    superhost = request.form['Superhost']

    results = (neighbour, superhost, listing)

    query = "SELECT * FROM Host WHERE Host_Neighbourhood = %s AND Superhost = %s AND Host_Listing_Count = %s AND isDeleted = 0 LIMIT 10;"
    cursor.execute(query, results)
    results = cursor.fetchall()

    # creating a cvs to download the data for a better readability for the user
    with open("hostComp.csv", mode='w') as file:
        writer = csv.writer(file)
        writer.writerow(["Host Id", "Name", "Host Since", "About", "Response Time", "Acceptance Rate", "Superhost", "Neighbourhood", "Listing Count", "Id Verified"])
        for i in results:
            # Split the categories up for readability/tracking purposes
            writer.writerow([i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7], i[8], i[9]])

    print("CSV created under the name: hostComp.csv")
    message = "CSV created under the name: hostComp.csv for better readability, please check your file directory for the csv file"
    flash(message, "success")
    return render_template('hostComp.html', results=results)

# user will go to page to display listings that meet a certain critera
# directed from the /host page
@app.route('/hostListings/', methods=['GET', 'POST'])
def hostCompListings():
    priceSign = request.form['priceSign']
    price = request.form['price']
    neighbourhood = request.form['neighbourhood']
    roomTypeId = request.form['roomTypeId']
    cancellation = request.form['cancellation']

    results = (neighbourhood, roomTypeId, price, cancellation)

    query = '''DROP VIEW IF EXISTS hostListings;'''
    cursor.execute(query)

    #joins at least 3 tables and creating a view in order to perform aggregates on it later 
    if priceSign == '>':
        query = '''CREATE VIEW hostListings AS
            SELECT l.Location_Id  AS Location1, l.URL, l.Name, l.Summary, l.Notes, l.Transit, l.Host_Id, l.Room_Id AS Room1, 
            l.Price, l.Cancellation_Policy, L2.Location_Id AS Location2, L2.Neighbourhood_Id, r.Room_Id AS Room2, r.RoomType_Id
            FROM Listing AS l
            INNER JOIN Location AS L2 on l.Location_Id = L2.Location_Id and Neighbourhood_Id = %s
            INNER JOIN Room AS r on l.Room_Id = r.Room_Id and r.RoomType_ID = %s
            WHERE l.Price > %s AND l.Cancellation_Policy = %s'''

    if priceSign == '<':
        query = '''CREATE VIEW hostListings AS
            SELECT l.Location_Id  AS Location1, l.URL, l.Name, l.Summary, l.Notes, l.Transit, l.Host_Id, l.Room_Id AS Room1, 
            l.Price, l.Cancellation_Policy, L2.Location_Id AS Location2, L2.Neighbourhood_Id, r.Room_Id AS Room2, r.RoomType_Id
            FROM Listing AS l
            INNER JOIN Location AS L2 on l.Location_Id = L2.Location_Id and Neighbourhood_Id = %s
            INNER JOIN Room AS r on l.Room_Id = r.Room_Id and r.RoomType_ID = %s
            WHERE l.Price < %s AND l.Cancellation_Policy = %s'''

    if priceSign == '<=':
        query = '''CREATE VIEW hostListings AS
            SELECT l.Location_Id  AS Location1, l.URL, l.Name, l.Summary, l.Notes, l.Transit, l.Host_Id, l.Room_Id AS Room1, 
            l.Price, l.Cancellation_Policy, L2.Location_Id AS Location2, L2.Neighbourhood_Id, r.Room_Id AS Room2, r.RoomType_Id
            FROM Listing AS l
            INNER JOIN Location AS L2 on l.Location_Id = L2.Location_Id and Neighbourhood_Id = %s
            INNER JOIN Room AS r on l.Room_Id = r.Room_Id and r.RoomType_ID = %s
            WHERE l.Price <= %s AND l.Cancellation_Policy = %s'''

    if priceSign == '>=':
        query = '''CREATE VIEW hostListings AS
            SELECT l.Location_Id  AS Location1, l.URL, l.Name, l.Summary, l.Notes, l.Transit, l.Host_Id, l.Room_Id AS Room1, 
            l.Price, l.Cancellation_Policy, L2.Location_Id AS Location2, L2.Neighbourhood_Id, r.Room_Id AS Room2, r.RoomType_Id
            FROM Listing AS l
            INNER JOIN Location AS L2 on l.Location_Id = L2.Location_Id and Neighbourhood_Id = %s
            INNER JOIN Room AS r on l.Room_Id = r.Room_Id and r.RoomType_ID = %s
            WHERE l.Price >= %s AND l.Cancellation_Policy = %s'''

    if priceSign == '=':
        query = '''CREATE VIEW hostListings AS
            SELECT l.Location_Id  AS Location1, l.URL, l.Name, l.Summary, l.Notes, l.Transit, l.Host_Id, l.Room_Id AS Room1, 
            l.Price, l.Cancellation_Policy, L2.Location_Id AS Location2, L2.Neighbourhood_Id, r.Room_Id AS Room2, r.RoomType_Id
            FROM Listing AS l
            INNER JOIN Location AS L2 on l.Location_Id = L2.Location_Id and Neighbourhood_Id = %s
            INNER JOIN Room AS r on l.Room_Id = r.Room_Id and r.RoomType_ID = %s
            WHERE l.Price = %s AND l.Cancellation_Policy = %s'''
    cursor.execute(query, results)

    query = "SELECT * FROM hostListings"
    cursor.execute(query)
    results = cursor.fetchall()

    # creating a cvs to download the data for a better readability for the user
    with open("Listings.csv", mode='w') as file:
        writer = csv.writer(file)
        writer.writerow(["Listing Id", "URL", "Name", "Summary", "Notes", "Transit", "Host Id", "Location Id", "Room Id", "Price", "Cancellation"])
        for i in results:
            # Split the categories up for readability/tracking purposes
            writer.writerow([i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7], i[8], i[9], i[10]])

    print("CSV created under the name: Listings.csv")
    message = "CSV created under the name: Listings.csv for better readability, please check your file directory for the csv file"
    flash(message, "success")

    return render_template('hostCompListings.html', results=results)


# user will go to a page where they can input information about a new host
# directed from the /host page
@app.route('/newHost', methods=['GET', 'POST'])
def newHost():
    query = "SELECT * FROM Neighbourhood WHERE Neighbourhood_Id != 13 ORDER BY Neighbourhood_Id;"
    cursor.execute(query)
    results = cursor.fetchall()
    return render_template('newHost.html', results=results)

# user will go to Host page after the new host was added
# directed from the /newHost page
@app.route('/host/', methods=['GET', 'POST'])
def newHostCreated():
    name = request.form['name']
    date = request.form['date']
    about = request.form['about']
    respTime = request.form['respTime']
    superhost = request.form['superhost']
    neighbourhood = request.form['neighbourhood']
    listing_count = request.form['listing_count']
    idverify = request.form['idverify']

    # starting the transaction
    try:
        query = "SELECT Host_Id FROM Host WHERE isDeleted = 0;"
        cursor.execute(query)
        results = cursor.fetchall()
    
        host_id = random.randint(0,90000000)
        if host_id in results:
            host_id = random.randint(0,90000000)

        records = [host_id, name, date, about, respTime, '100%', superhost, neighbourhood, listing_count, idverify]

        query = '''INSERT INTO Host(Host_Id, Host_Name, Host_Since, Host_About, Host_Response, Host_Acceptance_Rate, Superhost, 
             Host_Neighbourhood, Host_Listing_Count, Host_Identity_Verified, isDeleted) VALUES(%s,%s,%s,%s,%s,%s,%s,
              %s,%s,%s,0);'''

        cursor.execute(query, records)
        message = "Your new host ID is " + str(host_id)
        flash(message, "success")
        connection.commit()
    
    # In case something went wrong    
    except mysql.connector.Error as error:
        print("Database failed to update: {}".format(error))
        message = "Database failed to update: {}".format(error)
        flash(message, "danger")
        #rollback
        connection.rollback()

    finally:
        return render_template('host.html')

# user will go to Host page after the new host was added
# directed from the /newHost page
@app.route('/isDeleted', methods=['GET', 'POST'])
def deleteHost():
    id = request.form['id']
    id = (id,)
    query = '''UPDATE Host Set isDeleted = 1 WHERE Host_Id = %s '''
    cursor.execute(query, id)

    # hides/deletes the listings for the host that was just deleted  
    # pk and fk integrity 
    query = '''UPDATE Listing Set isDeleted = 1 WHERE Host_Id = %s'''
    cursor.execute(query, id)
    message = "Host was deleted. ID number: " + str(id[0])
    flash(message, "success")
    return render_template('host.html')


# start of the customer side of the application 
# directed from the main page (index.html)

@app.route('/customer', methods=['GET', 'POST'])
def customer():
    query = '''DROP VIEW IF EXISTS neighbourPrices;'''
    cursor.execute(query)

    #another view to query for aggregates for the averages in price, bathrooms, bedrooms, and beds per neighbourhood 
    query = '''CREATE VIEW neighbourPrices AS
            SELECT l.Location_Id  AS Location1, l.URL, l.Name, l.Summary, l.Notes, l.Transit, l.Host_Id, l.Room_Id AS Room1, 
            l.Price, l.Cancellation_Policy, L2.Location_Id AS Location2, L2.Neighbourhood_Id, r.Room_Id AS Room2, r.RoomType_Id,
            r.Bathrooms, r.Bedrooms, r.Beds
            FROM Listing AS l
            INNER JOIN Location AS L2 on l.Location_Id = L2.Location_Id
            INNER JOIN Room AS r on l.Room_Id = r.Room_Id'''

    cursor.execute(query)
        
    # using the view to find the average prices and min and maxs per neighbourhood
    query = '''SELECT N.Neighbourhood_Id, N.Neighbourhood_Name, ROUND(AVG(Price),2) as AvgPrice, MIN(Price) as MinPrice, MAX(Price) as MaxPrice, COUNT(*) as count
    FROM neighbourPrices
    INNER JOIN Neighbourhood AS N on neighbourPrices.Neighbourhood_Id = N.Neighbourhood_Id
    WHERE N.Neighbourhood_Name != ""
    GROUP BY N.Neighbourhood_Name; '''
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    return render_template('customer.html', results = results)

# user will go to a Listings css page for a random Listing
# directed from the /customer page
@app.route('/custListing', methods=['GET', 'POST'])
def custListing():
    id = request.form['neighbourhood']
    results = (id,)
    query = '''SELECT * FROM Listing
            INNER JOIN Host as H on H.Host_Id = Listing.Host_Id
            INNER JOIN Location as L on L.Location_Id = Listing.Location_Id
            INNER JOIN Room as R on R.Room_Id = Listing.Room_Id
            INNER JOIN RoomType as R2 on R.RoomType_Id = R2.RoomType_Id
            INNER JOIN Cancellation C on Listing.Cancellation_Policy = C.Cancellation_Id
            INNER JOIN Neighbourhood N on H.Host_Neighbourhood = N.Neighbourhood_Id
            WHERE Listing.isDeleted = 0 AND L.Neighbourhood_Id = %s 
            ORDER BY RAND() LIMIT 1;'''
    cursor.execute(query, (id,))
    results = cursor.fetchall()

   # creating a cvs to download the data for a better readability for the user
    with open("randomListings.csv", mode='w') as file:
        writer = csv.writer(file)
        writer.writerow(["Listing Id", "URL", "Name", "Summary", "Notes", "Transit", "Host Id", "Host Name", "Location Id", "Location Name", "Room Id", "Room Name", "Price", "Cancellation Types"])
        for i in results:
            # Split the categories up for readability/tracking purposes
            writer.writerow([i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[13], i[7], i[24], i[8], i[35], i[9], i[37]])

    print("CSV created under the name: randomListings.csv")
    message = "CSV created under the name: randomListings.csv for better readability, please check your file directory for the csv file"
    flash(message, "success")

    return render_template('hostListings.html', results=results)

# user will go to a Listings css page for a random Listing
# directed from the /customer page
@app.route('/reviews', methods=['GET', 'POST'])
def reviews():
    id = request.form['id']
    results = (id,)

    #Sub-query and joining two tables to check that the Listing Id is in the Listing table and was not deleted/not there
    query = '''SELECT * FROM Review
            INNER JOIN Reviewer R on Review.Reviewer_Id = R.Reviewer_Id
            WHERE Listing_Id IN (
            SELECT Listing.Listing_Id  FROM Listing
            WHERE Listing.Listing_Id = %s
            AND Listing.isDeleted = 0
            );'''

    cursor.execute(query, (id,))
    results = cursor.fetchall()

    # creating a cvs to download the data for a better readability for the user
    with open("reviews.csv", mode='w') as file:
        writer = csv.writer(file)
        writer.writerow(["Review Id", "Listing Id", "Date", "Reviewer Id", "Reviewer_Name" "Comments"])
        for i in results:
            # Split the categories up for readability/tracking purposes
            writer.writerow([i[0], i[1], i[2], i[3], i[7], i[4]])

    print("CSV created under the name: reviews.csv")
    message = "CSV created under the name: reviews.csv for better readability, please check your file directory for the csv file"
    flash(message, "success")

    return render_template('reviewRecords.html', results = results)

#close connection when user quits
def onExit():
    connection.close()
    print() 
    print()
    print("Thank you for using this LuckySharms application Professor Rao, have a great summer!")
    print()
atexit.register(onExit)

if __name__ == '__main__':

    app.secret_key = 'super secret key'

    app.run(host='localhost', port=5000)
