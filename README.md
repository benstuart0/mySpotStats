## mySpotStats

This is an web app to display a user's top tracks and artists from spotify. The end goal is to obtain data and give user analytics based off of their music interests.

### Instructions to Run Project:

##### Local
* Pull master
* pip3 install -r requirements.txt
* python3 -m flask run (this will run the service locally on http://127.0.0.1:5000/)

##### Remote
* change REDIRECT_URI in app.py
* commit all changes
* git push heroku master (http://myspotstats.herokuapp.com)

### Instructions to Edit Frontend:

* HTML and CSS code will go in the templates folder.

### TODO:

* Homepage (route: '/') needs to have a form that directs to any other page.
    * Two tiers of options: tracks & artists --> short_term, medium_term, & long_term
* Artist pages and track pages follow the same templates (artists.html & tracks.html)
