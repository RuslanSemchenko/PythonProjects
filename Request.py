import tkinter as tk
from tkinter import messagebox
import requests  # type: ignore
from urllib.parse import urlparse
import threading
from concurrent.futures import ThreadPoolExecutor
from queue import Queue

class RequestTester:
    def __init__(self, root):
        self.root = root
        self.root.title("HTTP/HTTPS Request Sender")
        
        # URL Entry
        tk.Label(root, text="URL:").grid(row=0, column=0, padx=5, pady=5)
        self.url_entry = tk.Entry(root, width=50)
        self.url_entry.grid(row=0, column=1, columnspan=2, padx=5, pady=5)
        
        # Number of Requests Entry
        tk.Label(root, text="Number of Requests:").grid(row=1, column=0, padx=5, pady=5)
        self.num_requests_entry = tk.Entry(root, width=10)
        self.num_requests_entry.grid(row=1, column=1, padx=5, pady=5)
        self.num_requests_entry.insert(0, "1")  # Default value
        
        # Send Button
        tk.Button(root, text="Send Requests", command=self.start_requests).grid(row=1, column=2, padx=5, pady=5)
        
        # Results Text Area
        self.results_text = tk.Text(root, height=15, width=60)
        self.results_text.grid(row=2, column=0, columnspan=3, padx=5, pady=5)
        
        # Queue for thread-safe updates to text widget
        self.result_queue = Queue()
        self.running = False
        
    def validate_url(self, url):
        parsed = urlparse(url)
        return bool(parsed.scheme and parsed.netloc and parsed.scheme in ['http', 'https'])
    
    def update_results(self):
        while self.running or not self.result_queue.empty():
            try:
                result = self.result_queue.get_nowait()
                self.results_text.insert(tk.END, result)
                self.root.update()
            except:
                break
        if self.running:
            self.root.after(100, self.update_results)
            
    def make_request(self, url, i):
        try:
            response = requests.get(url)
            result = f"Request {i+1}:\n"
            result += f"Status Code: {response.status_code}\n"
            result += f"Response Time: {response.elapsed.total_seconds():.2f} seconds\n"
            result += "-" * 50 + "\n"
            self.result_queue.put(result)
        except requests.exceptions.RequestException as e:
            self.result_queue.put(f"Request {i+1} failed: {str(e)}\n" + "-" * 50 + "\n")
        
    def start_requests(self):
        url = self.url_entry.get().strip()
        
        try:
            num_requests = int(self.num_requests_entry.get())
            if num_requests <= 0:
                raise ValueError("Number of requests must be positive")
        except ValueError as e:
            messagebox.showerror("Error", "Please enter a valid number of requests")
            return
            
        if not self.validate_url(url):
            messagebox.showerror("Error", "Please enter a valid HTTP or HTTPS URL")
            return
            
        self.results_text.delete(1.0, tk.END)
        self.running = True
        
        # Start the update loop
        self.update_results()
        
        # Create thread pool and submit requests
        def run_requests():
            with ThreadPoolExecutor(max_workers=10) as executor:
                for i in range(num_requests):
                    executor.submit(self.make_request, url, i)
            self.running = False
            
        threading.Thread(target=run_requests, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = RequestTester(root)
    root.mainloop()
