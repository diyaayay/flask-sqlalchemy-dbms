from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests
from flask_wtf import FlaskForm
from wtforms import (StringField, TextAreaField, IntegerField, BooleanField,
                     RadioField)
from wtforms.validators import InputRequired, Length
myapikey ="d16d242a7fcb8546f6cedf5b14bb2d48"
appurl = "https://api.themoviedb.org/3/search/movie"
'''
Red underlines? Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'
db = SQLAlchemy()
db.init_app(app)


class Movie(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    title=db.Column(db.String(250),unique=False,nullable=False)
    year=db.Column(db.Integer,nullable=False)
    description=db.Column(db.String(250),nullable=False)
    rating=db.Column(db.Integer,nullable=True)
    ranking=db.Column(db.Integer,nullable=True)
    review = db.Column(db.String(250), nullable=True)
    img_url = db.Column(db.String(250), nullable=False)


with app.app_context():
    db.create_all()

# new_movie = Movie(
#     title="Phone Booth",
#     year=2002,
#     description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
#     rating=7.3,
#     ranking=10,
#     review="My favourite character was the caller.",
#     img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
# )
#
# with app.app_context():
#     db.session.add(new_movie)
#     db.session.commit()

class edform(FlaskForm):
    rating=IntegerField("Your Rating out of 10 eg:7 :")
    review=TextAreaField("Your Review")
    submit = SubmitField("Done")
class addform(FlaskForm):
    title = StringField("Movie Title", validators=[DataRequired()])
    submit = SubmitField("Add Movie")
@app.route("/")
def home():
    result=db.session.execute(db.select(Movie))
    all_movies=result.scalars()
    return render_template("index.html",movies=all_movies)

@app.route("/edit",methods=["GET", "POST"])
def editform():
    form=edform()
    movie_id = request.args.get("id")
    movie = db.get_or_404(Movie, movie_id)
    if form.validate_on_submit():
        movie.rating=int(form.rating.data)
        movie.review=form.review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html", movie=movie, form=form)


get_details_url="https://api.themoviedb.org/3/movie"





@app.route("/delete")
def delmovie():
    movie_id = request.args.get("id")
    movie = db.get_or_404(Movie, movie_id)
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for('home'))


@app.route("/add", methods=["GET", "POST"])
def addmovie():
    form = addform()

    if form.validate_on_submit():
        movie_title = form.title.data
        response = requests.get(appurl, params={"api_key": myapikey, "query": movie_title})
        data = response.json()["results"]

        return render_template("select.html", options=data)

    return render_template("add.html", form=form)


MOVIE_DB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"
@app.route("/find")
def find_movie():
    movie_api_id=request.args.get("id")
    if movie_api_id:
        find_details_by_id=f"{get_details_url}/{movie_api_id}"
        response=requests.get(url=find_details_by_id,params={"api_key": myapikey, "language": "en-US"})
        data=response.json()

        new_movie=Movie(
            title=data["title"],
            year = data["release_date"].split("-")[0],
            img_url=f"{MOVIE_DB_IMAGE_URL}{data['poster_path']}",
            description=data["overview"]

        )
        db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for("editform", id=new_movie.id))



if __name__ == '__main__':
    app.run(debug=True)
