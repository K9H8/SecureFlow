import psutil
import time
from datetime import datetime, timedelta
import os
import sqlite3

def setup_metrics_database():
    """Create a new database and required table"""
    # Delete existing database if it exists
    if os.path.exists('system_metrics.db'):
        os.remove('system_metrics.db')
    
    conn = sqlite3.connect('system_metrics.db')
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS system_metrics (
            timestamp DATETIME,
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
    
    # Use the system's current time as the timestamp
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    c.execute('''
        INSERT INTO system_metrics (
            timestamp,
            cpu_percent, ram_percent, ram_used, ram_total,
            upload_speed, download_speed, disk_read_speed, disk_write_speed
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        current_time,
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

def setup_average_table(conn):
    """Create a new table for storing minute averages"""
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS minute_averages (
            timestamp DATETIME,
            avg_cpu_percent REAL,
            avg_ram_percent REAL,
            avg_ram_used REAL,
            avg_ram_total REAL,
            avg_upload_speed REAL,
            avg_download_speed REAL,
            avg_disk_read_speed REAL,
            avg_disk_write_speed REAL
        )
    ''')
    
    conn.commit()

def store_minute_averages(conn):
    """Calculate and store the average metrics from the last minute"""
    c = conn.cursor()
    
    # Get the current time and the time one minute ago
    current_time = datetime.now()
    one_minute_ago = current_time - timedelta(minutes=1)
    
    # Query to calculate averages
    c.execute('''
        SELECT 
            AVG(cpu_percent) AS avg_cpu_percent,
            AVG(ram_percent) AS avg_ram_percent,
            AVG(ram_used) AS avg_ram_used,
            AVG(ram_total) AS avg_ram_total,
            AVG(upload_speed) AS avg_upload_speed,
            AVG(download_speed) AS avg_download_speed,
            AVG(disk_read_speed) AS avg_disk_read_speed,
            AVG(disk_write_speed) AS avg_disk_write_speed
        FROM system_metrics
        WHERE timestamp >= ?
    ''', (one_minute_ago.strftime("%Y-%m-%d %H:%M:%S"),))
    
    averages = c.fetchone()
    
    # Store the averages in the minute_averages table
    c.execute('''
        INSERT INTO minute_averages (
            timestamp,
            avg_cpu_percent, avg_ram_percent, avg_ram_used, avg_ram_total,
            avg_upload_speed, avg_download_speed, avg_disk_read_speed, avg_disk_write_speed
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (current_time.strftime("%Y-%m-%d %H:%M:%S"),) + averages)
    
    conn.commit()

def monitor_system():
    # Setup database connection
    conn = setup_metrics_database()
    setup_average_table(conn)  # Create the average table
    
    # Get initial counters
    net_io = psutil.net_io_counters()
    bytes_sent = net_io.bytes_sent
    bytes_recv = net_io.bytes_recv
    
    # Get initial disk I/O counters
    disk_io = psutil.disk_io_counters()
    bytes_read = disk_io.read_bytes
    bytes_write = disk_io.write_bytes
    
    # data collection start time for consle print 
    start_time = time.time()

    while True:
        print(f"Time passed: {int(time.time() - start_time)} seconds")
        time.sleep(1)  # Adjust the sleep time as needed
        
        # Get updated metrics
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
        
        # Store minute averages every minute
        if int(time.time()) % 60 == 0:  # Check if the current time is a multiple of 60 seconds
            store_minute_averages(conn)

def monitor_system_averages():
    conn = setup_metrics_database()
    setup_average_table(conn)
    conn.close()

if __name__ == "__main__":
    monitor_system()
    monitor_system_averages()
    