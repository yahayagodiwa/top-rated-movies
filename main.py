from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from sqlalchemy import Integer, String, Float
from wtforms import StringField, SubmitField, FloatField, IntegerField
from wtforms.validators import DataRequired, NumberRange
from sqlalchemy.exc import IntegrityError
from flask import flash
import requests



class Base(DeclarativeBase):
  pass

db = SQLAlchemy(model_class=Base) 

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///top-10-movies.db"
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)
db.init_app(app)

#--------------------------------- MOVIE DATABASE MODEL -------------------------------------#

class Movies(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(500), unique=True, nullable=False)
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String(500), nullable=True)
    img_url = db.Column(db.String(500), nullable=True)
    
with app.app_context():
    db.create_all()

#--------------------------------- ADD MOVIE FORM -------------------------------------#

class MovieForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    submit = SubmitField('Submit')
    
#--------------------------------- UPDATE MOVIE FORM -------------------------------------#
    
class UpdateForm(FlaskForm):
    rating = FloatField('Rating', validators=[
        DataRequired(),
        NumberRange(min=0, max=10, message="Rating must be between 0 and 10.")
    ])
    review = StringField('Review', validators=[DataRequired()])
    submit = SubmitField('Update')
    
    
#--------------------------------- HOME ROUTE -------------------------------------#
    
@app.route("/")
def home():
    movies = Movies.query.order_by(Movies.rating.desc()).all()
    return render_template("index.html", movies = movies)

#--------------------------------- ADD MOVIE ROUUTE -------------------------------------#

@app.route('/add', methods=['GET', 'POST'])
def add():
    movie_form = MovieForm()
    data = None
    try:
        if movie_form.validate_on_submit():
          title = movie_form.title.data
          url = f"https://api.themoviedb.org/3/search/movie?query={title}&include_adult=false&language=en-US&page=1"

          headers = {
    "accept": "application/json",
    "Authorization": "Bearer YOUR TOKEN"
          }

          response = requests.get(url, headers=headers)
          data = response.json().get('results', [])
          print(data)
          return render_template('select.html', data=data)
    except NameError as e:
        flash(f"Error fetching movie data: {e}", 'danger')
        print(e)
        return render_template('add.html', form=movie_form)
    return render_template('add.html', form=movie_form, data = data)

#--------------------------------- EDIT MOVIE ROUUTE -------------------------------------#

@app.route('/edit/<int:index>', methods=['GET', 'POST'])
def edit(index):
    try:
        movie_to_update = Movies.query.get_or_404(index)
        update = UpdateForm()
        
       
        if update.validate_on_submit():
            movie_to_update.rating = update.rating.data
            movie_to_update.review = update.review.data
            db.session.commit()
            
            return redirect('/')
    except IntegrityError as e:
        flash(f"Database Integrity Error: {e}", 'danger')
        db.session.rollback() 
        return redirect(url_for('home'))
    return render_template('edit.html', update = update, movie = movie_to_update)


#--------------------------------- ADD MOVIE ROUUTE -------------------------------------#
 
@app.route('/delete/<int:index>')
def delete(index):
    movie_to_delete = Movies.query.get(index)
    if movie_to_delete:
        db.session.delete(movie_to_delete)
        db.session.commit()
    movies = Movies.query.all()
    return render_template('index.html', movies = movies)

#--------------------------------- SELECTED MOVIE ROUUTE -------------------------------------#

@app.route('/selected/<int:id>')
def select(id):
   base_image_url = "https://image.tmdb.org/t/p/w500"
   try:
        url = f"https://api.themoviedb.org/3/movie/{id}?language=en-US"

        headers = {
        "accept": "application/json",
        "Authorization": "Bearer YOUR TOKEN"
        }

        response = requests.get(url, headers=headers)
        data = response.json()
        
        new_movie = Movies(
            id = data['id'],
            title = data['original_title'],
            img_url = f"{base_image_url}{data.get('poster_path')}" if data.get('poster_path') else None,
            year = data['release_date'][:4],
            description = data['overview'],
        )
        db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for('edit', index = id))
        
   except ConnectionError as e:
       print(e)
      
      
      
#---------------------------------  RUN FLASK -------------------------------------#
       
if __name__ == '__main__':
    app.run(debug=True)
