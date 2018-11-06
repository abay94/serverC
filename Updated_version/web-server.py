# from sklearn.externals import joblib             #The scikit-learn version is 0.19.1.
from flask import Flask, jsonify, request, Response

app = Flask(__name__)

@app.route('/recieve_data', methods = ['POST'])

def apicall_two(responses2 = None):

    try:

        print('/model_hand')

    except Exception as e:

        raise e

    returning_data =100

    print(returning_data)

    return str(returning_data)


if __name__ == '__main__':
    #iniatialize()
    app.run(host="0.0.0.0", port=5003)








