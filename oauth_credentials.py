class OauthInfo:

    class Neurio:

        client_id = 'sqiUUK77SI-9b80-0N0QCQ'
        client_secret = 'wi62EbkiRY2w9NDByGhj9g'
        callback_url = 'https://38.68.237.187:12346/oauth/neurio'
        oauth_entry = 'https://my.neur.io/v1/oauth2/authorize?response_type=token&client_id='+client_id + \
                  '&redirect_uri='+callback_url+'&state='
        token_request_url = 'https://api.neur.io/v1/oauth2/token'

    class SmartThings:

        client_id = '85946b71-d34c-46d1-a336-c34bd819ecc4'
        client_secret = '2c3b22d9-7dc7-4622-97d1-4ceb9d9ae7e3'
        callback_url = 'https://38.68.237.187:12346/oauth/smartthings'
        oauth_entry = 'https://graph.api.smartthings.com/oauth/authorize?response_type=code&client_id='+client_id + \
                  '&scope=app&redirect_uri='+callback_url+'&state='
        token_request_url = 'https://graph.api.smartthings.com/oauth/token'

    class Nest:

        client_id = '7d7a95b7-53a6-4a90-bee2-35c9a6947b60'
        client_secret = 'GElta8GxB9CEICAwM2zJGwGDO'
        callback_url = 'https://38.68.237.187:12346/oauth/nest'
        oauth_entry = 'https://home.nest.com/login/oauth2?client_id=' + client_id + '&state='
        token_request_url = 'https://api.home.nest.com/oauth2/access_token'

    class Harmony:

        client_id = 'SdaUZmjikFSbFpaJbiv87A'
        client_secret = '2Rgh5mKizXZrJnJs4KV7uOXIT-uvK1EEMQhPn1tBYAY'
        callback_url = 'https://38.68.237.187:12346/callback/harmony'
        oauth_entry = 'https://home.myharmony.com/oauth2/authorize?client_id=' + client_id + \
                      '&scope=remote&response_type=code&redirect_uri=https://www.bemcontrols.info/callback/harmony&state='
        # token_request_url = 'https://home.myharmony.com/oauth2/token?code=AUTHORIZATION_CODE&client_id='+client_id+\
        #                     '&client_secret='+client_secret+'&grant_type=authorization_code'
        token_request_url = 'https://home.myharmony.com/oauth2/token'
