SESSIONS = {}

def get_session(session_id):

    if session_id not in SESSIONS:
        SESSIONS[session_id] = []
    return SESSIONS[session_id]