import numpy as np

def vote(voters):
    joined = voters[0]
    for i in range(1, len(voters)-1):
        joined = np.concatenate((joined, voters[i]), axis=1)
    ballot = []
    for votes in joined:
        ballot.append(max(set(votes), key=votes.count))
    return ballot
