from flask import *
import pymysql
import sms
import requests
import datetime
import base64
from requests.auth import HTTPBasicAuth

app = Flask(__name__)
app.secret_key = "AW_r%@jN*HU4AW_r%@jN*HU4AW_r%@jN*HU4"

@app.route('/')
def home():
   connection = pymysql.connect(host= 'localhost', user= 'root', password= '', database= 'kiboko')

   sqlPhone = "SELECT * FROM products WHERE product_category = 'Phones' "

   cursorPhone =connection.cursor()
   cursorPhone.execute(sqlPhone)

   phones = cursorPhone.fetchall()

   sqlLaptops = "SELECT * FROM products WHERE product_category = 'Laptops'"

   cursorLaptop =connection.cursor()
   cursorLaptop.execute(sqlLaptops)

   Laptops =cursorLaptop.fetchall()

   sqlDetergents = "SELECT * FROM products WHERE product_category = 'Detergents'"

   cursorDetergent = connection.cursor()
   cursorDetergent.execute(sqlDetergents)
   
   Detergents =cursorDetergent.fetchall()

   sqlClothes = "SELECT * FROM products WHERE product_category = 'Clothes'"

   cursorClothe = connection.cursor()
   cursorClothe.execute(sqlClothes)
   
   Clothes =cursorClothe.fetchall()

   sqlElectronics = "SELECT * FROM products WHERE product_category = 'Electronics'"

   cursorElectronic = connection.cursor()
   cursorElectronic.execute(sqlElectronics)
   
   Electronics =cursorElectronic.fetchall()

   return render_template('home.html', phones = phones, Laptops=Laptops, Detergents= Detergents, Clothes = Clothes,  Electronics = Electronics)

@app.route('/single_item/<product_id>')
def single(product_id):
    connection = pymysql.connect(host='localhost', user='root', password='', database='kiboko')
    sqlproduct= "SELECT * FROM products WHERE product_id = %s"

    cursorproduct=connection.cursor()
    cursorproduct.execute(sqlproduct, product_id)
    product = cursorproduct.fetchone()
    
    category = product[4]
    sqlsimilar = "SELECT * FROM products WHERE product_category = %s LIMIT 4"

    cursorsimilar = connection.cursor()
    cursorsimilar.execute(sqlsimilar, category)
    similarproducts = cursorsimilar.fetchall()

    return render_template('single.html', product = product, similarproducts = similarproducts)
    
@app.route('/signup',methods = ['POST','GET'])
def signup():
   if request.method== 'GET':
       return render_template('signup.html')
   else:
       username = request.form['username'] 
       email = request.form['email'] 
       phone = request.form['phone']
       password = request.form['password1']
       password2 = request.form['password2']

       if len(password) < 8:
           return render_template('signup.html', error='password must be atleast 8 characters')
       elif password != password2:
           return render_template('signup.html', error='passwords do not match')
       else:
           connection = pymysql.connect(host ='localhost' ,user= 'root' ,password= '', database='kiboko')
           sql = '''
           INSERT INTO USERS (username,email,phone,password)
           VALUES (%s,%s,%s,%s)
           '''

           cursor= connection.cursor()
           cursor.execute(sql,(username,email,phone,password))
           connection.commit()
           sms.send_sms(phone, "Thank you for registering")           


           return render_template('signup.html',success='registered successfully')
       

@app.route('/signin', methods=['POST','GET'])
def signin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        connection = pymysql.connect(host='localhost', user='root', password='', database='kiboko')
        sql = '''
        select * from users where username = %s and password = %s
        '''

        cursor = connection.cursor()
        cursor.execute(sql, (username, password))

        if cursor.rowcount == 0:
            return render_template('signin.html', error = "Invalid password")
        else:
            session['key'] = username
            return redirect('/')

    else:
        return render_template('signin.html')
    
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/signin')



@app.route('/mpesa', methods=['POST', 'GET'])
def mpesa_payment():
    if request.method == 'POST':
        phone = str(request.form['phone'])
        amount = str(request.form['amount'])
        # GENERATING THE ACCESS TOKEN
        # create an account on safaricom daraja
        consumer_key = "GTWADFxIpUfDoNikNGqq1C3023evM6UH"
        consumer_secret = "amFbAoUByPV2rM5A"

        api_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"  # AUTH URL
        r = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))

        data = r.json()
        access_token = "Bearer" + ' ' + data['access_token']

        #  GETTING THE PASSWORD
        timestamp = datetime.datetime.today().strftime('%Y%m%d%H%M%S')
        passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
        business_short_code = "174379"
        data = business_short_code + passkey + timestamp
        encoded = base64.b64encode(data.encode())
        password = encoded.decode('utf-8')

        # BODY OR PAYLOAD
        payload = {
            "BusinessShortCode": "174379",
            "Password": "{}".format(password),
            "Timestamp": "{}".format(timestamp),
            "TransactionType": "CustomerPayBillOnline",
            "Amount": "1",  # use 1 when testing
            "PartyA": phone,  # change to your number
            "PartyB": "174379",
            "PhoneNumber": phone,
            "CallBackURL": "https://modcom.co.ke/job/confirmation.php",
            "AccountReference": "account",
            "TransactionDesc": "account"
        }

        # POPULAING THE HTTP </div>HEADER
        headers = {
            "Authorization": access_token,
            "Content-Type": "application/json"
        }

        url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"  # C2B URL

        response = requests.post(url, json=payload, headers=headers)
        print(response.text)
        return '<h3>Please Complete Payment in Your Phone and we will deliver in minutes</h3>' \
               '<a href="/" class="btn btn-dark btn-sm">Back to Products</a>'

@app.route('/vendoraccount', methods = ['POST', 'GET'])
def accuont():
    if request.method == 'GET':
        return render_template('account.html')
    else:
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        county = request.form['county']
        password = request.form['password']
        password2 = request.form['password']
        email = request.form['email']

    if len(password) < 8:
           return render_template('account.html', error='password must be atleast 8 characters')
    elif password != password2:
           return render_template('account.html', error='passwords do not match')

    connection = pymysql.connect( host='localhost', user='root', password='', database='kiboko')
    sql = '''
    INSERT INTO vendors  (firstname, lastname , county , password , email ) VALUES (%s,%s,%s,%s,%s)'''
    
    cursor = connection.cursor()
    cursor.execute(sql, (firstname, lastname, county, password, email))
    connection.commit()

    return render_template('acccount.html', success= 'Successfully Created a Vendor account')
if __name__== '__main__':
    app.run()