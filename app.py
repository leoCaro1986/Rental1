from flask import Flask, render_template, request, redirect, url_for, session
import pymongo
from bson.objectid import ObjectId
import os
from bson import ObjectId
from pymongo.collation import CollationAlternate
# from flask_pymongo import Pymongo



#conexion
myClient = pymongo.MongoClient("mongodb://localhost:27017")
myDb = myClient["RentalDb"] #database
userCollection = myDb["user"] #myCollection
propertyCollection = myDb["property"]
reservaCollection = myDb["reserva"] #myCollection

app = Flask(__name__)
app.secret_key = "pass1234"
app.config['UPLOAD_FOLDER'] = './static/images'

 
@app.route('/')
def index():
    result = []
    for doc in propertyCollection.find():
        result.append({
            '_id':doc['_id'],
            'cityP':doc['cityP'],
            'countryP': doc['countryP'],
            'adressP': doc['adressP'],
            'ubication': doc['ubication'],
            'roomNumber': doc['roomNumber'],
            'imageP': doc['imageP'],
            'priceDay': doc['priceDay'],
            'Description': doc['Description']
        })
    return render_template("index.html", propertyp = result)


#formulario para registrar usuario
@app.route('/sign_in')
def sign_in():
    return render_template("sign_in.html")


@app.route('/addProperty')
def addproperty():
    return render_template("addProperty.html")

@app.route('/especificProperty/<id>')
def especificProperty(id):
    property = propertyCollection.find_one({'_id': ObjectId(id)})
    result = []
    result.append({
        '_id':property['_id'],
        'cityP':property['cityP'],
        'countryP': property['countryP'],
        'adressP': property['adressP'],
        'ubication': property['ubication'],
        'roomNumber': property['roomNumber'],
        'imageP': property['imageP'],
        'priceDay': property['priceDay'],
        'Description': property['Description'],
        'listimage': property['listimage']
    })
    return render_template("especificProperty.html", propertyp = result)

@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/loginApp', methods=["POST"])
def loginApp():
    username = request.form.get('username')
    password = request.form.get('password')
    resultRequest = {'password': password,}
    session['user'] = username
    result = userCollection.find_one(resultRequest)
    idUser = str(result['_id'])
    session['roll'] = result["roll"]
    if result != None:
            if result["roll"] == "invitado":
                return redirect(url_for('getProperty'))
            else:
                return redirect(url_for('getPropertyByIdUser', id = idUser))

@app.route('/getProperty')
def getProperty():
    result = []
    for doc in propertyCollection.find():
        result.append({
        'id_user': doc['id_user'],  
        '_id':doc['_id'],
        'cityP':doc['cityP'],
        'countryP': doc['countryP'],
        'adressP': doc['adressP'],
        'ubication': doc['ubication'],
        'roomNumber': doc['roomNumber'],
        'imageP': doc['imageP'],
        'priceDay': doc['priceDay'],
        'Description': doc['Description']
    })
    username = session["user"]
    user = userCollection.find_one({'email': username})
    session['roll'] = user["roll"]
    if 'user' in session:
        return render_template("getProperty.html", propertyp = result, user = user["_id"])  
    else:
        return render_template("index.html")

@app.route('/getPropertyByIdUser/<id>')
def getPropertyByIdUser(id):
    property = propertyCollection.find_one({'id_user': ObjectId(id)})
    result = []
    mensaje = ""
    if property is None:
        return render_template("getProperty.html", mensaje = "El usuario no tiene ninguna propiedad asociada")    

    result.append({
        '_id':property['_id'],
        'cityP':property['cityP'],
        'countryP': property['countryP'],
        'adressP': property['adressP'],
        'ubication': property['ubication'],
        'roomNumber': property['roomNumber'],
        'imageP': property['imageP'],
        'priceDay': property['priceDay'],
        'Description': property['Description'],
        'listimage': property['listimage']
    })
    return render_template("getProperty.html", propertyp = result)        

#insertar propiedades en la base de datos
@app.route('/Addproperty', methods=["POST"])
def Addproperty():
        cityP = request.form.get('cityP')
        countryP = request.form.get('countryP')
        adressP = request.form.get('adressP')
        ubication = request.form.get('ubication')
        roomNumber = request.form.get('roomNumber')
        imageP = request.files['imageP']
        priceDay = request.form.get('priceDay')
        Description = request.form.get('Description')
        imageMain = request.files.getlist('imageMain[]')
        mainimage = imageP.filename
        imageP.save(os.path.join(app.config['UPLOAD_FOLDER'], mainimage))
        name_images =[]
        for image in imageMain:
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], image.filename))
            name_images.append(image.filename)
        username = session["user"]
        user = userCollection.find_one({'email': username}) 
        idUser = str(user['_id'])   
        insertProperty={'cityP': cityP, 'countryP': countryP, 'adressP': adressP, 'ubication': ubication, 'roomNumber': roomNumber, 'imageP': mainimage, 'priceDay': priceDay, 'Description': Description,'listimage':name_images,"id_user":user['_id'] }
        save = propertyCollection.insert_one(insertProperty)
        return redirect(url_for('getPropertyByIdUser', id = idUser))

