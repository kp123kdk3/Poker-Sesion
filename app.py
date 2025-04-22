from flask import Flask, render_template, jsonify, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from flask_cors import CORS
from flask_migrate import Migrate
import json
from werkzeug.security import generate_password_hash, check_password_hash
import os
from functools import wraps
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///poker_tracker.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

db = SQLAlchemy(app)
migrate = Migrate(app, db)
CORS(app)

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.String(20), unique=True, nullable=False)  # Unique player ID
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    avatar = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    friends = db.relationship('Friendship', 
                            foreign_keys='Friendship.user_id',
                            backref='user', 
                            lazy='dynamic')
    friend_of = db.relationship('Friendship',
                              foreign_keys='Friendship.friend_id',
                              backref='friend',
                              lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'player_id': self.player_id,
            'username': self.username,
            'avatar': self.avatar,
            'created_at': self.created_at.isoformat()
        }

class LoginHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    login_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    ip_address = db.Column(db.String(45))  # IPv6 addresses can be up to 45 chars
    user_agent = db.Column(db.String(255))
    
    user = db.relationship('User', backref='login_history')

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    score = db.Column(db.Integer, default=0)
    avatar = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'score': self.score,
            'avatar': self.avatar
        }

class PokerSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    buy_in_amount = db.Column(db.Float)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.strftime('%Y-%m-%d'),
            'buy_in_amount': self.buy_in_amount,
            'notes': self.notes
        }

class SessionPlayer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('poker_session.id'), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    session = db.relationship('PokerSession', backref='players')
    player = db.relationship('Player', backref='sessions')

class PlayerResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('poker_session.id'), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    final_amount = db.Column(db.Float, nullable=False)
    session = db.relationship('PokerSession', backref='results')
    player = db.relationship('Player', backref='results')

class Friendship(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    friend_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')  # pending, accepted, rejected

    __table_args__ = (
        db.UniqueConstraint('user_id', 'friend_id', name='unique_friendship'),
    )

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/leaderboard')
def get_leaderboard():
    players = Player.query.order_by(Player.score.desc()).limit(10).all()
    return jsonify([player.to_dict() for player in players])

@app.route('/api/sessions', methods=['GET', 'POST'])
@login_required
def sessions():
    if request.method == 'POST':
        data = request.json
        session = PokerSession(
            date=datetime.strptime(data['date'], '%Y-%m-%d'),
            buy_in_amount=data.get('buy_in_amount'),
            notes=data.get('notes')
        )
        db.session.add(session)
        db.session.commit()
        return jsonify(session.to_dict())
    else:
        sessions = PokerSession.query.order_by(PokerSession.date.desc()).all()
        return jsonify([session.to_dict() for session in sessions])

@app.route('/api/players', methods=['GET', 'POST'])
def players():
    if request.method == 'POST':
        data = request.json
        player = Player(
            username=data['username'],
            avatar=data.get('avatar')
        )
        db.session.add(player)
        db.session.commit()
        return jsonify(player.to_dict())
    else:
        players = Player.query.all()
        return jsonify([player.to_dict() for player in players])

@app.route('/api/session/<int:session_id>/results', methods=['GET', 'POST'])
def session_results(session_id):
    if request.method == 'POST':
        data = request.json
        result = PlayerResult(
            session_id=session_id,
            player_id=data['player_id'],
            final_amount=data['final_amount']
        )
        db.session.add(result)
        db.session.commit()
        return jsonify({'status': 'success'})
    else:
        results = PlayerResult.query.filter_by(session_id=session_id).all()
        return jsonify([{
            'player_id': r.player_id,
            'player_name': r.player.username,
            'final_amount': r.final_amount
        } for r in results])

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Missing username or password'}), 400
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    user = User(
        username=data['username'],
        avatar=data.get('avatar', 'default.png')
    )
    user.set_password(data['password'])
    
    try:
        db.session.add(user)
        db.session.commit()
        session['user_id'] = user.id
        return jsonify(user.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Registration failed'}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Missing username or password'}), 400
    
    user = User.query.filter_by(username=data['username']).first()
    
    if user and user.check_password(data['password']):
        session['user_id'] = user.id
        
        # Record login history
        login_record = LoginHistory(
            user_id=user.id,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(login_record)
        db.session.commit()
        
        return jsonify(user.to_dict()), 200
    
    return jsonify({'error': 'Invalid username or password'}), 401

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({'message': 'Logged out successfully'}), 200

@app.route('/api/auth/check', methods=['GET'])
def check_auth():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        if user:
            return jsonify(user.to_dict()), 200
    return jsonify({'error': 'Not authenticated'}), 401

@app.route('/api/sessions/<int:session_id>', methods=['DELETE'])
@login_required
def delete_session(session_id):
    session = PokerSession.query.get(session_id)
    if session:
        db.session.delete(session)
        db.session.commit()
        return jsonify({'message': 'Session deleted successfully'}), 200
    else:
        return jsonify({'error': 'Session not found'}), 404

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@app.route('/api/profile/avatar', methods=['POST'])
@login_required
def upload_avatar():
    if 'avatar' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['avatar']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(f"{session['user_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}")
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        # Update user's avatar in database
        user = User.query.get(session['user_id'])
        if user:
            # Delete old avatar if exists
            if user.avatar and os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], user.avatar)):
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], user.avatar))
            
            user.avatar = filename
            db.session.commit()
            
            return jsonify({'avatar': filename}), 200
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/api/profile/stats/<int:user_id>')
@login_required
def get_user_stats(user_id):
    # Get user's sessions
    sessions = PokerSession.query.join(SessionPlayer).join(Player).filter(Player.id == user_id).all()
    
    # Calculate statistics
    total_sessions = len(sessions)
    total_profit = 0
    winning_sessions = 0
    
    recent_sessions = []
    for session in sessions[:10]:  # Get last 10 sessions
        result = PlayerResult.query.filter_by(session_id=session.id, player_id=user_id).first()
        if result:
            profit_loss = result.final_amount - session.buy_in_amount
            total_profit += profit_loss
            if profit_loss > 0:
                winning_sessions += 1
            
            recent_sessions.append({
                'date': session.date.strftime('%Y-%m-%d'),
                'buy_in_amount': session.buy_in_amount,
                'profit_loss': profit_loss,
                'notes': session.notes
            })
    
    win_rate = (winning_sessions / total_sessions * 100) if total_sessions > 0 else 0
    
    return jsonify({
        'total_sessions': total_sessions,
        'total_profit': total_profit,
        'win_rate': round(win_rate, 1),
        'recent_sessions': recent_sessions
    })

