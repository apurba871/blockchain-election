from datetime import datetime
import requests

def update_election_state():
    from app import db
    from app.models import Election
    from datetime import datetime
    elections = Election.query.all()
    for election in elections:
        if election.election_state == 'counting_finished':
            continue
        elif election.start_date <= datetime.now() <= election.end_date:
            election.election_state = 'ongoing'
        elif datetime.now() < election.start_date:
            election.election_state = 'upcoming'
        elif datetime.now() > election.end_date and election.results_published == False:
            election.election_state = 'over'
        elif datetime.now() > election.end_date and election.results_published == True:
            election.election_state = 'past'
    db.session.commit()
    print("Election states updated at", datetime.now())

def get_new_election_id():
    from app import db
    from app.models import Election
    last_record = Election.getLastElectionRecord()
    numeric_id = int(0 if last_record is None else last_record.election_id[1:])
    return f'E{numeric_id+1}'

def get_new_candidate_id(election_id):
    from app import db
    from app.models import CandidateList
    return (0 if CandidateList.getLastCandidateRecord(election_id) is None else CandidateList.getLastCandidateRecord(election_id).id) + 1

def validate_cin(cin):
    from app.models import Voter
    user = Voter.query.filter_by(cin=cin).first()
    if user:
        return False
    else:
        return True

def validate_email(email):
    from app.models import Voter
    user = Voter.query.filter_by(email=email).first()
    if user:
        return False
    else:
        return True

def validateFields(cin, name, dept, join_year, is_admin, email, password, existence=True):
    import validators
    field_errors = []
    if cin == '':
        field_errors.append({'name':'cin', 'status':'Please fill out this field.'})
    elif existence and not validate_cin(cin):
        field_errors.append({'name':'cin', 'status':'CIN already in use. Please enter a different one.'})

    if name == '':
        field_errors.append({'name':'name', 'status':'Please fill out this field.'})
    elif not validators.length(name, min=3, max=255):
        field_errors.append({'name':'name', 'status':'Name length not between 3 and 255'})
    
    if dept == '':
        field_errors.append({'name':'dept', 'status':'Please select a department.'})
    
    if join_year == '':
        field_errors.append({'name':'join_year', 'status':'Please fill out this field.'})
    elif not join_year.isdecimal():
        field_errors.append({'name':'join_year', 'status':'Joining year should be a number'})
    elif not validators.between(int(join_year), min=2016, max=int(datetime.now().strftime("%Y"))):
        field_errors.append({'name':'join_year', 'status':'Joining year should be between 2016 and 2020'})
    
    if is_admin == '':
        field_errors.append({'name':'is_admin', 'status':'Please select an admin right.'})
    
    if email == '':
        field_errors.append({'name':'email', 'status':'Please fill out this field.'})
    elif existence and not validate_email(email):
        field_errors.append({'name':'email', 'status':'This email is already taken. Please enter a new one.'})
    elif not validators.email(email):
        field_errors.append({'name':'email', 'status':'Please enter a valid email.'})
    
    if password == '':
        field_errors.append({'name':'password', 'status':'Please fill out this field.'})

    return field_errors

def transform_vote(election_id, candidate_id):
    from app.models import Voter_List
    voter_count = len(Voter_List.getVotersInList(election_id))
    max_dig = len(str(voter_count))
    return 10 ** (max_dig * (candidate_id - 1))

def encrypt_vote(election_id, t_vote):
    import app.paillier_utils as paillier_utils
    from app.models import Election
    election_record = Election.getElectionRecord(election_id)
    (cipher_text, exp) = paillier_utils.encrypt_value(election_record.public_key, t_vote)
    return cipher_text, exp 

def create_shares(election_id, candidate_id):
    from secretsharing import SecretSharer
    from phe import paillier
    from phe.util import int_to_base64, base64_to_int
    t_vote = transform_vote(election_id, candidate_id)
    cipher_text, exp = encrypt_vote(election_id, t_vote)
    print("cipher_text -",base64_to_int(cipher_text))
    shares = SecretSharer.split_secret(str(base64_to_int(cipher_text)), 2, 3)
    return shares, exp

def combine_shares(shares):
    from secretsharing import SecretSharer
    return SecretSharer.recover_secret(shares)

def save_shares(election_id, candidate_id):
    urls = ["http://127.0.0.1:5100", "http://127.0.0.1:5200", "http://127.0.0.1:5300"]
    end_point = "/storeVote"
    shares, exp = create_shares(election_id, candidate_id)
    results = []
    for url, share in zip(urls, shares):
        r = requests.post(url+end_point, 
                    params={'election_id': election_id, 'exponent': exp, 'share':share})
        results.append(r.json())
    print(results)

# {   
#     "success":True, 
#     "election_id": election_id, 
#     "exponent":exponent, 
#     "shares":[
#           {'id': s.share_id, 'share': s.share},
#           {'id': s.share_id, 'share': s.share},
#           .... 
#       ]
# }

