import time
from flask import Flask, render_template, request, redirect, url_for, session, flash
import pymongo
from bson.objectid import ObjectId
import os
from bson import ObjectId
from pymongo.collation import CollationAlternate
from datetime import datetime

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
    if not session:
        return render_template("especificProperty.html", propertyp = result)
    username = session["user"]
    user = userCollection.find_one({'email': username})
    session['roll'] = user["roll"]
    if 'user' in session:
        return render_template("especificProperty.html", propertyp = result, user = user["_id"])  
    else: 
        return render_template("index.html")
    

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
    result = []
    mensaje = ""
    property = propertyCollection.find({'id_user': ObjectId(id)})
    if property is None:
        return render_template("getProperty.html", mensaje = "El usuario no tiene ninguna propiedad asociada")    
    for doc in property:
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
            'listimage': doc['listimage']
        })
    username = session["user"]
    user = userCollection.find_one({'email': username})    
    return render_template("getProperty.html", propertyp = result, user = user["_id"])        

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
        # state = request.form.get('state')
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
        insertProperty={'cityP': cityP, 'countryP': countryP, 'adressP': adressP, 'ubication': ubication, 'roomNumber': roomNumber, 'imageP': mainimage, 'priceDay': priceDay, 'Description': Description,'listimage':name_images,"id_user":user['_id'] , "state":"Disponible"}
        save = propertyCollection.insert_one(insertProperty)
        return redirect(url_for('getPropertyByIdUser', id = idUser))

#registrar nuevo usuario
@app.route('/sign_up', methods=["POST"])
def sign_up():
        name = request.form.get('name')
        lastname = request.form.get('lastName')
        email = request.form.get('email')
        country = request.form.get('country')
        city = request.form.get('city')
        password = request.form.get('password')
        roll = request.form.get('roll')
        inserUser = {'name':name, 'lastName':lastname, 'email':email, 'country':country, 'city':city, 'password':password, 'roll':roll}
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
        'lastName':userEd['lastName'],
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
        lastName = request.form.get('lastName')
        email = request.form.get('email')
        country = request.form.get('country')
        city = request.form.get('city')
        password = request.form.get('password')
        roll = request.form.get('roll')
        userCollection.update_one({'_id': ObjectId(id)}, {"$set": {
            'name': name,
            'lastName': lastName,
            'email': email,
            'country': country,
            'city': city,   
            'password': password,
            'roll': roll
        }})
        session.clear()
        return render_template('login.html')

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


@app.route('/ReserveProperty')
def ReserveProperty():
    return render_template("ReserveProperty.html") 

@app.route('/ReservePropertyByState/<id>')
def ReservePropertyByState(id):
    if 'user' in session:
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
            'listimage': property['listimage'],
            'state': property['state']
        })
        return render_template('ReserveProperty.html', propertyc = result)
    else:
        return render_template('login.html')

@app.route('/ReservePropertyById/<id>', methods=['POST'])
def ReservePropertyById(id):
    bandera = 0
    dateIni = request.form.get('dateIni')
    dateEnd = request.form.get('dateEnd')
    price = request.form.get('price')
    newDateIni =int(datetime.strptime(dateIni, '%Y-%m-%d').strftime('%y%m%d'))
    newDateEnd =int(datetime.strptime(dateEnd, '%Y-%m-%d').strftime('%y%m%d'))
    reserva = reservaCollection.find_one({'id_property':  ObjectId(id)})
    if reserva is not None:
        dateIniReserva = reserva['dateIni']
        dateEndReserva = reserva['dateEnd']
        if ((newDateIni >= dateIniReserva ) and (newDateEnd <= dateEndReserva) or (newDateIni >= dateIniReserva ) and (newDateIni <= dateEndReserva ) or (newDateEnd >= dateIniReserva) and (newDateEnd <= dateEndReserva)) and (reserva is not None):
            bandera = 1
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
                'listimage': property['listimage'],
                'state': property['state']
            })
            return render_template('ReserveProperty.html', propertyc = result, message = "Propiedad no disponible para estas fechas",switch = bandera)
        else:
            bandera = 0   
            property = propertyCollection.find_one({'_id':  ObjectId(id)})

            username = session["user"]
            user = userCollection.find_one({'email': username}) 
            insertReserve={'cityP': property['cityP'] ,'adressP': property['adressP'],  'roomNumber': property['roomNumber'], 'priceDay': property['priceDay'], "dateIni": newDateIni, "dateEnd": newDateEnd,"price":price,"id_user":user['_id'],'id_property': property['_id']}
            save = reservaCollection.insert_one(insertReserve)
            if save is not None:
                propertyCollection.update_one({'_id': ObjectId(id)}, {"$set": {
                    'state': 'No disponible'
                }})
            return redirect(url_for('HistoryReservePropertyById',id=id))
    else:
        bandera = 0   
        property = propertyCollection.find_one({'_id':  ObjectId(id)})

        username = session["user"]
        user = userCollection.find_one({'email': username}) 
        insertReserve={'cityP': property['cityP'] ,'adressP': property['adressP'],  'roomNumber': property['roomNumber'], 'priceDay': property['priceDay'], "dateIni": newDateIni, "dateEnd": newDateEnd,"price":price,"id_user":user['_id'],'id_property': property['_id']}
        save = reservaCollection.insert_one(insertReserve)
        if save is not None:
            propertyCollection.update_one({'_id': ObjectId(id)}, {"$set": {
                    'state': 'No disponible'
            }})
        return redirect(url_for('HistoryReservePropertyById',id=id))        

@app.route('/HistoryReserveProperty')
def HistoryReserveProperty():
    return render_template("HistoryReserveProperty.html") 

@app.route('/HistoryReservePropertyById/<id>')
def HistoryReservePropertyById(id):
    result = []
    for doc in reservaCollection.find({'id_property': ObjectId(id)}):
        result.append({
            '_id':doc['_id'],
            'cityP':doc['cityP'],
            'adressP': doc['adressP'],
            'roomNumber': doc['roomNumber'],
            'priceDay': doc['priceDay'],
            'id_user': doc['id_user'],
            'dateIni': doc['dateIni'],
            'dateEnd': doc['dateEnd'],
            'price': doc['price']
        })
    return render_template('HistoryReserveProperty.html', propertyc = result)    

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':    app.run(debug=True) #se genera el servidor loca