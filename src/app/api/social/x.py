'''
Usiamo l'API rettiwt per ottenere dati da X aggirando i limiti dell'API free
Questo potrebbe portare al ban dell'account anche se improbabile, non usare l'account personale
Per farlo funzionare è necessario installare npm in un container docker ed installarlo con npm install -g rettiwt-api dopo essersi connessi al docker
https://www.npmjs.com/package/rettiwt-api
'''

import os
import json
import subprocess
from shutil import which
from app.api.core.social import SocialWrapper, SocialPost

class XWrapper(SocialWrapper):
    def __init__(self):
        '''
        This wrapper uses the rettiwt API to get data from X in order to avoid the rate limits of the free X API,
        even if improbable this could lead to a ban so do not use the personal account,
        In order to work a docker container with npm installed is needed, it's also necessary to install rettiwt in the container with npm install -g rettiwt-api
        '''
        # This is the list of users that can be interesting
        # To get the ID of a new user is necessary to search it on X, copy the url and insert it in a service like "https://get-id-x.foundtt.com/en/"
        self.users = [
            'watcherguru',
            'Cointelegraph',
            'BTC_Archive',
            'elonmusk'
        ]
        self.api_key = os.getenv("X_API_KEY")
        assert self.api_key, "X_API_KEY environment variable not set"
        '''
        # Connection to the docker deamon
        self.client = docker.from_env()
        # Connect with the relative container
        self.container = self.client.containers.get("node_rettiwt")
        '''
        assert which('rettiwt') is not None, "Command `rettiwt` not installed"
        self.social_posts: list[SocialPost] = []
    def get_top_crypto_posts(self, limit = 5) -> list[SocialPost]: #-> list[SocialPost]:
        '''
        Otteniamo i post più recenti da X, il limite si applica al numero di post per ogni utente nella lista interna
        '''
        social_posts: list[SocialPost] = []
        for user in self.users:
            # This currently doesn't work as intended since it returns the posts in random order
            # tweets = self.container.exec_run("rettiwt -k" + self.api_key + " tweet search -f " + str(user), tty=True)
            tweets = subprocess.run("rettiwt -k" + self.api_key + " tweet search -f " + str(user))
            tweets = tweets.output.decode()
            tweets = json.loads(tweets)
            tweets: list[dict] = tweets['list']
            tweets = tweets[:limit]
            for tweet in tweets:
                social_post = SocialPost()
                social_post.time = tweet['createdAt']
                social_post.title = str(user) + " tweeted: "
                social_post.description = tweet['fullText']
                social_posts.append(social_post)
        self.social_posts = social_posts
        return social_posts
    def print(self):
        i = 1
        for post in self.social_posts:
            print(f"Post {i}:")
            print(f"Time: {post.time}")
            print(f"Title: {post.title}")
            print(f"Description: {post.description}")
            print()
            i += 1

# x_wrapper = XWrapper()
# social_posts = x_wrapper.get_top_crypto_posts(limit=3)
# x_wrapper.print()