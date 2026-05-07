#!/usr/bin/env python3
"""
MiniMax Image Generation API
Handles both Text-to-Image and Image-to-Image generation
"""

import os
import base64
import requests
from datetime import datetime

# API Configuration
MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY", "")
MINIMAX_API_URL = "https://api.minimax.io/v1/image_generation"

# Daily limits
DAILY_LIMIT = 10

def get_usage():
    """Get today's usage from file"""
    today = datetime.now().strftime("%Y-%m-%d")
    usage_file = "/tmp/minimax_image_usage.json"
    
    if os.path.exists(usage_file):
        with open(usage_file, 'r') as f:
            data = json.load(f)
            if data.get('date') == today:
                return data.get('count', 0)
    
    return 0

def increment_usage():
    """Increment today's usage"""
    today = datetime.now().strftime("%Y-%m-%d")
    usage_file = "/tmp/minimax_image_usage.json"
    
    current = get_usage()
    
    with open(usage_file, 'w') as f:
        json.dump({'date': today, 'count': current + 1}, f)

def generate_image(prompt, aspect_ratio="16:9", subject_reference=None):
    """Generate image using MiniMax API"""
    headers = {
        "Authorization": f"Bearer {MINIMAX_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "image-01",
        "prompt": prompt,
        "aspect_ratio": aspect_ratio,
        "response_format": "url"
    }
    
    if subject_reference:
        payload["subject_reference"] = subject_reference
    
    response = requests.post(MINIMAX_API_URL, headers=headers, json=payload, timeout=60)
    
    if response.status_code != 200:
        raise Exception(f"API Error: {response.status_code} - {response.text}")
    
    data = response.json()
    
    if 'data' not in data or 'image_base64' not in data['data'] and 'image_urls' not in data['data']:
        raise Exception("Invalid response from API")
    
    # Get image URLs
    image_urls = data['data'].get('image_urls', [])
    
    if not image_urls and 'image_base64' in data['data']:
        # If we got base64, we need to decode and return URL (or store locally)
        images = data['data']['image_base64']
        # Store images locally and return URLs
        saved_urls = []
        for i, img_b64 in enumerate(images):
            img_data = base64.b64decode(img_b64)
            filename = f"/tmp/image_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i}.jpg"
            with open(filename, 'wb') as f:
                f.write(img_data)
            saved_urls.append(f"/images/{os.path.basename(filename)}")
        
        return saved_urls
    
    return image_urls

# API Route for Flask/FastAPI
@app.route('/api/minimax/image', methods=['POST'])
def minimax_image_endpoint():
    """API endpoint for image generation"""
    try:
        # Check rate limit
        usage = get_usage()
        if usage >= DAILY_LIMIT:
            return jsonify({
                'error': 'Daily limit reached',
                'message': f'Has alcanzado tu límite de {DAILY_LIMIT} imágenes por día'
            }), 429
        
        # Parse request
        data = request.get_json()
        
        prompt = data.get('prompt')
        if not prompt:
            return jsonify({'error': 'Prompt requerido'}), 400
        
        aspect_ratio = data.get('aspect_ratio', '16:9')
        subject_reference = data.get('subject_reference')
        
        # Generate
        image_urls = generate_image(prompt, aspect_ratio, subject_reference)
        
        # Increment usage
        increment_usage()
        
        return jsonify({
            'success': True,
            'image_url': image_urls[0] if image_urls else None,
            'image_urls': image_urls,
            'usage_today': get_usage(),
            'remaining': DAILY_LIMIT - get_usage()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    print("MiniMax Image Generator Module")
    print(f"Daily limit: {DAILY_LIMIT}")
    print(f"API Key configured: {'Yes' if MINIMAX_API_KEY else 'No'}")