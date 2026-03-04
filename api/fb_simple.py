from flask import Blueprint, request, jsonify
import requests
import os

fb = Blueprint('fb', __name__)

PAGE_TOKEN = os.environ.get("FB_PAGE_TOKEN", "YOUR_TOKEN")
VERIFY_TOKEN = "astra_simple_2024"

@fb.route('/fbhook', methods=['GET'])
def fbhook_get():
    verify_token = request.args.get('hub.verify_token')
    if verify_token == VERIFY_TOKEN:
        return request.args.get('hub.challenge')
    return "Invalid token", 403

@fb.route('/fbhook', methods=['POST'])
def fbhook_post():
    data = request.json
    
    if data.get('object') == 'page':
        for entry in data.get('entry', []):
            for event in entry.get('messaging', []):
                if event.get('message'):
                    sender = event['sender']['id']
                    text = event['message'].get('text', '')
                    
                    # رد بسيط
                    reply = "مرحباً! شكراً على رسالتك. هذا رد تلقائي من مساعد العيادة."
                    
                    # إرسال الرد
                    requests.post(
                        f"https://graph.facebook.com/v18.0/me/messages?access_token={PAGE_TOKEN}",
                        json={
                            "recipient": {"id": sender},
                            "message": {"text": reply}
                        }
                    )
    
    return "OK", 200
