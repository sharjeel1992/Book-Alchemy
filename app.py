from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import or_
from data_models import db, Author, Book
from datetime import datetime
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/jsk1992/PycharmProjects/Book Alchemy/data/library.sqlite'
db.init_app(app)


@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    """
    This method is for adding author to our database.It will first get the information from web form
    and pass it to the class Author to be added to the database table.General exception is added in case we
    encounter an error
    """
    if request.method == 'POST':
        name = request.form['name']
        birth_date = datetime.strptime(request.form['birth_date'], '%Y-%m-%d')
        date_of_death_str = request.form['date_of_death']
        date_of_death = datetime.strptime(date_of_death_str, '%Y-%m-%d') if date_of_death_str else None
        new_author = Author(name=name, birth_date=birth_date, date_of_death=date_of_death)
        try:
            db.session.add(new_author)
            db.session.commit()
            message = "Author added successfully"
        except Exception as e:
            db.session.rollback()
            message = f"Error: {e}"
        return render_template('add_author.html', message=message)
    return render_template('add_author.html')


def fetch_book_info(isbn):
    """
    This method is to get cover pic for the book title using an API.If there will be cover image
    it will be added to the database otherwise column will remain null
    """
    api_url = f'https://covers.openlibrary.org/b/isbn/{isbn}-M.jpg'
    response = requests.get(api_url)
    if response.status_code == 200:
        cover_image_url = response.url
    else:
        cover_image_url = None
    return cover_image_url


@app.route('/add_book', methods=['POST', 'GET'])
def add_book():
    """
    This method defines route for adding book to the database.Handles both post adnd get requests
    It will fetch data from web form and pass it to Book class.Exception is added to handle any error
    """
    if request.method == 'POST':
        isbn = request.form['isbn']
        title = request.form['title']
        publication_year = request.form['publication_year']
        author_id = request.form['author_id']
        cover_image = fetch_book_info(isbn)
        new_book = Book(title=title, isbn=isbn, publication_year=publication_year, author_id=author_id,
                        cover_image=cover_image)
        try:
            db.session.add(new_book)
            db.session.commit()
            message = "Book added successfully"
        except Exception as e:
            db.session.rollback()
            message = f"Error: {e}"
        return render_template('add_book.html', message=message)
    authors = Author.query.all()
    return render_template('add_book.html', authors=authors)


@app.route('/book/<int:book_id>/delete', methods=['POST'])
def delete_book(book_id):
    """
    This is for handling a delete option.It will check the book based on a book id and then delete
    the book.Also runs a check if author has any other book in the library if not, it will also delete
    the author from the database
    """
    book = Book.query.get(book_id)
    if book:
        author_id = book.author_id
        db.session.delete(book)
        db.session.commit()
        author_books = Book.query.filter_by(author_id=author_id).count()
        if author_books == 0:
            author = Author.query.get(author_id)
            if author:
                db.session.delete(author)
                db.session.commit()
        message = "Book deleted successfully."
    else:
        message = "Book not found."

    return redirect(url_for('home', message=message))


@app.route('/')
def home():
    """
    This is our homepage route.Enabled by sorting and searching options.
    """
    sort_by = request.args.get('sort_by', 'title')
    if sort_by not in ['title', 'author']:
        sort_by = 'title'
    search_query = request.args.get('search_query', '').strip()
    if search_query:
        books = Book.query.filter(or_(Book.title.like(f"%{search_query}%"),
                                      Author.name.like(f"%{search_query}%"))).join(Author).order_by(Book.title).all()
    else:
        if sort_by == 'title':
            books = Book.query.order_by(Book.title).join(Author).all()
        else:
            books = Book.query.order_by(Author.name, Book.title).join(Author).all()
    return render_template('home.html', books=books)


if __name__ == "__main__":
    app.run(debug=True)
