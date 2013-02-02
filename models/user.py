from sqlalchemy import Column, Integer, String
from db import Base

class User(Base):
  __tablename__ = 'users'

  id              = Column(Integer, primary_key = True)
  name            = Column(String)
  fb_uid          = Column(String)
  fb_access_token = Column(String)
  fs_uid          = Column(String)
  fs_access_token = Column(String)

  def __repr__(self):
    return "<User('%s', '%s', fbuid %s)>" % (self.id, self.name, self.fb_uid)
