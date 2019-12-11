from mattermostdriver import Driver, exceptions

class BotManager():
    def __init__(self, token, host):
        #Authenticate with token
        self.mmDriver = Driver(options={
            'url'      : host,  
            'token'    : token,
            'scheme'   : 'http',   # Change to https if you need
            'port'     : 8065,
            'basepath' : '/api/v4',
            'verify'   : False,    # Chenge to True if you are using https
            'debug'    : False     
            } )
        self.mmDriver.login()
    
    def create_post(self, channel_id, message):
        post = self.mmDriver.posts.create_post(options={
            'channel_id': channel_id,
            'message'   : message 
            } )
        return post

    def get_user(self, username):
        return self.mmDriver.users.get_user_by_username(username)
    
    def get_channel_name(self, team_id, channel_name):
        for i in range(0,9):
            channel_replace = channel_name
            try:
                if(not i):
                    channel = self.mmDriver.channels.get_channel_by_name(team_id, channel_name)
                else:
                    channel_replace = channel_replace + str(-(i+1))
                    channel = self.mmDriver.channels.get_channel_by_name(team_id, channel_replace)
            except exceptions.ResourceNotFound as exc:
                return channel_replace      # This means that no channel was found so we can create it with that name
        
    
    def add_user_channel(self, channel_id, user_id, post_id):
        self.mmDriver.channels.add_user(channel_id, options={
            'user_id': user_id,
            'post_root_id': post_id } )

    def create_channel(self, channel_name, message, user_id, team): 
            channel_name = channel_name.replace(' ', '-')
            channel_name = self.get_channel_name(team, channel_name)
            chan = self.mmDriver.channels.create_channel(options={
                'team_id': team,
                'name': channel_name,
                'display_name': channel_name,
                'type': 'O'
                })
            post = self.create_post(chan['id'], message)
            self.add_user_channel(chan['id'], user_id, post['id'])


