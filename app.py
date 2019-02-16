from flask import Flask, jsonify, abort, make_response, request

app = Flask(__name__)

# @app.route('/getname/<string:name>', methods=['POST'])
# def greet(name):
#     result = { "greeting": 'hello {}'.format(name) }
#     return make_response(jsonify(result))

# @app.route('/getname/<string:name>', methods=['GET'])
@app.route('/getname', methods=['GET', 'POST'])
def greet():

    # name= request.form['namae']
    name="satoru"

    # result = { "greeting": 'hello{}'.format(name) }
    result = { "greeting": 'hello{}'.format(name)}
    return make_response(jsonify(result))

# エラーハンドリング
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0')
