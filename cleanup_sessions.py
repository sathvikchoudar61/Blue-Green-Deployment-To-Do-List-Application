#!/usr/bin/env python3
"""
Manual session cleanup script for blue-green deployment
"""
import json
from datetime import datetime

def cleanup_old_sessions():
    """Clean up sessions older than 5 minutes"""
    status_file = 'data/server_status.json'
    
    try:
        # Read current status
        with open(status_file, 'r') as f:
            status = json.load(f)
        
        current_time = datetime.now()
        cutoff_time = current_time.timestamp() - (5 * 60)  # 5 minutes ago
        
        print(f'Current time: {current_time.isoformat()}')
        print(f'Cutoff time: {datetime.fromtimestamp(cutoff_time).isoformat()}')
        print()
        
        total_removed = 0
        total_kept = 0
        
        for server in ['blue', 'green']:
            if server in status and 'sessions' in status[server]:
                print(f'{server.upper()} server sessions:')
                
                # Filter sessions
                kept_sessions = {}
                removed_count = 0
                
                for sid, info in status[server]['sessions'].items():
                    try:
                        last_active = datetime.fromisoformat(info['last_active'])
                        should_keep = last_active.timestamp() > cutoff_time
                        
                        if should_keep:
                            kept_sessions[sid] = info
                            total_kept += 1
                            print(f'  KEEP {sid[:8]}... last active: {last_active.isoformat()}')
                        else:
                            removed_count += 1
                            total_removed += 1
                            print(f'  REMOVE {sid[:8]}... last active: {last_active.isoformat()}')
                            
                    except Exception as e:
                        print(f'  ERROR with session {sid[:8]}: {e}')
                        # Keep sessions with errors to be safe
                        kept_sessions[sid] = info
                        total_kept += 1
                
                # Update the sessions
                status[server]['sessions'] = kept_sessions
                print(f'  Kept: {len(kept_sessions)}, Removed: {removed_count}')
                print()
        
        # Save the cleaned status
        with open(status_file, 'w') as f:
            json.dump(status, f, indent=2)
        
        print(f'Session cleanup complete!')
        print(f'Total removed: {total_removed}')
        print(f'Total kept: {total_kept}')
        
        return True
        
    except Exception as e:
        print(f'Error during cleanup: {e}')
        return False

if __name__ == '__main__':
    cleanup_old_sessions()