def parse_shares(results):
    from phe import paillier
    from phe.util import int_to_base64, base64_to_int
    shares = []
    for result in results:
        shares.append([item['share'] for item in sorted(result["shares"], key=lambda d: d['id'])])
    # shares1 = [item['share'] for item in sorted(results[0]["shares"], key=lambda d: d['id'])]
    # shares2 = [item['share'] for item in sorted(results[1]["shares"], key=lambda d: d['id'])] 
    # shares3 = [item['share'] for item in sorted(results[2]["shares"], key=lambda d: d['id'])]
    # encrypted_votes = [int_to_base64(int(combine_shares(list(share)))) for share in zip(shares1, shares2, shares3)]
    encrypted_votes = [int_to_base64(int(combine_shares(list(share)))) for share in zip(*shares)]
    return encrypted_votes

def get_all_combined_votes(election_id):
    urls = ["http://127.0.0.1:5100", "http://127.0.0.1:5200", "http://127.0.0.1:5300"]
    end_point = "/getVotes"
    results = []
    for url in urls:
        r = requests.post(url+end_point, 
                        params={'election_id': election_id})
        results.append(r.json())
    count_success = 0
    for result in results:
        if result["success"]:
            count_success += 1

    if count_success < 2:
        return "access_denied"
    else:
        return parse_shares([result for result in results if result["success"] == True]), results[0]["exponent"]

# Where votes is a list of encrypted votes
def count_and_return_encrypted_total(votes, exp, election_id):
    import app.paillier_utils as paillier_utils
    from app.models import Election
    election_record = Election.getElectionRecord(election_id)
    total = None
    for vote in votes:
        pailier_obj = paillier_utils.convert_to_paillier_obj(vote, exp, election_record.public_key)
        if total is None:
            total = pailier_obj
        else:
            total = total + pailier_obj
    return paillier_utils.paillier_obj_to_tuple(total)

# Returns results as [{"id": 1, "votes_recieved": 3}, {"id": 2, "votes_recieved": 4}, ...]
def get_results(encrypted_count, exponent, election_id, private_key):
    import app.paillier_utils as paillier
    from app.models import Election
    election_record = Election.getElectionRecord(election_id)
    decrypted_count = paillier.decrypt_value(private_key, election_record.public_key, encrypted_count, exponent)
    counts = []
    temp = decrypted_count
    from app.models import Voter_List
    voter_count = len(Voter_List.getVotersInList(election_id))
    max_dig = len(str(voter_count))
    divisor = (10 ** max_dig)
    candidate_id = 1
    while temp != 0:
        counts.append({"id":candidate_id, "votes_recieved":temp % divisor})
        temp //= divisor
        candidate_id += 1
    return counts

def save_results_in_db(private_key, election_id):
    # results = get_results(encrypted_count, )
    from app import db
    from app.models import Result
    for result in results:
        new_result = Result(election_id=election_id, candidate_id=result["id"], total_votes=result["votes_recieved"])
        db.session.commit()

if __name__ == "__main__":
    import json
    import app.paillier_utils as paillier
    # print(get_new_election_id())
    # save_shares('E1', 1)
    # save_shares('E1', 1)
    # save_shares('E1', 1)
    # save_shares('E1', 2)
    # save_shares('E1', 2)
    # save_shares('E1', 3)
    election_id = "E1"
    votes, exponent = get_all_combined_votes('E1')
    print(votes, exponent)
    result = count_and_return_encrypted_total(votes, exponent, 'E1')
    if result == "access_denied":
        print("Make sure to grant access to atleast two observer nodes to start counting process")
    else:
        encrypted_count, exponent = result
        print("encrypted_count -", encrypted_count)
        private_key = json.dumps({
            "kty": "DAJ",
            "key_ops": [
                "decrypt"
            ],
            "p": "yjs7b-IvT_5aeM1P0cQfrPMQ4ZY7NOUhLjOTQU6SuJbEbkbSH8XoxqgDfcfa0YCn9qGOexvCuB1Xc2bYwsxh6FzaQvIOLsohMUP7Xf-2zPlaH5v7aVrmjNCcm6xehoe1WypGPay_ML_89ip1RbLCO39dXTN9AuCHwbVuPZiOqNc",
            "q": "0H1G7Ts4tdU8GXyFIxgjy5epddQ_8lxJNx2C5nG2ANmeA8CJUUpE5Y17NMSY4wCwmDem2yKaFf8ZSKatIbXTd7NZbFieFP85V-8xM6CX-SHkzgquBgDX7vkLPUy_VfymJjnVDrAyNhe1ncI9-l1HqRTpgi4GRLz7CnV30y3i2Os",
            "kid": "Paillier private key generated by phe on 2022-05-05T01:06:49"
        })
        from app.models import Election
        election_record = Election.getElectionRecord(election_id)
        decrypted_count = paillier.decrypt_value(private_key, election_record.public_key, encrypted_count, exponent)
        print(decrypted_count)
        counts = []
        print("Individual Counts")
        temp = decrypted_count
        from app.models import Voter_List, CandidateList
        voter_count = len(Voter_List.getVotersInList(election_id))
        max_dig = len(str(voter_count))
        divisor = (10 ** max_dig)
        while temp != 0:
            counts.append(temp % divisor)
            temp //= divisor
        print(counts)