# How to Login with Facebook

At the first version of socialchef, we created a test page for FB login test.

## Configure /main/settings.py

* Ask John Hu to know the FB app id and secret id
* Update the following two settings:
```python
SOCIAL_AUTH_FACEBOOK_KEY = '{ask john hu}'
SOCIAL_AUTH_FACEBOOK_SECRET = '{ask john hu}'
```

## Create a [django-oauth-toolkit](https://django-oauth-toolkit.readthedocs.io/en/latest/) app

* Create superuser (if you haven't done it before): `python manage.py createsuperuser`
* Start the server: `python manage.py runserver`
* Open `http://localhost:8000/rest/login`
* Login and you will see a 404 or 400
* Open `http://localhost:8000/o/applications/`
* Create an app with the followings:
  * Client type: confidential
  * Authorization grant type: Resource owner password-based
  * leave others as default
* Collect `Client ID` and `Client Secret`

## Download and Enable ngrok

Since FB only supports `https` requests, we have to use ngrok to create an SSL server for us.

* Download ngrok from https://ngrok.com/
* Execute: `ngrok http 8000`
* Open https://developers.facebook.com/apps/1627966500734672/fb-login/settings/
* Add the ngrok https base URL to `Allowed Domains for the JavaScript SDK`

## Test FB Login
* Open https://{your ngrok url}/
* Click FBLogin
* Open Web Console to get the FB access token

## Obtain SocialChef token
* Use postman to POST http://localhost:8000/convert-token with form data:
  * client_id: _Client ID_ (collected previously)
  * client_secret: _Client Secret_ (collected previously)
  * backend: `facebook`
  * grant_type: `convert_token`
  * token: _FB access token_ (collected previously)
* Collect SocialChef `access_token` from response

## Test authentication
* Use postman to send a GET request to http://localhost:8000/test/
* Check the terminal to find: `user: AnonymousUser`
* Change postman Authorization Type to `Bearer Token`
* Fill the SocialChef `access_token` in Token field
* Send the GET request again
* Check the terminal to find: `user: {your FB email}`
