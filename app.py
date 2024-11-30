from flask import Flask, jsonify, render_template, request
import os
from angelBot import AngelBot
from devilBot import DevilBot
from conversations import ConversationManager
from logger_config import setup_logger
import random
from twitter_auth import setup_twitter_routes

# Initialize logger
logger = setup_logger('flask_app')

app = Flask(__name__)

# Use environment variable for API key
api_key = os.getenv('GROK_API_KEY')
if not api_key:
    logger.error("No API key found in environment variables")
    raise ValueError("GROK_API_KEY environment variable is required")

# Initialize bots and conversation manager
try:
    logger.info("Initializing bots and conversation manager")
    angel = AngelBot(api_key)
    devil = DevilBot(api_key)
    conversation_manager = ConversationManager(angel, devil)
    conversation_manager.start()
except Exception as e:
    logger.error(f"Error initializing bots: {e}")
    raise

# Original single-message generation endpoints
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
        logger.error(f"Error generating message: {e}")
        return jsonify({'error': str(e)}), 500
@app.route('/conversation_stats/<conversation_id>', methods=['GET'])
def get_conversation_stats(conversation_id):
    try:
        stats = conversation_manager.get_conversation_timing_stats(conversation_id)
        if stats:
            return jsonify({
                'conversation_id': conversation_id,
                'statistics': stats
            })
        return jsonify({'error': 'Conversation not found'}), 404
    except Exception as e:
        logger.error(f"Error getting conversation stats: {e}")
        return jsonify({'error': str(e)}), 500
# Original response generation endpoint
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
        logger.error(f"Error generating response: {e}")
        return jsonify({'error': str(e)}), 500

# Original conversation generation endpoint
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
        logger.error(f"Error generating conversation: {e}")
        return jsonify({'error': str(e)}), 500

# New managed conversation endpoints
@app.route('/start_conversation', methods=['GET'])
def start_new_conversation():
    try:
        conversation_id = conversation_manager.start_conversation()
        return jsonify({'status': 'success', 'conversation_id': conversation_id})
    except Exception as e:
        logger.error(f"Error starting conversation: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/get_conversation/<conversation_id>', methods=['GET'])
def get_conversation(conversation_id):
    try:
        conversation = conversation_manager.tracker.conversations.get(conversation_id)
        if conversation:
            return jsonify({'conversation': conversation})
        return jsonify({'error': 'Conversation not found'}), 404
    except Exception as e:
        logger.error(f"Error retrieving conversation: {e}")
        return jsonify({'error': str(e)}), 500

# New endpoint to list all active conversations
@app.route('/list_conversations', methods=['GET'])
def list_conversations():
    try:
        conversations = {
            id: {
                'start_time': conv['start_time'],
                'message_count': len(conv['messages']),
                'status': conv['status'],
                'initiator': conv['initiator']
            }
            for id, conv in conversation_manager.tracker.conversations.items()
        }
        return jsonify({'conversations': conversations})
    except Exception as e:
        logger.error(f"Error listing conversations: {e}")
        return jsonify({'error': str(e)}), 500

# New endpoint to stop a specific conversation
@app.route('/stop_conversation/<conversation_id>', methods=['POST'])
def stop_conversation(conversation_id):
    try:
        if conversation_id in conversation_manager.tracker.conversations:
            conversation_manager.tracker.conversations[conversation_id]['status'] = 'completed'
            return jsonify({'status': 'success', 'message': 'Conversation stopped'})
        return jsonify({'error': 'Conversation not found'}), 404
    except Exception as e:
        logger.error(f"Error stopping conversation: {e}")
        return jsonify({'error': str(e)}), 500
setup_twitter_routes(app)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 3000)))