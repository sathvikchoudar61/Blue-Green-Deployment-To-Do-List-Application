from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import os
import json
import time
from datetime import datetime
import uuid

app = Flask(__name__)
app.secret_key = 'blue-green-deployment-secret-key'

# Enable template reloading for development
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.debug = True

# Server configuration
SERVER_NAME = os.environ.get('SERVER_NAME', 'Blue')
SERVER_PORT = int(os.environ.get('SERVER_PORT', 5001))
SERVER_COLOR = os.environ.get('SERVER_COLOR', 'blue')

# Data storage - Common database for both servers
COMMON_DATA_FILE = 'data/common_todos.json'
STATUS_FILE = 'server_status.json'

# Ensure data directory exists
os.makedirs('data', exist_ok=True)
COMMON_DATA_PATH = os.path.join('data', COMMON_DATA_FILE)
STATUS_PATH = os.path.join('data', STATUS_FILE)

def load_todos():
    """Load todos from common JSON file"""
    try:
        if os.path.exists(COMMON_DATA_PATH):
            with open(COMMON_DATA_PATH, 'r') as f:
                return json.load(f)
        return []
    except Exception as e:
        print(f"Error loading todos: {e}")
        return []

def save_todos(todos):
    """Save todos to common JSON file"""
    try:
        with open(COMMON_DATA_PATH, 'w') as f:
            json.dump(todos, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving todos: {e}")
        return False

def update_server_status():
    """Update server status with session count"""
    try:
        # Initialize session ID if not exists
        if 'session_id' not in session:
            session['session_id'] = str(uuid.uuid4())
            session['start_time'] = datetime.now().isoformat()
        
        # Load or create status
        status = {}
        if os.path.exists(STATUS_PATH):
            with open(STATUS_PATH, 'r') as f:
                status = json.load(f)
        
        # Update current server status
        server_key = SERVER_NAME.lower()
        if server_key not in status:
            status[server_key] = {
                'name': SERVER_NAME,
                'color': SERVER_COLOR,
                'sessions': {},
                'start_time': datetime.now().isoformat(),
                'port': SERVER_PORT
            }
        
        # Update session info
        session_id = session['session_id']
        status[server_key]['sessions'][session_id] = {
            'start_time': session.get('start_time', datetime.now().isoformat()),
            'last_active': datetime.now().isoformat()
        }
        
        # Clean up old sessions (older than 5 minutes) - reduced from 30 minutes
        current_time = datetime.now()
        cutoff_time = current_time.timestamp() - (5 * 60)  # 5 minutes
        
        for server in status:
            if 'sessions' in status[server]:
                status[server]['sessions'] = {
                    sid: info for sid, info in status[server]['sessions'].items()
                    if datetime.fromisoformat(info['last_active']).timestamp() > cutoff_time
                }
        
        # Save status
        with open(STATUS_PATH, 'w') as f:
            json.dump(status, f, indent=2)
            
        return status
    except Exception as e:
        print(f"Error updating server status: {e}")
        return {}

def get_active_sessions():
    """Get number of active sessions for current server"""
    try:
        if os.path.exists(STATUS_PATH):
            with open(STATUS_PATH, 'r') as f:
                status = json.load(f)
                server_key = SERVER_NAME.lower()
                if server_key in status and 'sessions' in status[server_key]:
                    return len(status[server_key]['sessions'])
        return 0
    except Exception as e:
        print(f"Error getting active sessions: {e}")
        return 0

@app.before_request
def before_request():
    """Check session and update server status before each request"""
    # Initialize session for new users
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
        session['start_time'] = datetime.now().isoformat()
        session['server_assigned'] = SERVER_NAME.lower()
    
    update_server_status()

def get_blue_server_sessions():
    """Get number of active sessions on blue server specifically"""
    try:
        if os.path.exists(STATUS_PATH):
            with open(STATUS_PATH, 'r') as f:
                status = json.load(f)
                if 'blue' in status and 'sessions' in status['blue']:
                    return len(status['blue']['sessions'])
        return 0
    except Exception as e:
        print(f"Error getting blue server sessions: {e}")
        return 0

@app.route('/')
def index():
    """Main page - check if we need to redirect to green server"""
    # Always check blue server load regardless of which server this is
    blue_sessions = get_blue_server_sessions()
    
    # If blue server has more than 3 sessions, redirect to green
    # Only redirect if this request is not already on green server
    if blue_sessions > 3 and SERVER_NAME.lower() != 'green':
        return redirect('http://localhost:5002')
    
    # Update current server's session count for display
    active_sessions = get_active_sessions()
    
    todos = load_todos()
    return render_template('index.html', 
                         todos=todos, 
                         server_name=SERVER_NAME,
                         server_color=SERVER_COLOR,
                         active_sessions=active_sessions)

@app.route('/add', methods=['POST'])
def add_todo():
    """Add a new todo item"""
    todo_text = request.form.get('todo', '').strip()
    if todo_text:
        todos = load_todos()
        new_todo = {
            'id': str(uuid.uuid4()),
            'text': todo_text,
            'created_at': datetime.now().isoformat(),
            'completed': False
        }
        todos.append(new_todo)
        save_todos(todos)
    
    return redirect(url_for('index'))

@app.route('/delete/<todo_id>')
def delete_todo(todo_id):
    """Delete a todo item"""
    todos = load_todos()
    todos = [todo for todo in todos if todo['id'] != todo_id]
    save_todos(todos)
    return redirect(url_for('index'))

@app.route('/toggle/<todo_id>')
def toggle_todo(todo_id):
    """Toggle todo completion status"""
    todos = load_todos()
    for todo in todos:
        if todo['id'] == todo_id:
            todo['completed'] = not todo['completed']
            break
    save_todos(todos)
    return redirect(url_for('index'))

@app.route('/server')
def server_info():
    """Display server information"""
    active_sessions = get_active_sessions()
    uptime = datetime.now() - datetime.fromisoformat(session.get('start_time', datetime.now().isoformat()))
    
    return render_template('server.html',
                         server_name=SERVER_NAME,
                         server_color=SERVER_COLOR,
                         server_port=SERVER_PORT,
                         active_sessions=active_sessions,
                         session_id=session.get('session_id', 'Unknown'),
                         uptime=str(uptime).split('.')[0],
                         container_id=os.environ.get('HOSTNAME', 'Local Development'))

@app.route('/api/status')
def api_status():
    """API endpoint for server status"""
    try:
        if os.path.exists(STATUS_PATH):
            with open(STATUS_PATH, 'r') as f:
                status = json.load(f)
                return jsonify(status)
        return jsonify({})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print(f"Starting {SERVER_NAME} server on port {SERVER_PORT}")
    app.run(host='0.0.0.0', port=SERVER_PORT, debug=True)