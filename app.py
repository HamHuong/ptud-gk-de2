from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Task
from datetime import datetime
import os
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'  # Change this in production
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

def get_random_avatar():
    return f"https://avatar-placeholder.iran.liara.run/public/{datetime.now().timestamp()}"

def get_overdue_count():
    if current_user.is_authenticated:
        tasks = Task.query.filter_by(user_id=current_user.id).all() if not current_user.is_admin else Task.query.all()
        return sum(1 for task in tasks if task.is_overdue)
    return 0

@app.route('/')
@login_required
def index():
    tasks = Task.query.filter_by(user_id=current_user.id).all() if not current_user.is_admin else Task.query.all()
    overdue_count = get_overdue_count()
    return render_template('index.html', tasks=tasks, overdue_count=overdue_count)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and user.check_password(request.form['password']):
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid username or password')
    return render_template('login.html', overdue_count=0)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if User.query.filter_by(username=request.form['username']).first():
            flash('Username already exists')
            return redirect(url_for('register'))
        
        user = User(
            username=request.form['username'],
            email=request.form['email'],
            avatar_url=get_random_avatar()
        )
        user.set_password(request.form['password'])
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', overdue_count=0)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/task/new', methods=['GET', 'POST'])
@login_required
def new_task():
    if request.method == 'POST':
        try:
            print("Form data:", request.form)
            
            due_time_str = request.form['due_time']
            due_time = datetime.strptime(due_time_str, '%Y-%m-%dT%H:%M')
            
            task = Task(
                title=request.form['title'],
                description=request.form['description'],
                due_time=due_time,
                user_id=current_user.id if not current_user.is_admin else int(request.form.get('user_id', current_user.id))
            )
            db.session.add(task)
            db.session.commit()
            flash('Task created successfully!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            print("Error creating task:", str(e))
            db.session.rollback()
            flash('Error creating task: ' + str(e), 'error')
            return redirect(url_for('new_task'))
            
    users = User.query.all() if current_user.is_admin else None
    overdue_count = get_overdue_count()
    return render_template('task_form.html', users=users, overdue_count=overdue_count)

@app.route('/task/<int:task_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    if not current_user.is_admin and task.user_id != current_user.id:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        task.title = request.form['title']
        task.description = request.form['description']
        task.status = request.form['status']
        task.due_time = datetime.strptime(request.form['due_time'], '%Y-%m-%dT%H:%M')
        if task.status == 'completed' and not task.finished_time:
            task.finished_time = datetime.utcnow()
        db.session.commit()
        return redirect(url_for('index'))
    overdue_count = get_overdue_count()
    return render_template('task_form.html', task=task, overdue_count=overdue_count)

@app.route('/task/<int:task_id>/delete')
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if current_user.is_admin or task.user_id == current_user.id:
        db.session.delete(task)
        db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Create admin user if not exists
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@example.com',
                is_admin=True,
                avatar_url=get_random_avatar()
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
    app.run(debug=True) 