from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Author(db.Model):
    """
    This is our Author class that defines the table author as db model and also add data to the database
    """
    __tablename__ = 'authors'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(db.Date)
    date_of_death = db.Column(db.Date)

    def __repr__(self):
        return f'<Author {self.name}>'


class Book(db.Model):
    """
    This is our book class that creates a table in the database and also add data to the table
    """
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    isbn = db.Column(db.String(20), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    publication_year = db.Column(db.Integer)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'), nullable=False)
    cover_image = db.Column(db.String(500))
    author = db.relationship('Author', backref='books')

    def __repr__(self):
        return f'<Book {self.title}>'

# with app.app_context():
#   db.create_all()
