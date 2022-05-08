// SPDX-License-Identifier: MIT
// Solidity program
// to store
// casted vote  Details
pragma solidity ^0.6.0;

// Creating a Smart Contract
contract CastVotes	{

	// Structure of casted vote
	struct CastedVote{
		// State variables
		int voter_id;
		string election_id;
	}

CastedVote []cvotes;

// Function to add
// vote cast details
function addCastedVote( int voter_id, string memory election_id) public {
	CastedVote memory c =CastedVote(voter_id, election_id);
	cvotes.push(c);
}

function compareStrings(string memory a, string memory b) public pure returns (bool) {
  return (keccak256(abi.encodePacked((a))) == keccak256(abi.encodePacked((b))));
}

function countCastedVotes(string memory election_id) public view returns(uint){
	uint i;
	uint count = 0;
	for(i = 0; i < cvotes.length; i++){
		CastedVote memory c = cvotes[i];
		if(compareStrings(election_id, c.election_id)){
			count++;
		}
	}
	return count;
}

// Function to get
// details of the casted vote
function getCastedVote(int voter_id, string memory election_id) public view returns(string memory){
	uint i;
	for(i=0;i<cvotes.length;i++)
	{
		CastedVote memory c
			=cvotes[i];
		
		// Looks for a matching
		// voter_id and election_id
		if(compareStrings(election_id, c.election_id) && c.voter_id==voter_id)
		{
				return("found");
		}
	}
	
	// If provided employee
	// id is not present
	// it returns Not
	// Found
	return("not found");
}
}
