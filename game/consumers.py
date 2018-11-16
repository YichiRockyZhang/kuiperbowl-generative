from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from channels import Group
from channels.sessions import channel_session
from .models import *
import json
import datetime
import hashlib
import random

@channel_session
def ws_connect(message):
    # get room
    prefix, label = message['path'].strip('/').split('/')
    room = Room.objects.get(label=label)
    Group('game-'+label).add(message.reply_channel)
    message.reply_channel.send({"accept":True})
    message.channel_session['room'] = room.label

@channel_session
def ws_receive(message):
    # get message
    label = message.channel_session['room']
    room = Room.objects.get(label=label)
    data = json.loads(message['text'])

    # determine request type
    if(data['request_type'] == 'ping'):
        # update ping
        update_time_state(room)
        message.reply_channel.send(get_response_json(room))

    elif(data['request_type'] == 'new_user'):
        # new user
        m = hashlib.md5()
        m.update((label + str(room.players.count())).encode("utf8"))
        player_id = int(m.hexdigest(), 16) % 1000000
        p = Player(player_id=player_id, name="Jerry", score=0, locked_out=False, room=room)
        p.save()

        message.reply_channel.send({'text':json.dumps({
            "response_type":"new_user",
            "player_id":p.player_id,
            "player_name":p.name,
        })})

    elif(data['request_type'] == 'set_name'):
        # update name
        p = Player.objects.get(player_id=int(data['player_id']))
        p.name = data['content']
        p.save()

        Group('game-'+label).send(get_response_json(room))

    elif(data['request_type'] == 'next'):
        # next question
        update_time_state(room)
        if room.state == 'idle':
            questions = Question.objects.all()
            q = random.choice(questions)

            room.state = 'playing'
            room.start_time = datetime.datetime.now().timestamp()
            room.end_time = room.start_time + q.duration
            room.current_question = q
            room.save()

            Group('game-'+label).send(get_response_json(room))

    elif(data['request_type'] == 'buzz_init'):
        # buzz init
        if room.state == 'playing':
            room.state = 'contest'
            room.buzz_player = room.players.get(player_id=data['player_id'])
            room.buzz_start_time = datetime.datetime.now().timestamp()
            room.save()

            Group('game-'+label).send(get_response_json(room))

    elif(data['request_type'] == 'buzz_answer'):
        # buzz answer
        if room.state == 'contest':

            # evaluate answer here!!!!!!!!!!!!!!!!!!!!!!!!!!!

            buzz_duration = datetime.datetime.now().timestamp() - room.buzz_start_time
            room.state = 'playing'
            room.start_time += buzz_duration
            room.end_time += buzz_duration
            room.save()

            Group('game-'+label).send(get_response_json(room))

    elif(data['request_type'] == 'get_answer'):
        if room.state == 'idle':
            Group('game-'+label).send({'text':json.dumps({
                "response_type":"send_answer",
                "answer":room.current_question.answer,
            })});

@channel_session
def ws_disconnect(message):
    label = message.channel_session['room']
    Group('chat-'+label).discard(message.reply_channel)

# Helper methods

def update_time_state(room):
    """Checks time and updates state"""
    if(datetime.datetime.now().timestamp() >= room.end_time):
        room.state = 'idle'
        room.save()

def get_response_json(room):
    """Generates json for update response"""

    return {'text':json.dumps({
        "response_type":"update",
        "game_state":room.state,
        "current_time":datetime.datetime.now().timestamp(),
        "start_time":room.start_time,
        "end_time":room.end_time,
        "buzz_start_time":room.buzz_start_time,
        "current_question_content": room.current_question.content if room.current_question != None else "",
        "category":room.current_question.category if room.current_question != None else "",
        "scores":room.get_scores(),
    })}
