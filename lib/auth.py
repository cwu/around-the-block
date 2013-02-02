from flask import session
import models as m

def get_user():
  if 'user_id' not in session:
    return None
  return m.User.query.filter(m.User.id==session['user_id']).first()
