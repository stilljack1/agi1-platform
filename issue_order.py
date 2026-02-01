import requests
import sys
import json

def send_order(executive, intent):
    url = "http://127.0.0.1:8000/directive/issue"
    payload = {
        "executive": executive,
        "intent": intent,
        "priority": 10
    }
    try:
        res = requests.post(url, json=payload)
        if res.status_code == 200:
            print(f"✅ Directive Issued: {json.dumps(res.json(), indent=2)}")
        else:
            print(f"❌ Error: {res.text}")
    except Exception as e:
        print(f"❌ Connection Failed: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 issue_order.py <EXECUTIVE_NAME> <INTENT_STRING>")
        print('Example: python3 issue_order.py JACK "Analyze global cloud spend"')
        sys.exit(1)
    
    send_order(sys.argv[1], " ".join(sys.argv[2:]))
