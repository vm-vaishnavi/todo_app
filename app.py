from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ------------------------------
# Database Model
# ------------------------------
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    deadline = db.Column(db.DateTime, nullable=True)
    completed = db.Column(db.Boolean, default=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Task {self.id} - {self.content}>"

# ------------------------------
# Routes
# ------------------------------
@app.route('/')
def index():
    tasks = Todo.query.order_by(Todo.date_created.desc()).all()
    return render_template('index.html', tasks=tasks)

@app.route('/add', methods=['POST'])
def add():
    content = request.form['content']
    deadline_str = request.form['deadline']

    # Parse deadline date if provided
    deadline = datetime.strptime(deadline_str, '%Y-%m-%d') if deadline_str else None

    if content.strip():
        new_task = Todo(content=content.strip(), deadline=deadline)
        db.session.add(new_task)
        db.session.commit()

    return redirect(url_for('index'))

@app.route('/complete/<int:id>')
def complete(id):
    task = Todo.query.get_or_404(id)
    task.completed = not task.completed
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete/<int:id>')
def delete(id):
    task = Todo.query.get_or_404(id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    task = Todo.query.get_or_404(id)

    if request.method == 'POST':
        task.content = request.form['content']
        deadline_str = request.form['deadline']
        task.deadline = datetime.strptime(deadline_str, '%Y-%m-%d') if deadline_str else None
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('edit.html', task=task)


# Run the App

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
