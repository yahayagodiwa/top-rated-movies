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


class Base(DeclarativeBase):
  pass

db = SQLAlchemy(model_class=Base) 

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///top-10-movies.db"
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)
db.init_app(app)

class Movies(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=False)
    ranking: Mapped[int] = mapped_column(Integer, nullable=False)
    review: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=True)
    
class MyForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    
with app.app_context():
    db.create_all()

class MovieForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    year = IntegerField('Year', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    rating = FloatField('Rating', validators=[
        DataRequired(),
        NumberRange(min=0, max=10, message="Rating must be between 0 and 10.")
    ])  
    ranking = IntegerField('Ranking', validators=[DataRequired()])
    review = StringField('Review', validators=[DataRequired()])
    img_url = StringField('Image URL', validators=[DataRequired()])
    submit = SubmitField('Submit')
    
class UpdateForm(FlaskForm):
    rating = FloatField('Rating', validators=[
        DataRequired(),
        NumberRange(min=0, max=10, message="Rating must be between 0 and 10.")
    ])
    review = StringField('Review', validators=[DataRequired()])
    submit = SubmitField('Update')
    
@app.route("/")
def home():
    movies = db.session.query(Movies).all()
    return render_template("index.html", movies = movies)

@app.route('/add', methods=['GET', 'POST'])
def add():
    movie_form = MovieForm()
    try:
        if movie_form.validate_on_submit():
            title = movie_form.title.data
            year = movie_form.year.data
            description = movie_form.description.data
            rating = movie_form.rating.data
            ranking = movie_form.ranking.data
            review = movie_form.review.data
            img_url = movie_form.img_url.data
            new_movie = Movies(title= title, year=year, description=description,
                            rating=rating, id=ranking, review=review, img_url=img_url)
            db.session.add(new_movie)
            db.session.commit()
            return redirect('/')
    except IntegrityError as e:
          flash("A movie with this title already exists. Please use a different title.")
          return redirect('/add')
    return render_template('add.html', form=movie_form)

@app.route('/edit/<int:index>', methods=['GET', 'POST'])
def edit(index):
     movie_to_update = Movies.query.get_or_404(index)
     update = UpdateForm()
     if update.validate_on_submit():
         movie_to_update.rating = update.rating.data
         movie_to_update.review = update.review.data
         db.session.commit()
         
         return redirect('/')
            
     return render_template('edit.html', update = update, movie = movie_to_update)
@app.route('/delete/<int:index>')
def delete(index):
    movie_to_delete = Movies.query.get(index)
    if movie_to_delete:
        db.session.delete(movie_to_delete)
        db.session.commit()
        movies = Movies.query.all()
        return render_template('index.html', movies = movies)

if __name__ == '__main__':
    app.run(debug=True)
