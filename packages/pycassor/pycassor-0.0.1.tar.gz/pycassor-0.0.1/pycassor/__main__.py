
from flask import Flask, request
from flask_restful import Resource, Api

app = Flask('pycassor_suite')
api = Api(app)

class DosageSensitivityPlot(Resource):
    def get(self):
        return {'genes': [{'id':1, 'name':'BRIP1'},{'id':2, 'name':'BRCA1'}]} 

api.add_resource(DosageSensitivityPlot, '/dosage') # Route_1

if __name__ == '__main__':
     app.run(port=4444)
