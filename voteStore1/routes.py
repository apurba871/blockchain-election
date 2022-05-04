from voteStore1 import app, db
from flask import request
from voteStore1.models import Access, Share
import voteStore1.util as util

@app.route("/storeVote", methods=["POST"])
def store_vote():
  election_id = None
  # part_no = None
  share = None
  if "election_id" in request.args:
    election_id = request.args["election_id"]
  # if "part_no" in request.args:
  #   part_no = request.args["part_no"]
  if "share" in request.args:
    share = request.args["share"]
  
  # if election_id is None or part_no is None or share is None:
  if election_id is None or share is None:
    return {"success":False, "message":"Wrong parameters passed"}
  else:
    util.store_vote_helper(election_id, share)
    return {"success":True}
  
@app.route("/getVote", methods=["POST"])
def get_vote():
  if "election_id" in request.args:
    election_id = request.args["election_id"]
    if Access.is_present(election_id):
      if Access.get_has_access(election_id):
        share = util.get_vote_helper(election_id)
        return {"success":True, "election_id": election_id, "share":share.share}
      else:
        return {"success":False, "message":"Access not granted"}
    else:
      return {"success":False, "message":"No record exists"}
  else:
    return {"success":False, "message":"Wrong parameters passed"}

@app.route("/grantAccess", methods=["POST"])
def grant_access():
  username = None
  password = None
  election_id = None
  if "username" in request.args:
    username = request.args["username"]
  if "password" in request.args:
    password = request.args["password"]
  if "election_id" in request.args:
    election_id = request.args["election_id"]
  print(username, password, election_id)
  if username is None or password is None or election_id is None:
    return {"success":False, "message":"Wrong parameters recieved"}
  elif not Access.is_present(election_id):
    return {"success":False, "message":"No record exists"}
  elif username == "admin" and password == "password":
    access_obj = Access.getRecord(election_id)
    access_obj.has_access = True
    db.session.commit()
    return {"success":True, "message":"Access granted"}
  else:
    return {"success":False, "message":"Invalid credentials"}
