from flask import Flask, render_template, redirect, request, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///mydatabase.db"
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(50), nullable=False)
    expensename = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(50), nullable=False)

# Create the database tables
with app.app_context():
    db.create_all()

# Routes
@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return render_template('landing.html', error=True)
        else:
            new_user = User(username=username)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            return redirect('/login')  # Redirect to login page after signing up
    return render_template('landing.html', error=False)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['username'] = username
            return redirect('/addexpense')  # Redirect to add expense page after logging in
        else:
            return render_template('landing.html', error=True)
    return render_template('landing.html', error=False)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')

@app.route('/expenses')
def expenses():
    if 'username' not in session:
        return redirect('/login')
    expenses = Expense.query.all()
    total = sum(int(expense.amount) for expense in expenses if expense.amount)  # Check if amount is not empty
    t_business = sum(int(expense.amount) for expense in expenses if expense.amount and expense.category == "business")  # Check if amount is not empty
    t_entertainment = sum(int(expense.amount) for expense in expenses if expense.amount and expense.category == "entertainment")  # Check if amount is not empty
    t_food = sum(int(expense.amount) for expense in expenses if expense.amount and expense.category == "food")  # Check if amount is not empty
    t_other = sum(int(expense.amount) for expense in expenses if expense.amount and expense.category == "other")  # Check if amount is not empty
    return render_template("expenses.html", expenses=expenses, total=total, t_business=t_business, t_entertainment=t_entertainment, t_food=t_food, t_other=t_other)

@app.route('/addexpense', methods=['GET', 'POST'])
def addexpense():
    if 'username' not in session:
        return redirect('/login')
    if request.method == 'POST':
        date = request.form['date']
        expensename = request.form['expensename']
        amount = request.form['amount']
        category = request.form['category']
        expense = Expense(date=date, expensename=expensename, amount=amount, category=category)
        db.session.add(expense)
        db.session.commit()
        return redirect('/expenses')
    return render_template('addexpense.html')

@app.route('/updateexpense/<int:expense_id>', methods=['POST','GET'])
def editexpense(expense_id):
    if 'username' not in session:
        return redirect('/login')
    expense = Expense.query.get(expense_id)
    if request.method == 'POST':
        expense.date = request.form['date']
        expense.expensename = request.form['expensename']
        expense.amount = request.form['amount']
        expense.category = request.form['category']
        db.session.commit()
        return redirect('/expenses')
    return render_template('updateexpense.html', expense=expense)

@app.route('/delete/<int:expense_id>')
def deleteexpense(expense_id):
    if 'username' not in session:
        return redirect('/login')
    expense = Expense.query.get(expense_id)
    db.session.delete(expense)
    db.session.commit()
    return redirect('/expenses')


if __name__ == '__main__':
    app.run(debug=True)