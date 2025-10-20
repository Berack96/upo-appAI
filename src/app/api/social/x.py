import os
import json
import subprocess
from shutil import which
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
        social_posts: list[SocialPost] = []

        for user in X_USERS:
            process = subprocess.run(f"rettiwt -k {self.api_key} tweet search -f {str(user)}", capture_output=True)
            results = process.stdout.decode()
            json_result = json.loads(results)

            tweets = json_result['list']
            for tweet in tweets[:limit]:
                social_post = SocialPost()
                social_post.time = tweet['createdAt']
                social_post.title = str(user) + " tweeted: "
                social_post.description = tweet['fullText']
                social_posts.append(social_post)

        return social_posts
