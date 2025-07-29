#!/usr/bin/env python3
"""
Simple API key testing endpoint for the admin panel
"""

import json
import time
import random
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import sys

class APIKeyTestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Handle POST requests for API key testing"""
        if self.path == '/api/test-key':
            # Parse request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                key_name = data.get('keyName', 'Unknown')
                api_key = data.get('apiKey', '')
                provider = data.get('provider', 'Unknown')
                
                # Simulate API key testing with some realistic logic
                start_time = time.time()
                
                # Basic validation
                if not api_key or len(api_key) < 8:
                    result = {
                        'success': False,
                        'message': 'Invalid API key format',
                        'responseTime': int((time.time() - start_time) * 1000)
                    }
                else:
                    # Simulate different response times and success rates based on provider
                    if provider == 'OpenAI':
                        success_rate = 0.95
                        response_time = random.uniform(800, 1500)
                    elif provider == 'Anthropic':
                        success_rate = 0.90
                        response_time = random.uniform(1000, 2000)
                    elif provider == 'Google':
                        success_rate = 0.85
                        response_time = random.uniform(1200, 2500)
                    else:
                        success_rate = 0.80
                        response_time = random.uniform(1500, 3000)
                    
                    # Simulate the test delay
                    time.sleep(response_time / 1000)
                    
                    # Determine success based on simulated success rate
                    is_success = random.random() < success_rate
                    
                    if is_success:
                        result = {
                            'success': True,
                            'message': f'{provider} API key is valid and responding',
                            'responseTime': int(response_time)
                        }
                    else:
                        error_messages = [
                            'API key authentication failed',
                            'Rate limit exceeded',
                            'Service temporarily unavailable',
                            'Invalid permissions for this key'
                        ]
                        result = {
                            'success': False,
                            'message': random.choice(error_messages),
                            'responseTime': int(response_time)
                        }
                
                # Send response
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                self.end_headers()
                
                response_json = json.dumps(result)
                self.wfile.write(response_json.encode('utf-8'))
                
            except json.JSONDecodeError:
                self.send_error(400, 'Invalid JSON in request body')
            except Exception as e:
                self.send_error(500, f'Server error: {str(e)}')
        else:
            self.send_error(404, 'Endpoint not found')
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        """Override to reduce logging noise"""
        return

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8011
    server = HTTPServer(('localhost', port), APIKeyTestHandler)
    print(f"API Key Test server running on port {port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.shutdown()
