from flask import g
from flask import Flask
from flask import request
from flask.views import MethodView

import utils as ut

app = Flask(__name__)

# @app.before_request
# def before_request():
#     pass
#     # g.seq_db = ut.connect_seq()

# @app.teardown_request
# def teardown_request(exception):
#     db = getattr(g, 'seq_db', None)
#     if db is not None:
#         db.close()

@app.route('/variation', methods=['GET'])
def get():
    units = request.args['units']
    sequences = request.args.get('sequences', None)
    return ut.compute_variation(units, sequences)


# @app.route('/variation', methods=['POST'])
# def post(self):
#     data = request.get_json() or request.form
#     if not data:
#         raise BadRequest()
#     units = data['units']
#     sequnces = request.get('sequences', None)
#     return ut.compute_variation(units, sequences)



if __name__ == '__main__':
    app.run()
