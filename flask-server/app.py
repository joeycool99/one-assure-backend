from flask import Flask, render_template, request,jsonify
from pymongo import MongoClient
import pandas as pd
from io import StringIO
import certifi
from flask_cors import CORS

# Connect to the local MongoDB instance
# client = MongoClient('mongodb://localhost:27017/')
# db = client['helth-insurace-project']  
# collection_csv = db['csv_data']


app=Flask(__name__)
CORS(app)
uri='mongodb+srv://joey_cool_one:Joey123@cluster0.gc8pm.mongodb.net/?retryWrites=true&w=majority'


client = MongoClient(uri, tlsCAFile=certifi.where())
db = client['helth-insurace-project']  
collection_csv = db['csv_data']



@app.route('/upload', methods=['POST'])
def upload_csv():
    file = request.files['file']

    if file.filename == '':
        return "No file selected"

    if file:
        csv_content = file.read().decode('utf-8')
        data = pd.read_csv(StringIO(csv_content))

        data_dict_list = data.to_dict(orient='records')
        collection_csv.insert_many(data_dict_list)

        return "CSV file uploaded and data inserted into MongoDB"



@app.route('/view')
def view():
    data = list(collection_csv.find())
    return render_template('view.html', data=data)




@app.route('/calculate_premium', methods=['POST'])
def calculate_total_premium():
    data = request.json
    ages = sorted(data["ages"], reverse=True)
    cover = int(data["cover"])
    price=[]
    discount=[0]

    total_premium = 0.0
    for idx, age in enumerate(ages):
        age_range = get_age_range(age)
        query = {"age_range": age_range, "member_csv": "1a"}
        cursor = collection_csv.find_one(query)
        
        if cursor:
            premium = cursor[str(cover)]
            price.append(premium)
            if idx > 0:
                premium=premium - (premium * 0.5)
                discount.append(premium)
            total_premium += premium
        else:
            return jsonify({"error": "Premium data not found for given input"}), 404
    return jsonify({"total_premium": total_premium,"price":price,"discount":discount})

def get_age_range(age):
    age_ranges = {
        (0, 18): "0-18",
        (18, 24): '18-24',
        (25, 35): '25-35',
        (36, 40): '36-40',
        (41, 45): '41-45',
        (46, 50): '46-50',
        (51, 55): '51-55',
        (56, 60): '56-60',
        (61, 65): '61-65',
        (66, 70): '66-70',
        (71, 75): '71-75',
        (76, 99): '76-99'
    }

    for age_range, label in age_ranges.items():
        if age_range[0] <= age <= age_range[1]:
            return label
    return None 

if __name__== "__main__":
    app.run( debug= True)