from app import app
from app import election_util
import app.election_util as election_util

if __name__ == '__main__':
    election_util.update_election_state()
    app.run(debug=True)

#Flask stuffs:
# set FLASK_APP=app.py
# set FLASK_DEBUG=1