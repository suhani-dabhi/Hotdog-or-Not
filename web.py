from flask import Flask, render_template, request, jsonify
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("HUGGING_FACE_API_KEY")
# Store our url as API_URL
HOTDOG_URL = os.getenv("HUGGING_FACE_HOTDOG_URL")

GENERAL_URL = os.getenv("HUGGING_FACE_GENERAL_URL")


app = Flask(__name__)

def query(data, model_url):

    # The below code sends data to the API using "requests" library
    # POST - sending information 
    # API_URL - where the request is being sent
    # header - contains authorization token
    # data - the data or image being sent to HuggingFace
    # Whatever the API sent back as reply, is stored in response
    response = requests.post(model_url, headers={"Authorization": f"Bearer {API_KEY}", "Content-Type":"application/octet-stream",
        }, 
        data=data,
        )
    
    print("Model URL: ", model_url)
    print("Status: ", response.status_code)
    print("Body: ", response.text[:500])

    response.raise_for_status()
    # response is in bytes -- so decode() will convert it into string
    # then json.loads() will convert it into a python dictionary
    return response.json()

# down below -- when someone visits the localhost 5000 url, it will render 
# and return index.html 
@app.route('/')
def index():
    return render_template('index.html')



# down below - this route handles file upload 
@app.route("/upload_hotdog",methods=['POST'])

def upload_hotdog():
    
    #gets the file from the form
    file=request.files['file1']
    image_bytes = file.read()
    #passes the file to the query function
    results = query(image_bytes, HOTDOG_URL)
    top = max(results, key=lambda x: x["score"])


    #at this point, modeldata looks something like 
    #{'prediction": 'hotdog'}

    #this returns the dictionary into JSON so the frontend can recieve and display the results
    return render_template("index.html", 
            mode="Hotdog or Not Hotdog", 
            prediction = top["label"], 
            score = top["score"], 
            )


@app.route("/upload_general", methods = ["POST"])
def upload_general():
    
    if "file1" not in request.files:
        return "No file uploaded", 400

    file = request.files["file1"]

    if file.filename == "":
        return "Empty file", 400

    image_bytes = file.read()


    results = query(image_bytes, GENERAL_URL)
    top = max(results, key=lambda x: x["score"])
    if top["score"] < 0.5:
        prediction = "Sorry, we are not confident enough to classify the image :("
    else:
        prediction = top["label"]

    return render_template("index.html", 
            mode = "General Classifier", 
            prediction = top["label"], 
            score = top["score"],
            )


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)



