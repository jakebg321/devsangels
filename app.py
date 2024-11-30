from flask import Flask, jsonify, render_template, request
import os
from angelBot import AngelBot
from devilBot import DevilBot
import random
from logger_config import setup_logger

# Initialize logger
logger = setup_logger('flask_app')

app = Flask(__name__)

# Use environment variable for API key
api_key = os.getenv('GROK_API_KEY')
if not api_key:
    logger.error("No API key found in environment variables")
    raise ValueError("GROK_API_KEY environment variable is required")

# Initialize bots
try:
    logger.info("Initializing bots")
    angel = AngelBot(api_key)
    devil = DevilBot(api_key)
except Exception as e:
    logger.error(f"Error initializing bots: {e}")
    raise
@app.route('/generate/<bot_type>', methods=['GET'])
def generate_message(bot_type):
    try:
        if bot_type.lower() == 'angel':
            response = angel.generate_response()
        elif bot_type.lower() == 'devil':
            response = devil.generate_response()
        else:
            return jsonify({'error': 'Invalid bot type'}), 400
            
        return jsonify({'message': response})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/respond/<bot_type>/<message>', methods=['GET'])
def respond_to_message(bot_type, message):
    try:
        if bot_type.lower() == 'angel':
            response = angel.generate_response(message)
        elif bot_type.lower() == 'devil':
            response = devil.generate_response(message)
        else:
            return jsonify({'error': 'Invalid bot type'}), 400
            
        return jsonify({'message': response})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/conversation', methods=['GET'])
def generate_conversation():
    try:
        # Randomly choose who starts
        starter = random.choice(['angel', 'devil'])
        current_speaker = starter
        
        conversation = []
        num_exchanges = random.randint(1, 5)
        
        # Run the conversation
        for _ in range(num_exchanges):
            if current_speaker == 'angel':
                response = angel.generate_response(conversation[-1]['message'] if conversation else None)
            else:
                response = devil.generate_response(conversation[-1]['message'] if conversation else None)
                
            conversation.append({
                'speaker': current_speaker,
                'message': response
            })
            
            current_speaker = 'devil' if current_speaker == 'angel' else 'angel'
            
        return jsonify({'conversation': conversation})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 3000)))