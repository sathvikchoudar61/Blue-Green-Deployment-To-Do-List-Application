# Blue-Green Deployment To-Do List App

A Python Flask application demonstrating blue-green deployment with automatic load balancing based on session count.

## Fixed Issues

✅ **Fixed session counting logic** - Now properly checks blue server sessions before redirecting
✅ **Created separate data files** - Blue and green servers now have independent todo lists
✅ **Fixed redirect logic** - No longer always starts on green server
✅ **Improved session management** - Better tracking of user sessions

## How It Works

1. **Blue Server** (Port 5001): Handles initial traffic up to 3 concurrent sessions
2. **Green Server** (Port 5002): Receives new sessions when Blue exceeds 3 active sessions
3. **Auto-switching**: New users are automatically redirected based on Blue server load

## Running the Application

To run the application, simply run the `start_servers.bat` file. This will start the blue server, the green server, and the router. You can then access the application at http://localhost:5000.

## Testing the Blue-Green Switching

1. Open http://localhost:5001 (Blue server)
2. Add some todo items
3. Open 4+ different browser tabs/windows to exceed the 3-session limit
4. New sessions will automatically redirect to http://localhost:5002 (Green server)
5. Each server maintains its own separate todo list

## Features

- 🟦 Blue Server: Handles initial traffic (up to 3 sessions)
- 🟩 Green Server: Activated when Blue is overloaded
- 📊 Session tracking: Real-time session count display
- 📝 Independent todo lists: Each server has its own data
- 🔄 Automatic load balancing: Seamless server switching
- 📱 Responsive UI: Works on desktop and mobile

## Data Storage

- Todo data: Stored in `data/data_blue.json` and `data/data_green.json`
- Session status: Tracked in `data/server_status.json`
- Each server maintains independent data for true blue-green deployment simulation"# Blue-Green-Deployment-To-Do-List-Application" 
