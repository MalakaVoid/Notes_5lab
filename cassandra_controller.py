import uuid

from cassandra.cluster import Cluster
from datetime import *

cluster = Cluster()
session = cluster.connect('db0')

def login_user(username, password):
    result = session.execute(f"SELECT user_id, username, password FROM user_by_username WHERE username = '{username}'")
    user = result.one()
    if user is not None:
        if user.password == password:
            return user.user_id
        return 500
    return 404


def register_user(username, password):
    result = session.execute(f"SELECT user_id, username, password FROM user_by_username WHERE username = '{username}'")
    user = result.one()
    if user is None:
        try:
            result = session.execute(f"INSERT INTO user_by_username(user_id, username, password)"
                                     f"VALUES ({uuid.uuid4()}, '{username}', '{password}')")
        except Exception as ex:
            print(ex)
            return 404
        return 200
    return 500


def get_user_notes(user_id):
    result = session.execute(f"SELECT note_id, title, text FROM notes_by_user_id WHERE user_id = {user_id}")
    return result.all()


def add_note(title, text, user_id):
    try:
        metadata_id = uuid.uuid4()
        session.execute(f"INSERT INTO note_metadata(metadata_id, creation_date, updation_date)"
                        f"VALUES ({metadata_id}, '{datetime.now()}', '{datetime.now()}')")

        session.execute(f"INSERT INTO notes_by_user_id(note_id, title, text, user_id, metadata_id) "
                        f"VALUES ({uuid.uuid4()}, '{title}', '{text}', {user_id}, {metadata_id})")
    except Exception as ex:
        print(ex)
        return 404
    return 200

def edit_note(title, text, user_id):
    try:
        tmp1 = session.execute(f"SELECT note_id, title FROM notes_by_user_id WHERE user_id = {user_id}")
        tmp2 = tmp1.all()
        note_id = ''
        for each in tmp2:
            if each.title == title:
                note_id = each.note_id
        session.execute(f"UPDATE notes_by_user_id SET text = '{text}' WHERE note_id = {note_id}")
    except Exception as ex:
        print(ex)

def get_preset(note_id, user_id):
    result = session.execute(f"SELECT preset_id, note_id, font_size, is_italic, is_bold, color, font FROM presets_by_note_id WHERE note_id = {note_id}")
    return result.one()



def get_note_id_by_title(user_id, title):
    result = session.execute(f"SELECT note_id, title FROM notes_by_user_id WHERE user_id = {user_id}")
    note_id = ''
    for each in result.all():
        if each.title == title:
            note_id = each.note_id
    return note_id

def create_preset(note_id, font_size, is_italic, is_bold, color, font):
    result = session.execute(f"SELECT * FROM presets_by_note_id WHERE note_id = {note_id}")
    if result.one() is None:
        try:
            session.execute(f"INSERT INTO presets_by_note_id(preset_id, note_id, font_size, is_italic, is_bold, color, font)"
                            f" VALUES ({uuid.uuid4()}, {note_id}, {font_size}, {is_italic}, {is_bold}, '{color}', '{font}')")
        except Exception as ex:
            print(ex)
    else:
        try:
            session.execute(f"UPDATE presets_by_note_id SET"
                            f" font_size = {font_size}, is_italic = {is_italic}, is_bold = {is_bold}, color = '{color}', font = '{font}'")
        except Exception as ex:
            print(ex)

def get_note_metadata(note_id):
    metadata_id = session.execute(f"SELECT metadata_id FROM notes_by_user_id WHERE note_id={note_id}").one().metadata_id
    result = session.execute(f"SELECT * FROM note_metadata WHERE metadata_id = {metadata_id}")
    return result.one()

def edit_note_title(title, note_id):
    session.execute(f"UPDATE notes_by_user_id SET title = '{title}' WHERE note_id = {note_id}")

def delete_note(note_id):
    session.execute(f"DELETE FROM notes_by_user_id WHERE note_id = {note_id}")