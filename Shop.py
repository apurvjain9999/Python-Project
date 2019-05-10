from flask import Flask,render_template,request,redirect,session,url_for
import pymysql

connection = pymysql.connect(host='localhost',
                             user='root',
                             passwd='',
                             db='grocerymania',
                             port = 3306
                            )

cart = {}
dict = {}
flag = 0
sum = 0
value = 0
OrderName = ""
app = Flask(__name__)
app.secret_key = "It is a secret"

@app.route('/')
def index():
    return  render_template('login.html')

@app.route('/authenticate',methods=['POST', 'GET'])
def authenticate():
    if request.method=='POST':
        name=request.form['user']
        password = request.form['pass']
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM signup WHERE Username = %s and Password = %s",
            (name,password))
            row_count = cursor.rowcount
            if row_count == 0:
                return "Invalid Credentials"
            elif row_count > 0:
                session['username'] = name
                return render_template('home.html')
               

@app.route('/signuppage')
def signuppage():
    return  render_template('signup.html')

@app.route('/home')
def HomePage():
    return  render_template('home.html')

@app.route('/signup',methods=['POST', 'GET'])
def signup():
    if request.method=='POST':
        name=request.form['user']
        email=request.form['email_address']
        password = request.form['pass']
        mobile = request.form['mobile']
        with connection.cursor() as cursor:
            cursor.execute("SELECT Email FROM signup WHERE Email = %s",
            (email))
            row_count = cursor.rowcount
            if row_count == 0:
                sql ="INSERT INTO signup (Email,Username,Password,Mobile) VALUES (%s,%s,%s,%s)"
                cursor.execute(sql,(email,name,password,mobile))
                connection.commit()
                return "Successfully Registered"
            elif row_count > 0:
                return "Email already exists"

@app.route('/forgotPage')
def forgot():
    return render_template('forgot.html')

@app.route('/logout')
def logout():
    session.pop('username')
    global flag
    global sum
    global value
    dict.clear()
    cart.clear()
    global OrderName
    sum = 0
    flag = 0
    value = 0
    OrderName = ""
    return redirect(url_for('index'))

@app.route('/forgotPassword',methods=['POST', 'GET'])
def forgotPassword():
    if request.method=='POST':
        email=request.form['email_address']
        mobile = request.form['mobile']
        with connection.cursor() as cursor:
            cursor.execute("SELECT Password FROM signup WHERE Email = %s and Mobile = %s",(email,mobile))
            row_count = cursor.rowcount
            result = cursor.fetchall()
            if row_count == 0:
                return "You are not registered with us...."
            else:
                for row in result:
                    return "Your Password is " +row[0]


@app.route('/Vegetables')
def Vegetables():
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM products WHERE Product_Type = 'Vegetables' ORDER BY Product_ID ASC")
        row_count = cursor.rowcount
        result = cursor.fetchall()
    return render_template('Vegetables.html',data = result)


@app.route('/AddCart',methods=['POST', 'GET'])
def AddCartVegetables():
    if request.method=='POST':
        global flag
        global sum
        Name = request.form['name']
        ID = request.form['ID']
        Price = request.form['price']
        Quantity = request.form['quantity']
        if ID in cart.keys():
            cart[ID]['Quantity'] = int(cart[ID]['Quantity']) + int(Quantity)
            sum = sum - cart[ID]['Amount']
            cart[ID]['Amount'] = round(int(cart[ID]['Quantity'])*float(Price),2)
            sum = sum + cart[ID]['Amount']
        else:
            dict['Name'] = Name
            dict['Price'] = Price
            dict['Quantity'] = int(Quantity)
            dict['Amount'] = round(float(Price)*int(Quantity),2)
            cart[ID] = dict.copy()
            sum = sum + cart[ID]['Amount']
            flag = 1
        return redirect(url_for('Vegetables'))

@app.route('/carts')
def carts():
    global OrderName
    for i in cart:
        OrderName = OrderName + cart[i]['Name']+" X"+str(cart[i]['Quantity'])+",  "
    return render_template('Cart.html', data = cart, check = flag, bill = sum)

@app.route('/deleteItem/<string:id>')
def deleteItem(id):
    global sum
    global flag
    sum = sum - cart[id]['Amount']
    del cart[id]
    length = len(cart.keys())
    if length ==0:
        flag = 0;
    return redirect(url_for('carts'))

@app.route('/emptyCart')
def emptyCart():
    global flag
    cart.clear()
    length = len(cart.keys())
    if length ==0:
        flag = 0;
    return redirect(url_for('carts'))

@app.route('/takeAddress')
def takeAddress():
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM userdetails WHERE Name = %s",(session['username']))
        row_count = cursor.rowcount
        if row_count > 0:
            return render_template('Payment.html')
        else:
            return render_template('Address.html')

@app.route('/AddDetails',methods=['POST'])
def AddDetails():
    if request.method=='POST':
        Home = request.form['HomeNo']
        Locality = request.form['Locality']
        City = request.form['City']
        State = request.form['State']
        Pincode = request.form['Pincode']
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO userdetails VALUES(%s,%s,%s,%s,%s,%s)",(session['username'],Home,Locality,City,State,Pincode))
            connection.commit()
            return render_template('Payment.html')
    

@app.route('/order',methods=['POST'])
def FinishOrder():
    global sum
    global OrderName
    global flag
    if request.method=='POST':
        payMethod = request.form['payment']
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO orderdetails(Username,Order_Amount,Payment_Method) VALUES(%s,%s,%s)",(session['username'],sum,payMethod))
            connection.commit()
            cursor.execute("INSERT INTO pastorders(Order_Name,Order_Amount,Person_Name) VALUES(%s,%s,%s)",(OrderName,sum,session['username']))
            connection.commit()
            OrderName = ""
            cart.clear()
            dict.clear()
            sum = 0
            flag = 0
            return redirect(url_for('HomePage'))

@app.route('/AccountInfo')
def AccountInfo():
    global value
    with connection.cursor() as cursor:
        cursor.execute("SELECT Username,Mobile,HomeNo,Locality,City,State,Zipcode FROM userdetails right outer join signup On Username = Name WHERE Username = %s",(session['username']))
        result = cursor.fetchall()
        cursor.execute("SELECT * FROM userdetails WHERE Name = %s",(session['username']))
        row_count = cursor.rowcount
        if row_count>0:
            value = 1
        return render_template('AccountInfo.html', data = result,data2 = value)

@app.route('/change')
def changePage():
    return render_template('change.html')

@app.route('/update',methods=['POST'])
def update():
    Homeno = request.form['HomeNo']
    Locality = request.form['Locality']
    City = request.form['City']
    State = request.form['State']
    Pincode = request.form['Pincode']
    Mobile = request.form['Mobile']
    with connection.cursor() as cursor:
        cursor.execute("Update signup set Mobile = %s where Username = %s",(Mobile,session['username']))
        connection.commit()
        cursor.execute("Update userdetails set HomeNo = %s,Locality = %s,City = %s,State = %s,Zipcode =%s where Name = %s",(Homeno,Locality,City,State,Pincode,session['username']))
        connection.commit()
        return redirect(url_for('AccountInfo'))

@app.route('/pastOrders')
def pastOrders():
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM pastorders where Person_Name = %s Order by Order_ID desc",(session['username']))
        result = cursor.fetchall()
    return render_template('past.html',data = result)


        
if __name__ == '__main__':
    app.run()
