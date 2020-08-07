from flask import Flask, render_template, url_for, request, flash
import db, os.path

#Set up path
app = Flask(__name__, instance_relative_config=True)
app.config.from_mapping(
    SECRET_KEY='dev',
    DATABASE=os.path.join(app.instance_path, 'script.sqlite'),
)
#Set up and initialize the application
def setApp(conn=None):
    if conn is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(conn)
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    db.initialize_app(app)
    return app

db.initialize_app(app)
#Route for the home page.
#Connects to the database and selects items that are already saved.
@app.route('/')
@app.route('/home')
def index():
    conn = db.conn_db()
    items = conn.execute(
        'SELECT * FROM list'
    ).fetchall()
    return render_template('home.html', items=items)

#Delete items that user selects
#Remove it from the database
@app.route('/delete/<int:id>', methods=('GET', 'POST'))
def delete(id):
    #GET the correct items based on item id
    if request.method == 'GET':
        conn = db.conn_db()
        get = conn.execute(
            'SELECT * FROM list WHERE id = ?', (id,)
        ).fetchone()
        return render_template('delete.html', get=get)
    #POST data from database
    #By POSTing we will be editing the database by deleting the id based on the user's choice
    elif request.method == 'POST':
        #Connect to database
        conn = db.conn_db()
        error = None
        if not id:
            error = 'Item does no exist.'
        #If no error then execute delete id list
        if error is None:
            conn.execute(
                'DELETE from list WHERE id = ?',
                (id,)
            )
            conn.commit()
            posts = conn.execute(
                'SELECT * FROM list'
            ).fetchall()
            return render_template('home.html', posts=posts)
        #If delete is not successful
        else:
            post = conn.execute(
                'SELECT * FROM list WHERE id = ?', (id,)
            ).fetchone()
            flash(error)
            return render_template('delete.html', post=post)
#Method for adding items
@app.route('/add', methods=('GET', 'POST'))
def add():
    #POST= want to POST new item made by user to the database
    if request.method == 'POST':
        item_name = request.form['item_name']
        amount = request.form['amount']
        category = request.form['category']
        conn = db.conn_db()
        error = None

        #If user has not completed all fields, flash an error
        if not item_name or not amount or not category:
            error = 'You have incomplete fields.'
        #If no error then insert new list item into the database
        if error is None:
            conn.execute(
                'INSERT INTO list (item_name, amount, category) VALUES (?, ?, ?)',
                (item_name, amount, category)
            )
            conn.commit()
            flash('Item added successfully!')
            return render_template('add.html')
        flash(error)
    return render_template('add.html')
#Run the flask application in the background
if __name__ == '__main__':
    app.run(debug=True)
    if not os.path.exists('script.sqlite'):
        db.create_all()