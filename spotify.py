import requests

class Spotify:

    def __init__(self, client_id, client_secret) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.generate_access_token()

    
    def generate_access_token(self):
        url = "https://accounts.spotify.com/api/token"
        
        payload = 'grant_type=client_credentials&client_id={0}&client_secret={1}'.format(self.client_id, self.client_secret)
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        response = requests.request("POST", url, headers=headers, data=payload)

        resp = response.json()

        if response.status_code != 200:
            print("request failed")
            print(response.status_code)
            return
    
        access_token = resp["access_token"]
        token_type = resp["token_type"]
        expires_in = resp["expires_in"]

        if response.status_code != 200:
            # todo 
            pass

        self.access_token = access_token

        return access_token, token_type, expires_in
    
    def get_track_features(self, trackId):
        headers = { 'Authorization': 'Bearer ' + self.access_token}
        response = requests.get('https://api.spotify.com/v1/audio-features/' + trackId, headers=headers)
        return response.json(), response.status_code
