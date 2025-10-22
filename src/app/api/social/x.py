import os
import json
import subprocess
from shutil import which
from datetime import datetime
from app.api.core.social import SocialWrapper, SocialPost


# This is the list of users that can be interesting
# To get the ID of a new user is necessary to search it on X, copy the url and insert it in a service like "https://get-id-x.foundtt.com/en/"
X_USERS = [
    'watcherguru',
    'Cointelegraph',
    'BTC_Archive',
    'elonmusk'
]

class XWrapper(SocialWrapper):
    def __init__(self):
        '''
        This wrapper uses the rettiwt API to get data from X in order to avoid the rate limits of the free X API,
        even if improbable this could lead to a ban so do not use the personal account,
        In order to work it is necessary to install the rettiwt cli tool, for more information visit the official documentation at https://www.npmjs.com/package/rettiwt-api
        '''

        self.api_key = os.getenv("X_API_KEY")
        assert self.api_key, "X_API_KEY environment variable not set"
        assert which('rettiwt') is not None, "Command `rettiwt` not installed"


    def get_top_crypto_posts(self, limit:int = 5) -> list[SocialPost]:
        posts: list[SocialPost] = []

        for user in X_USERS:
            cmd = f"rettiwt -k {self.api_key} tweet search {limit} -f {str(user)}"
            process = subprocess.run(cmd, capture_output=True, shell=True)
            results = process.stdout.decode()
            json_result = json.loads(results)

            for tweet in json_result.get('list', []):
                time = datetime.fromisoformat(tweet['createdAt'])
                social_post = SocialPost()
                social_post.set_timestamp(timestamp_s=int(time.timestamp()))
                social_post.title = f"{user} tweeted: "
                social_post.description = tweet['fullText']
                posts.append(social_post)

        return posts
