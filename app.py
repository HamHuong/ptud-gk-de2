from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Task
from datetime import datetime
import os
import requests
import random

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
    # Using DiceBear's API for reliable avatar generation
    styles = ['adventurer', 'avataaars', 'bottts', 'pixel-art']
    style = random.choice(styles)
    seed = datetime.now().timestamp()
    return f"https://api.dicebear.com/7.x/{style}/svg?seed={seed}"

def get_overdue_count():
    if current_user.is_authenticated:
        if current_user.is_admin:
            # Admin sees overdue count for all tasks
            tasks = Task.query.all()
        else:
            # Regular users only see their own overdue count
            tasks = Task.query.filter_by(user_id=current_user.id).all()
        
        now = datetime.now()
        overdue_tasks = [task for task in tasks if task.is_overdue]
        return {
            'count': len(overdue_tasks),
            'urgent': sum(1 for task in overdue_tasks if (now - task.due_time).days >= 3),
            'recent': sum(1 for task in overdue_tasks if (now - task.due_time).days < 3)
        }
    return {'count': 0, 'urgent': 0, 'recent': 0}

@app.route('/')
@login_required
def index():
    if current_user.is_admin:
        # Admin sees all tasks
        tasks = Task.query.all()
    else:
        # Regular users only see their own tasks
        tasks = Task.query.filter_by(user_id=current_user.id).all()
    
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
        username = request.form['username']
        email = request.form['email']
        
        # Check if username exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return redirect(url_for('register'))
        
        # Check if email exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return redirect(url_for('register'))
        
        try:
            user = User(
                username=username,
                email=email,
                avatar_url=get_random_avatar()
            )
            user.set_password(request.form['password'])
            db.session.add(user)
            db.session.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'error')
            return redirect(url_for('register'))
            
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
            due_time_str = request.form['due_time']
            due_time = datetime.strptime(due_time_str, '%Y-%m-%dT%H:%M')
            
            # Ensure regular users can only create tasks for themselves
            if current_user.is_admin:
                user_id = int(request.form.get('user_id', current_user.id))
            else:
                user_id = current_user.id
            
            task = Task(
                title=request.form['title'],
                description=request.form['description'],
                due_time=due_time,
                user_id=user_id
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
    
    # Only fetch users list if current user is admin
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
        new_status = request.form['status']
        
        # Handle status change and finished time
        if new_status == 'completed' and task.status != 'completed':
            task.finished_time = datetime.now()
        elif new_status == 'pending' and task.status == 'completed':
            task.finished_time = None
            
        task.status = new_status
        task.due_time = datetime.strptime(request.form['due_time'], '%Y-%m-%dT%H:%M')
        
        db.session.commit()
        flash('Task updated successfully!', 'success')
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

@app.route('/task/<int:task_id>/complete')
@login_required
def complete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if current_user.is_admin or task.user_id == current_user.id:
        task.status = 'completed'
        task.finished_time = datetime.now()
        db.session.commit()
        flash('Task marked as completed!', 'success')
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