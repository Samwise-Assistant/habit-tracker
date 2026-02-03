from app import app, db, User, Habit, HabitCompletion, GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET
from flask import render_template, redirect, url_for, request, session, flash
from flask_login import login_required, current_user
import requests
from datetime import datetime, date, timedelta

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard():
    today = date.today()
    habits = Habit.query.filter_by(user_id=current_user.id).all()
    
    habit_data = []
    for habit in habits:
        # Check if completed today
        completion = HabitCompletion.query.filter_by(habit_id=habit.id, date=today).first()
        
        # Calculate streak
        streak = 0
        check_date = today
        while True:
            check = HabitCompletion.query.filter_by(habit_id=habit.id, date=check_date).first()
            if check:
                streak += 1
                check_date -= timedelta(days=1)
            else:
                if check_date == today:  # Check yesterday if today not done
                    check_date -= timedelta(days=1)
                else:
                    break
        
        # Get completions for heatmap (last 30 days)
        heatmap_data = []
        for i in range(29, -1, -1):
            d = today - timedelta(days=i)
            c = HabitCompletion.query.filter_by(habit_id=habit.id, date=d).first()
            heatmap_data.append({'date': d.isoformat(), 'done': bool(c)})
        
        habit_data.append({
            'habit': habit,
            'completed_today': bool(completion),
            'streak': streak,
            'heatmap': heatmap_data
        })
    
    return render_template('dashboard.html', habits=habit_data, today=today)

@app.route('/habit/add', methods=['POST'])
@login_required
def add_habit():
    name = request.form.get('name')
    icon = request.form.get('icon', '✅')
    color = request.form.get('color', '#3B82F6')
    frequency = request.form.get('frequency', 'daily')
    
    habit = Habit(user_id=current_user.id, name=name, icon=icon, color=color, frequency=frequency)
    db.session.add(habit)
    db.session.commit()
    
    flash(f'Habit "{name}" added!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/habit/<int:habit_id>/toggle', methods=['POST'])
@login_required
def toggle_habit(habit_id):
    habit = Habit.query.get_or_404(habit_id)
    if habit.user_id != current_user.id:
        flash('Unauthorized', 'error')
        return redirect(url_for('dashboard'))
    
    today = date.today()
    completion = HabitCompletion.query.filter_by(habit_id=habit.id, date=today).first()
    
    if completion:
        db.session.delete(completion)
        flash(f'Habit uncompleted for today', 'info')
    else:
        completion = HabitCompletion(habit_id=habit.id, date=today)
        db.session.add(completion)
        flash(f'Habit completed! 🎉', 'success')
    
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/habit/<int:habit_id>/delete', methods=['POST'])
@login_required
def delete_habit(habit_id):
    habit = Habit.query.get_or_404(habit_id)
    if habit.user_id != current_user.id:
        flash('Unauthorized', 'error')
        return redirect(url_for('dashboard'))
    
    db.session.delete(habit)
    db.session.commit()
    flash('Habit deleted', 'info')
    return redirect(url_for('dashboard'))

# GitHub OAuth
@app.route('/login/github')
def login_github():
    session['oauth_state'] = 'github'
    return redirect(f'https://github.com/login/oauth/authorize?client_id={GITHUB_CLIENT_ID}&scope=read:user')

@app.route('/login/github/callback')
def github_callback():
    if request.args.get('error'):
        flash('GitHub login cancelled', 'error')
        return redirect(url_for('index'))
    
    code = request.args.get('code')
    
    # Exchange code for token
    token_response = requests.post(
        'https://github.com/login/oauth/access_token',
        json={'client_id': GITHUB_CLIENT_ID, 'client_secret': GITHUB_CLIENT_SECRET, 'code': code},
        headers={'Accept': 'application/json'}
    )
    
    access_token = token_response.json().get('access_token')
    if not access_token:
        flash('GitHub login failed', 'error')
        return redirect(url_for('index'))
    
    # Get user info
    user_response = requests.get(
        'https://api.github.com/user',
        headers={'Authorization': f'Bearer {access_token}', 'Accept': 'application/json'}
    )
    github_user = user_response.json()
    
    # Find or create user
    user = User.query.filter_by(github_id=str(github_user['id'])).first()
    if not user:
        user = User(
            github_id=str(github_user['id']),
            name=github_user.get('name', github_user['login']),
            email=github_user.get('email'),
            avatar_url=github_user.get('avatar_url')
        )
        db.session.add(user)
        db.session.commit()
    
    login_user(user)
    flash(f'Welcome, {user.name}!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out', 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
