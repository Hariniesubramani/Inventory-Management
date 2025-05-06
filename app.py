from flask import Flask, render_template,url_for,redirect,request,flash
from flask_mysqldb import MySQL

app = Flask(__name__)

#mysql connections
app.config["MYSQL_HOST"]="localhost"
app.config["MYSQL_USER"]="root"
app.config["MYSQL_PASSWORD"]="Harinie@08"     
app.config["MYSQL_DB"]="Product"
app.config["MYSQL_CURSORCLASS"]="DictCursor"
mysql = MySQL(app)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/product')
def product():
    return redirect(url_for('home'))

@app.route('/movement')
def movement():
    con = mysql.connection.cursor()
    con.execute("SELECT * FROM movement")
    res = con.fetchall()
    con.close()
    return render_template("movement.html",movement=res)

@app.route('/location')
def location():
    con=mysql.connection.cursor()
    sql="SELECT*FROM location"
    con.execute(sql)
    res=con.fetchall()
    con.close()
    return render_template("location.html",datas=res)

#Loading Home page
@app.route('/home')
def home():
    con=mysql.connection.cursor()
    sql="SELECT*FROM products"
    con.execute(sql)
    res=con.fetchall()
    con.close()
    return render_template("home.html",datas=res)

# ADD New User 
@app.route('/addUsers',methods=["GET","POST"])
def addUsers():
    if request.method=="POST":
        p_name=request.form["p_name"]
        price=request.form['price']
        quantity=request.form['quantity']
        con=mysql.connection.cursor()
        sql="INSERT INTO products(product_name,price,quantity) VALUES(%s,%s,%s)"
        con.execute(sql,[p_name,price,quantity])
        mysql.connection.commit()
        con.close()        
        flash('Product Added Successfully')
        return redirect(url_for("home"))
    return render_template("addusers.html")

#update user
@app.route("/editUser/<string:product_id>",methods=['GET','POST'])

def editUser(product_id):
    con=mysql.connection.cursor()
    if request.method=="POST":
        p_name=request.form["p_name"]
        price=request.form['price']
        quantity=request.form['quantity']
        sql="update products set product_name=%s,price=%s,quantity=%s where product_id=%s"
        con.execute(sql,[p_name,price,quantity,product_id])
        mysql.connection.commit()
        con.close()
        flash('Product Details Updated')
        return redirect(url_for("home"))
    sql="SELECT*FROM products where product_id=%s"
    con.execute(sql, [product_id])
    res=con.fetchone()
    con.close()
    return render_template("editUser.html",data=res,product_id=product_id)

#Delete user
@app.route("/deleteUser/<string:product_id>",methods=['GET','POST'])

def deleteUser(product_id):
    con=mysql.connection.cursor()
    sql="delete from products where product_id=%s"
    con.execute(sql,[product_id])
    mysql.connection.commit()
    con.close()
    flash('User Details Deleted')
    return redirect(url_for("home"))

# ADD New Location
@app.route('/addLocation',methods=["GET","POST"])
def addLocation():
    if request.method=="POST":
        l_name=request.form["l_name"]
        con=mysql.connection.cursor()
        sql="INSERT INTO location(location_name) VALUES(%s)"
        con.execute(sql,[l_name])
        mysql.connection.commit()
        con.close()        
        flash('Location Added Successfully')
        return redirect(url_for("location"))
    return render_template("addlocation.html")

#update location
@app.route("/editlocation/<string:location_id>",methods=['GET','POST'])

def editlocation(location_id):
    con=mysql.connection.cursor()
    if request.method=="POST":
        l_name=request.form["l_name"]
        sql="update location set location_name=%s where location_id=%s"
        con.execute(sql,[l_name,location_id])
        mysql.connection.commit()
        con.close()
        flash('Location Details Updated')
        return redirect(url_for("location"))
    sql="SELECT*FROM location where location_id=%s"
    con.execute(sql, [location_id])
    res=con.fetchone()
    con.close()
    return render_template("editlocation.html",data=res,location_id=location_id)

#Delete location
@app.route("/deletelocation/<string:location_id>",methods=['GET','POST'])

def deletelocation(location_id):
    con=mysql.connection.cursor()
    sql="delete from location where location_id=%s"
    con.execute(sql,[location_id])
    mysql.connection.commit()
    con.close()
    flash('Location Details Deleted')
    return redirect(url_for("location"))

#product movement
@app.route('/addmovement', methods=["GET", "POST"])
def addmovement():
    if request.method == "POST":
        product_name = request.form['product_name']
        from_location = request.form['from_location']
        to_location = request.form['to_location']
        quantity = int(request.form['quantity']) 
        con = mysql.connection.cursor()
        con.execute("SELECT quantity FROM products WHERE product_name = %s", [product_name])
        product = con.fetchone()
        if product and product['quantity'] >= quantity:
            con.execute("UPDATE products SET quantity = quantity - %s WHERE product_name = %s", [quantity, product_name])
            sql = """ INSERT INTO movement (product_name, from_location, to_location, quantity)
            VALUES (%s, %s, %s, %s) """
            con.execute(sql, [product_name, from_location, to_location, quantity])
            mysql.connection.commit()
            con.close()
            flash("Product moved and quantity updated successfully!", "success")
        else:
            flash("Insufficient stock available!", "error")
            con.close()

        return redirect(url_for("movement"))
    con = mysql.connection.cursor()
    con.execute("SELECT * FROM products")
    products = con.fetchall()
    con.execute("SELECT * FROM location")
    locations = con.fetchall()
    mysql.connection.commit()
    con.close()
    return render_template("addmovement.html", pro=products, loc=locations)

#Delete movement
@app.route("/deleteMovement/<string:id>",methods=['GET','POST'])
def deleteMovement(id):
    con=mysql.connection.cursor()
    sql="delete from movement where id=%s"
    con.execute(sql,[id])
    mysql.connection.commit()
    con.close()
    flash('User Details Deleted')
    return redirect(url_for("movement"))

@app.route("/report")
def report():
    con = mysql.connection.cursor()

    con.execute("""
        SELECT 
            p.product_name,
            l.location_name,
            IFNULL(SUM(CASE WHEN m.to_location = l.location_name AND m.product_name = p.product_name THEN m.quantity ELSE 0 END), 0)
            -
            IFNULL(SUM(CASE WHEN m.from_location = l.location_name AND m.product_name = p.product_name THEN m.quantity ELSE 0 END), 0)
            AS balance_quantity
        FROM 
            products p
        CROSS JOIN 
            location l
        LEFT JOIN 
            movement m ON m.product_name = p.product_name 
        GROUP BY 
            p.product_name, l.location_name
        HAVING 
            balance_quantity > 0
        ORDER BY 
            l.location_name, p.product_name;
    """)

    report_data = con.fetchall()
    con.close()
    return render_template("report.html", report=report_data)


if(__name__ == '__main__'):
    app.secret_key="abc123"
    app.run(debug=True) 