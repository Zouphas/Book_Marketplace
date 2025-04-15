from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import os

app = Flask(__name__)

def create_db_connection():
    password = "" 

    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password=password,  # login to root w my password
            database="book_marketplace"
        )
        return connection
    except mysql.connector.Error as err:
        print(f" Database connection failed - {err}")    #if fails print to terminal
        return None


# DB Route
@app.route('/db')
def db_test():
    # Fetch data from database
    connection = create_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id, username, address FROM users;")
    result = cursor.fetchall()
    connection.close()
    
    # Pass result to HTML template for formatting
    return render_template('users.html', users=result)

@app.route('/', methods =['GET', 'POST'])
def add():
    if request.method == 'POST':
        user_name = request.form['user_name']  # Getting the user input from the form
        user_pass = request.form['user_pass']  
        
        # You can process or store the input here (e.g., in a database)

        action = request.form['action']

        if action == 'Submit':
            if login(user_name, user_pass):
                return redirect(url_for('home2', usern= user_name))
                #return f" You have logged in as Username: {user_name} User Pass: {user_pass}"
            else:
                 return f" You cannot log in as Username: {user_name}"   
        else:   
            user_add= request.form['user_add'] 
            if CreateUser(user_name, user_pass, user_add):
                return f" You have created an account as Username: {user_name} User Pass: {user_pass} User Address: {user_add}"
            else:
                return f" You cannot create an account as Username: {user_name}"   


    return render_template('add.html')  # Render the form when visiting the page via GET

#actual homepage once user has logged in
@app.route('/home2', methods = (['GET', 'POST']))
def home2(book = ""):
    #usern = request.args.get('usern', 'Guest')
    usern = request.form.get('usern', request.args.get('usern', 'Guest'))
    result = bookSearch("")
    if request.method == 'POST':
        if request.form["action"] == "delete_account":
            deleteAccount(usern)
            return render_template('add.html')
        elif request.form["action"] == "logout":
             return redirect(url_for('add'))
        elif request.form["action"] == "search_book":
            find_book = request.form['search_book']
            result = bookSearch(find_book)
        elif request.form["action"] == 'sell_book':
            return redirect(url_for('sellbook', usern = usern))


    return render_template('userhome.html', user=usern, books=result)   

def bookSearch(bName):
    connection = create_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT Title, author, isbn, genre FROM book WHERE Title LIKE %s;", (f"{bName}%",))
    result = cursor.fetchall()
    connection.close()
    return result




def deleteAccount(usern):
    connection = create_db_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM users WHERE username = %s ", (usern,))
    connection.commit()
    connection.close()

def login(usern, userp):
    # Fetch data from database
    connection = create_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT username, password FROM users WHERE username = %s AND password = %s;", (usern, userp))
    result = cursor.fetchone()
    connection.close()
    
    # Pass result to HTML template for formatting
    if result:
        return True;
    else: 
        return False;

def CreateUser(usern, userp, user_add):
    # Fetch data from database
    connection = create_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT username FROM users WHERE username = %s;", (usern,))
    result = cursor.fetchone()

    
    # Pass result to HTML template for formatting
    if result or len(usern) > 30 or len(userp) > 50 or len(user_add) > 150:
        connection.close()
        return False;  #User alr exists
    else:               #User DNE, make new one
        cursor.execute("INSERT INTO users (username, password, address) VALUES (%s, %s, %s);", (usern, userp, user_add))
        connection.commit()
        connection.close()
        return True;
 
@app.route('/addbook', methods=['GET', 'POST'])
def sellbook():
    usern = request.form.get('usern') or request.args.get('usern', 'Guest')


    connection = create_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT Title, author, price, conditionin, isbn, genre FROM book NATURAL JOIN listing WHERE SellerId = %s;", (usern,))
    result = cursor.fetchall()
  


    if request.method == 'POST':
        if request.form["action"] == "addBook":
            bname = request.form['bookname']  # Getting the user input from the form
            cond = request.form['conditionin']
            isbn = request.form['book']
            print(bname + cond + isbn)
            cursor.execute("INSERT INTO Listing (Price, CondtitionIn, SellerId ) VALUES (%s, %s, %s);", (isbn, cond, usern))
            connection.commit()
            
    connection.close()
    return render_template('sellbook.html', user=usern, books = result)

    




# ✅ Run Flask App
if __name__ == '__main__':
    app.run(debug=True)