#registrar nuevo usuario
@app.route('/sign_up', methods=["POST"])
def sign_up():
        name = request.form.get('name')
        lastname = request.form.get('lastname')
        email = request.form.get('email')
        country = request.form.get('country')
        city = request.form.get('city')
        password = request.form.get('password')
        roll = request.form.get('roll')
        inserUser = {'name':name, 'lastname':lastname, 'email':email, 'country':country, 'city':city, 'password':password, 'roll':roll}
        save = userCollection.insert_one(inserUser)
        return redirect(url_for('index'))
        

    
@app.route('/deleteP/<id>',methods=['GET'])
def deleteP(id):
        propertyCollection.delete_one({'_id': ObjectId(id)})
        username = session["user"]
        user = userCollection.find_one({'email': username})
        idUser = str(user['_id'])
        return redirect(url_for('getPropertyByIdUser', id = idUser))


#Consulta todos los datos de la propiedad y los pone en el formulario
@app.route('/editProperty/<id>')
def editProperty(id):
    property = propertyCollection.find_one({'_id': ObjectId(id)})
    result = []
    result.append({
        '_id':property['_id'],
        'cityP':property['cityP'],
        'countryP': property['countryP'],
        'adressP': property['adressP'],
        'ubication': property['ubication'],
        'roomNumber': property['roomNumber'],
        'imageP': property['imageP'],
        'priceDay': property['priceDay'],
        'Description': property['Description']
    })
    return render_template("editProperty.html",propertyp = result)

# Guarda los datos de la propiedad editada en la Base de datos
@app.route('/editDBProperty/<id>', methods=['POST'])
def editDBProperty(id):
        cityP = request.form.get('cityP')
        countryP = request.form.get('countryP')
        adressP = request.form.get('adressP')
        ubication = request.form.get('ubication')
        roomNumber = request.form.get('roomNumber')
        imageP = request.files['imageP']
        priceDay = request.form.get('priceDay')
        Description = request.form.get('Description')
        imageMain = request.files.getlist('imageMain[]')
        mainimage = imageP.filename
        imageP.save(os.path.join(app.config['UPLOAD_FOLDER'], mainimage))
        name_images =[]
        for image in imageMain:
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], image.filename))
            name_images.append(image.filename)
        propertyCollection.update_one({'_id': ObjectId(id)}, {"$set": {
            'cityP': cityP,
            'countryP': countryP,
            'adressP': adressP,
            'ubication': ubication,
            'roomNumber': roomNumber,
            'imageP': mainimage,
            'priceDay': priceDay,
            'Description': Description,
            'listimage': name_images
        }})
        return redirect(url_for('getProperty'))


#Hacer consulta para pintar datos del usuario en un formulario
@app.route('/editUser/<id>')
def editUser(id):
    userEd = userCollection.find_one({'_id': ObjectId(id)})
    result = []
    result.append({
        '_id':userEd['_id'],
        'name':userEd['name'],
        'lastname':userEd['lastname'],
        'email':userEd['email'],
        'country':userEd['country'],
        'city':userEd['city'],
        'password':userEd['password'],
        'roll':userEd['roll']
    })
    return render_template("editUser.html", user = result)

#Guardar datos de ususario editado en base de datos
@app.route('/editDBUser/<id>', methods=['POST'])
def editDBUser(id):
        name = request.form.get('name')
        lastname = request.form.get('lastname')
        email = request.form.get('email')
        country = request.form.get('country')
        city = request.form.get('city')
        password = request.form.get('password')
        roll = request.form.get('roll')
        userCollection.update_one({'_id': ObjectId(id)}, {"$set": {
            'name': name,
            'lastname': lastname,
            'email': email,
            'country': country,
            'city': city,
            'password': password,
            'roll': roll
        }})
        return redirect(url_for('getProperty'))

@app.route('/propertyByCity')
def propertyByCity():
   
  
    return render_template("propertyByCity.html") 
    # return render_template("propertyByCity.html", propertyc = result)

@app.route('/listpropertyByCity/<ciudad>')
def listpropertyByCity(ciudad):
    result = []
    for doc in propertyCollection.find({'cityP': ciudad}):
        result.append({
            '_id':doc['_id'],
            'cityP':doc['cityP'],
            'countryP': doc['countryP'],
            'adressP': doc['adressP'],
            'ubication': doc['ubication'],
            'roomNumber': doc['roomNumber'],
            'imageP': doc['imageP'],
            'priceDay': doc['priceDay'],
            'Description': doc['Description'],
            'id_user': doc['id_user']
    })
        return render_template('propertyByCity.html', propertyc = result)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True) #se genera el servidor loca