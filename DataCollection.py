import psutil
import time
from datetime import datetime
import os
import sqlite3

def setup_database():
    """Create a new database and required table"""
    # Delete existing database if it exists
    if os.path.exists('system_metrics.db'):
        os.remove('system_metrics.db')
    
    conn = sqlite3.connect('system_metrics.db')
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS system_metrics (
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            cpu_percent REAL,
            ram_percent REAL,
            ram_used REAL,
            ram_total REAL,
            upload_speed REAL,
            download_speed REAL,
            disk_read_speed REAL,
            disk_write_speed REAL
        )
    ''')
    
    conn.commit()
    return conn

def store_metrics(conn, metrics):
    """Store the metrics in the database"""
    c = conn.cursor()
    c.execute('''
        INSERT INTO system_metrics (
            cpu_percent, ram_percent, ram_used, ram_total,
            upload_speed, download_speed, disk_read_speed, disk_write_speed
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        metrics['cpu_percent'],
        metrics['ram_percent'],
        metrics['ram_used'],
        metrics['ram_total'],
        metrics['upload_speed'],
        metrics['download_speed'],
        metrics['disk_read_speed'],
        metrics['disk_write_speed']
    ))
    conn.commit()

def get_size(bytes):
    """
    Convert bytes to human readable format
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes < 1024:
            return f"{bytes:.2f}{unit}"
        bytes /= 1024

def monitor_system():
    # Setup database connection
    conn = setup_database()
    
    # Get initial counters
    net_io = psutil.net_io_counters()
    bytes_sent = net_io.bytes_sent
    bytes_recv = net_io.bytes_recv
    
    # Get initial disk I/O counters
    disk_io = psutil.disk_io_counters()
    bytes_read = disk_io.read_bytes
    bytes_write = disk_io.write_bytes
    
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        
        # Get updated network stats
        new_net_io = psutil.net_io_counters()
        new_bytes_sent = new_net_io.bytes_sent
        new_bytes_recv = new_net_io.bytes_recv
        
        # Get updated disk I/O stats
        new_disk_io = psutil.disk_io_counters()
        new_bytes_read = new_disk_io.read_bytes
        new_bytes_write = new_disk_io.write_bytes
        
        # Calculate speeds
        upload_speed = new_bytes_sent - bytes_sent
        download_speed = new_bytes_recv - bytes_recv
        disk_read_speed = new_bytes_read - bytes_read
        disk_write_speed = new_bytes_write - bytes_write
        
        # Update previous values
        bytes_sent, bytes_recv = new_bytes_sent, new_bytes_recv
        bytes_read, bytes_write = new_bytes_read, new_bytes_write
        
        # Store metrics in database
        metrics = {
            'cpu_percent': cpu_percent,
            'ram_percent': memory.percent,
            'ram_used': memory.used,
            'ram_total': memory.total,
            'upload_speed': upload_speed,
            'download_speed': download_speed,
            'disk_read_speed': disk_read_speed,
            'disk_write_speed': disk_write_speed
        }
        store_metrics(conn, metrics)
        
        current_time = datetime.now().strftime("%H:%M:%S")
        
        # Print statistics
        print(f"System Monitor - {current_time}")
        print("-" * 40)
        print(f"CPU Usage: {cpu_percent}%")
        print(f"RAM Usage: {memory.percent}%")
        print(f"RAM Used: {get_size(memory.used)} / {get_size(memory.total)}")
        print(f"\nNetwork:")
        print(f"Upload Speed: {get_size(upload_speed)}/s")
        print(f"Download Speed: {get_size(download_speed)}/s")
        print(f"\nDisk Activity:")
        print(f"Read Speed: {get_size(disk_read_speed)}/s")
        print(f"Write Speed: {get_size(disk_write_speed)}/s")
        print("\nMetrics are being stored in 'system_metrics.db'")
        
        time.sleep(1)

if __name__ == "__main__":
    try:
        monitor_system()
    except KeyboardInterrupt:
        print("\nMonitoring stopped.")
