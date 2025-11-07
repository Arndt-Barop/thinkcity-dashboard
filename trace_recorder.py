#!/usr/bin/env python3
# trace_recorder.py
# Records CAN messages to PCAN .trc format

import os
import time
import threading
from datetime import datetime
from typing import Optional, Callable
from queue import Queue, Full
import can


class TraceRecorder:
    """
    Records CAN messages to PCAN .trc format.
    
    Features:
    - Real-time recording from CAN interface
    - PCAN .trc format (compatible with PCANview)
    - Non-blocking, thread-safe
    - Automatic storage management
    - Start/Stop/Pause functionality
    """
    
    def __init__(self, can_interface: str, output_dir: str):
        """
        Initialize TraceRecorder.
        
        Args:
            can_interface: CAN interface name (e.g., 'can0', 'vcan0')
            output_dir: Directory for trace files
        """
        self.can_interface = can_interface
        self.output_dir = os.path.expanduser(output_dir)
        
        # Create output directory if not exists
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Recording state
        self.is_recording_flag = False
        self.is_paused = False
        self.recording_thread = None
        self.message_queue = Queue(maxsize=10000)  # Max 10k messages buffered
        
        # Current recording
        self.current_file = None
        self.current_filepath = None
        self.start_time = None
        self.start_timestamp = None
        self.message_count = 0
        self.unique_can_ids = set()
        
        # Lock for thread-safe operations
        self.lock = threading.Lock()
        
        # Auto-stop threshold (MB)
        self.min_free_space_mb = 100
    
    def start_recording(self, filename: Optional[str] = None) -> bool:
        """
        Start recording CAN messages.
        
        Args:
            filename: Optional custom filename (without .trc extension)
                     If None, auto-generates: ThinkCity_YYYY-MM-DD_HH-MM-SS.trc
        
        Returns:
            True if started successfully, False otherwise
        """
        with self.lock:
            if self.is_recording_flag:
                print("Warning: Recording already active")
                return False
            
            # Check storage space
            if self.get_free_space_mb() < self.min_free_space_mb:
                print(f"Error: Not enough storage space (< {self.min_free_space_mb} MB)")
                return False
            
            # Generate filename if not provided
            if filename is None:
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                filename = f"ThinkCity_{timestamp}"
            
            # Ensure .trc extension
            if not filename.endswith('.trc'):
                filename += '.trc'
            
            self.current_filepath = os.path.join(self.output_dir, filename)
            
            # Check if file already exists
            if os.path.exists(self.current_filepath):
                print(f"Warning: File already exists: {self.current_filepath}")
                # Add suffix
                base, ext = os.path.splitext(self.current_filepath)
                counter = 1
                while os.path.exists(f"{base}_{counter}{ext}"):
                    counter += 1
                self.current_filepath = f"{base}_{counter}{ext}"
            
            try:
                # Open file for writing
                self.current_file = open(self.current_filepath, 'w')
                
                # Write header
                self._write_header()
                
                # Reset counters
                self.message_count = 0
                self.unique_can_ids.clear()
                self.start_time = time.time()
                self.start_timestamp = time.monotonic()
                self.is_recording_flag = True
                self.is_paused = False
                
                # Start writer thread
                self.recording_thread = threading.Thread(target=self._writer_thread, daemon=True)
                self.recording_thread.start()
                
                print(f"✓ Recording started: {os.path.basename(self.current_filepath)}")
                return True
                
            except Exception as e:
                print(f"Error starting recording: {e}")
                if self.current_file:
                    self.current_file.close()
                    self.current_file = None
                return False
    
    def stop_recording(self) -> dict:
        """
        Stop recording and return statistics.
        
        Returns:
            Dictionary with recording statistics
        """
        with self.lock:
            if not self.is_recording_flag:
                print("Warning: No active recording")
                return {}
            
            self.is_recording_flag = False
            self.is_paused = False
            
            # Wait for writer thread to finish
            if self.recording_thread:
                self.recording_thread.join(timeout=5.0)
            
            # Close file
            if self.current_file:
                self.current_file.flush()
                self.current_file.close()
                self.current_file = None
            
            # Calculate statistics
            duration = time.time() - self.start_time if self.start_time else 0
            file_size_mb = os.path.getsize(self.current_filepath) / (1024 * 1024) if self.current_filepath else 0
            
            stats = {
                'filename': os.path.basename(self.current_filepath) if self.current_filepath else '',
                'duration_seconds': duration,
                'message_count': self.message_count,
                'file_size_mb': file_size_mb,
                'unique_can_ids': len(self.unique_can_ids),
                'average_rate_hz': self.message_count / duration if duration > 0 else 0,
                'start_time': datetime.fromtimestamp(self.start_time).strftime("%Y-%m-%d %H:%M:%S") if self.start_time else '',
                'end_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            print(f"✓ Recording stopped: {stats['filename']}")
            print(f"  Duration: {stats['duration_seconds']:.1f}s")
            print(f"  Messages: {stats['message_count']}")
            print(f"  File size: {stats['file_size_mb']:.2f} MB")
            
            return stats
    
    def pause_recording(self):
        """Pause recording (stops writing but keeps file open)."""
        with self.lock:
            if self.is_recording_flag and not self.is_paused:
                self.is_paused = True
                print("⏸ Recording paused")
    
    def resume_recording(self):
        """Resume recording after pause."""
        with self.lock:
            if self.is_recording_flag and self.is_paused:
                self.is_paused = False
                print("▶ Recording resumed")
    
    def is_recording(self) -> bool:
        """Check if currently recording (and not paused)."""
        return self.is_recording_flag and not self.is_paused
    
    def get_stats(self) -> dict:
        """
        Get current recording statistics.
        
        Returns:
            Dictionary with current stats (while recording)
        """
        with self.lock:
            if not self.is_recording_flag:
                return {}
            
            duration = time.time() - self.start_time if self.start_time else 0
            file_size_mb = os.path.getsize(self.current_filepath) / (1024 * 1024) if self.current_filepath and os.path.exists(self.current_filepath) else 0
            
            return {
                'filename': os.path.basename(self.current_filepath) if self.current_filepath else '',
                'duration_seconds': duration,
                'message_count': self.message_count,
                'file_size_mb': file_size_mb,
                'unique_can_ids': len(self.unique_can_ids),
                'average_rate_hz': self.message_count / duration if duration > 0 else 0,
                'is_paused': self.is_paused
            }
    
    def record_message(self, msg: can.Message):
        """
        Record a CAN message (called from main CAN thread).
        
        Args:
            msg: python-can Message object
        """
        if not self.is_recording_flag or self.is_paused:
            return
        
        try:
            # Add to queue (non-blocking)
            self.message_queue.put_nowait(msg)
        except Full:
            print("Warning: Recording queue full, dropping message")
    
    def get_free_space_mb(self) -> float:
        """Get free storage space in MB."""
        try:
            st = os.statvfs(self.output_dir)
            free_bytes = st.f_bavail * st.f_frsize
            return free_bytes / (1024 * 1024)
        except Exception as e:
            print(f"Warning: Could not check storage: {e}")
            return 0.0
    
    def _write_header(self):
        """Write PCAN trace file header."""
        if not self.current_file:
            return
        
        # File version
        self.current_file.write(";$FILEVERSION=1.1\n")
        
        # Start time (Excel datetime format)
        # Days since 1899-12-30 + fraction of day
        now = datetime.now()
        excel_epoch = datetime(1899, 12, 30)
        delta = now - excel_epoch
        excel_time = delta.days + delta.seconds / 86400.0
        self.current_file.write(f";$STARTTIME={excel_time:.13f}\n")
        
        # Human-readable start time
        start_str = now.strftime("%d.%m.%Y %H:%M:%S.%f")[:-3]  # Milliseconds
        self.current_file.write(f";   Start time: {start_str}.0\n")
        
        # Column header
        self.current_file.write(";\n")
        self.current_file.write(";   Message   Time    Type ID     DLC Data Bytes\n")
        self.current_file.write(";   Number    Offset  \n")
        self.current_file.write(";---+--   ----+----  --+--  ----+---  +  -+ -- -- -- -- -- -- --\n")
        
        self.current_file.flush()
    
    def _write_message(self, msg_number: int, timestamp_ms: float, msg: can.Message):
        """
        Write a single CAN message to file.
        
        Args:
            msg_number: Sequential message number
            timestamp_ms: Relative timestamp in milliseconds
            msg: python-can Message object
        """
        if not self.current_file:
            return
        
        # Format: Number) Time Rx CAN-ID DLC Data
        # Example:      1)         0.0  Rx         0251  8  40 00 00 00 00 00 00 00
        
        # CAN ID (4 hex digits)
        can_id_str = f"{msg.arbitration_id:04X}"
        
        # Data bytes (space-separated hex, uppercase)
        data_str = ' '.join(f"{b:02X}" for b in msg.data)
        
        # Message line
        line = f"{msg_number:6d})  {timestamp_ms:11.1f}  Rx         {can_id_str}  {msg.dlc}  {data_str}\n"
        
        self.current_file.write(line)
    
    def _writer_thread(self):
        """Background thread that writes messages from queue to file."""
        batch_size = 100  # Flush every 100 messages
        messages_since_flush = 0
        
        while self.is_recording_flag:
            try:
                # Get message from queue (timeout 0.1s)
                msg = self.message_queue.get(timeout=0.1)
                
                if self.is_paused:
                    continue
                
                # Calculate relative timestamp (ms)
                timestamp_ms = (time.monotonic() - self.start_timestamp) * 1000.0
                
                # Increment message counter
                self.message_count += 1
                
                # Track unique CAN IDs
                self.unique_can_ids.add(msg.arbitration_id)
                
                # Write message
                self._write_message(self.message_count, timestamp_ms, msg)
                
                messages_since_flush += 1
                
                # Flush periodically
                if messages_since_flush >= batch_size:
                    self.current_file.flush()
                    messages_since_flush = 0
                
                # Check storage space (every 1000 messages)
                if self.message_count % 1000 == 0:
                    if self.get_free_space_mb() < self.min_free_space_mb:
                        print(f"Warning: Low storage space, stopping recording")
                        self.stop_recording()
                        break
                
            except Exception as e:
                if self.is_recording_flag:  # Only log if still supposed to be recording
                    pass  # Timeout is normal
        
        # Final flush
        if self.current_file:
            self.current_file.flush()


# Test/Demo
if __name__ == "__main__":
    import sys
    
    print("=== TraceRecorder Test ===")
    
    # Create recorder
    recorder = TraceRecorder(
        can_interface='vcan0',
        output_dir='~/thinkcity-dashboard-v3/traces'
    )
    
    print(f"Output directory: {recorder.output_dir}")
    print(f"Free space: {recorder.get_free_space_mb():.1f} MB")
    
    # Start recording
    if not recorder.start_recording():
        sys.exit(1)
    
    print("\n✓ Recording started")
    print("Simulating CAN messages for 5 seconds...\n")
    
    # Simulate some CAN messages
    for i in range(50):
        msg = can.Message(
            arbitration_id=0x251 + (i % 5),
            data=[0x40 + i % 16, 0x00, 0x00, 0x00, i % 256, 0x00, 0x00, 0x00],
            is_extended_id=False
        )
        recorder.record_message(msg)
        time.sleep(0.1)
        
        # Print stats every 10 messages
        if (i + 1) % 10 == 0:
            stats = recorder.get_stats()
            print(f"  Messages: {stats['message_count']}, "
                  f"Duration: {stats['duration_seconds']:.1f}s, "
                  f"Rate: {stats['average_rate_hz']:.1f} Hz, "
                  f"Size: {stats['file_size_mb']:.3f} MB")
    
    # Stop recording
    final_stats = recorder.stop_recording()
    
    print("\n=== Recording Complete ===")
    print(f"File: {final_stats['filename']}")
    print(f"Duration: {final_stats['duration_seconds']:.1f}s")
    print(f"Messages: {final_stats['message_count']}")
    print(f"Unique CAN IDs: {final_stats['unique_can_ids']}")
    print(f"Average rate: {final_stats['average_rate_hz']:.1f} Hz")
    print(f"File size: {final_stats['file_size_mb']:.3f} MB")
    
    print(f"\n✓ Test completed successfully")
    print(f"Trace file: {recorder.current_filepath}")