@app.route('/api/friends', methods=['GET'])
@login_required
def get_friends():
    user_id = session['user_id']
    friendships = Friendship.query.filter(
        (Friendship.user_id == user_id) | (Friendship.friend_id == user_id),
        Friendship.status == 'accepted'
    ).all()
    
    friends = []
    for friendship in friendships:
        friend_id = friendship.friend_id if friendship.user_id == user_id else friendship.user_id
        friend = User.query.get(friend_id)
        if friend:
            friends.append(friend.to_dict())
    
    return jsonify(friends)

@app.route('/api/friends/pending', methods=['GET'])
@login_required
def get_pending_friends():
    user_id = session['user_id']
    pending_friendships = Friendship.query.filter(
        Friendship.friend_id == user_id,
        Friendship.status == 'pending'
    ).all()
    
    pending_friends = []
    for friendship in pending_friendships:
        friend = User.query.get(friendship.user_id)
        if friend:
            pending_friends.append(friend.to_dict())
    
    return jsonify(pending_friends)

@app.route('/api/friends/add', methods=['POST'])
@login_required
def add_friend():
    data = request.get_json()
    friend_player_id = data.get('player_id')
    
    if not friend_player_id:
        return jsonify({'error': 'Player ID is required'}), 400
    
    friend = User.query.filter_by(player_id=friend_player_id).first()
    if not friend:
        return jsonify({'error': 'User not found'}), 404
    
    user_id = session['user_id']
    if user_id == friend.id:
        return jsonify({'error': 'Cannot add yourself as a friend'}), 400
    
    # Check if friendship already exists
    existing_friendship = Friendship.query.filter(
        ((Friendship.user_id == user_id) & (Friendship.friend_id == friend.id)) |
        ((Friendship.user_id == friend.id) & (Friendship.friend_id == user_id))
    ).first()
    
    if existing_friendship:
        return jsonify({'error': 'Friendship already exists'}), 400
    
    friendship = Friendship(user_id=user_id, friend_id=friend.id)
    db.session.add(friendship)
    db.session.commit()
    
    return jsonify({'message': 'Friend request sent'}), 201

@app.route('/api/friends/accept/<int:friend_id>', methods=['POST'])
@login_required
def accept_friend(friend_id):
    user_id = session['user_id']
    friendship = Friendship.query.filter_by(
        user_id=friend_id,
        friend_id=user_id,
        status='pending'
    ).first()
    
    if not friendship:
        return jsonify({'error': 'Friend request not found'}), 404
    
    friendship.status = 'accepted'
    db.session.commit()
    
    return jsonify({'message': 'Friend request accepted'}), 200

@app.route('/api/friends/reject/<int:friend_id>', methods=['POST'])
@login_required
def reject_friend(friend_id):
    user_id = session['user_id']
    friendship = Friendship.query.filter_by(
        user_id=friend_id,
        friend_id=user_id,
        status='pending'
    ).first()
    
    if not friendship:
        return jsonify({'error': 'Friend request not found'}), 404
    
    friendship.status = 'rejected'
    db.session.commit()
    
    return jsonify({'message': 'Friend request rejected'}), 200

@app.route('/api/users/search', methods=['GET'])
@login_required
def search_users():
    query = request.args.get('query', '')
    if not query:
        return jsonify([])
        
    # Search for users by username, excluding the current user
    users = User.query.filter(
        User.username.ilike(f'%{query}%'),
        User.id != session['user_id']
    ).limit(10).all()
    
    return jsonify([{
        'player_id': user.player_id,
        'username': user.username,
        'avatar': user.avatar
    } for user in users])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Add sample players if the database is empty
        if not Player.query.first():
            sample_players = [
                {'username': 'PokerPro', 'score': 1500},
                {'username': 'CardShark', 'score': 1200},
                {'username': 'RiverKing', 'score': 1000},
                {'username': 'BluffMaster', 'score': 800},
                {'username': 'AceHigh', 'score': 750}
            ]
            
            for player_data in sample_players:
                player = Player(username=player_data['username'], score=player_data['score'])
                db.session.add(player)
            
            db.session.commit()
            
    app.run(debug=True, host='0.0.0.0', port=5003) 