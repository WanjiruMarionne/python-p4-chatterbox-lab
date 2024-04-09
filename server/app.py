from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages', methods=['GET', 'POST'])
def messages():
    if request.method == 'GET':
        messages = Message.query.order_by(Message.created_at.asc()).all()
        
        response = make_response(jsonify([message.to_dict() for message in messages]), 200,)

    elif request.method == 'POST':
        request_info = request.get_json()
        message = Message(
            username = request_info['username'],
            body = request_info['body']
        )
        db.session.add(message)
        db.session.commit()

        response = make_response(jsonify(message.to_dict()), 201,)

    return response

@app.route('/messages/<int:id>', methods=['PATCH', 'DELETE'])
def messages_by_id(id):
    message = Message.query.filter_by(id=id).first()

    if message == None:
        response_message = {
            'message': f'Message {id} not found.'
        }
        return make_response(response_message, 404)

    if request.method == 'PATCH':
        request_info = request.get_json()
        for attr, value in request_info.items():
            setattr(message, attr, value)

        db.session.commit()

        response = make_response(jsonify(message.to_dict()), 200,)

    elif request.method == 'DELETE':
        db.session.delete(message)
        db.session.commit()
        
        response = make_response(jsonify({'deleted': True}), 200,)

    return response

if __name__ == '__main__':
    app.run(port=5555,debug=True)
