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
        msgs = Message.query.all()
        # msgs is a list of message objects
        # needs to be serialized to dict
        return [msg.to_dict() for msg in msgs], 200
    elif request.method == 'POST':
        # get the json data from request
        # build a new message object and save to db
        data = request.get_json()
        new_msg = Message(
            # .get() returns key or null if key doesn't exist. supports nested dicts or lists by chaining on .gets
            body=data.get('body'),
            username=data.get('username')
        )

        db.session.add(new_msg)
        db.session.commit()
    
    return new_msg.to_dict(), 201


@app.route('/messages/<int:id>', methods=['PATCH', 'DELETE'])
def messages_by_id(id):
    msg = Message.query.filter(Message.id == id).first()

    if msg is None:
        return {'error' : 'message not found'}, 404
    
    # we need to get the data from the request
    if request.method == 'PATCH':
        data = request.get_json()

        # just updating one field, doesn't need setattr()
        if 'body' in data:
            msg.body = data['body']

        db.session.add(msg)
        db.session.commit()

        return msg.to_dict(), 200
    elif request.method == 'DELETE':
        db.session.delete(msg)
        db.session.commit()

        return {}, 204

if __name__ == '__main__':
    app.run(port=5555)
