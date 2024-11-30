from flask import Flask, jsonify, render_template, request, redirect, session, url_for
import os
import json
import random
import asyncio
from functools import wraps
from angelBot import AngelBot
from devilBot import DevilBot
from conversations import ConversationManager
from logger_config import setup_logger
from twitter_auth import setup_twitter_routes, TwitterAuthManager
from urllib.parse import urlencode
import secrets

# Initialize logger
logger = setup_logger('flask_app')

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', secrets.token_hex(16))

# Constants
CALLBACK_URL = "https://devsangels.onrender.com/callback"
TWITTER_AUTH_SUCCESS_URL = "https://devsangels.onrender.com/twitter/auth/success"
TWITTER_AUTH_FAILURE_URL = "https://devsangels.onrender.com/twitter/auth/failure"

def init_app():
    """Initialize application components with proper error handling"""
    # Use environment variable for API key
    api_key = os.getenv('GROK_API_KEY')
    if not api_key:
        logger.error("No API key found in environment variables")
        raise ValueError("GROK_API_KEY environment variable is required")

    try:
        logger.info("Initializing bots and conversation manager")
        angel = AngelBot(api_key)
        devil = DevilBot(api_key)
        conversation_manager = ConversationManager(angel, devil)
        twitter_auth_manager = TwitterAuthManager()
        
        return angel, devil, conversation_manager, twitter_auth_manager
    except Exception as e:
        logger.error(f"Error initializing application components: {e}")
        raise

# Initialize application components
angel, devil, conversation_manager, twitter_auth_manager = init_app()
conversation_manager.start()

def async_route(f):
    """Decorator to handle async routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return asyncio.run(f(*args, **kwargs))
        except Exception as e:
            logger.error(f"Async route error: {e}")
            return jsonify({'error': str(e)}), 500
    return decorated_function

# Enhanced error handler
@app.errorhandler(Exception)
def handle_error(error):
    logger.error(f"Unhandled error: {error}")
    return jsonify({
        'error': str(error),
        'type': error.__class__.__name__
    }), getattr(error, 'code', 500)

# Twitter OAuth Routes
@app.route('/twitter/auth/<bot_type>')
def twitter_auth(bot_type):
    try:
        if bot_type not in ['angel', 'devil']:
            return jsonify({'error': 'Invalid bot type'}), 400

        auth_url = twitter_auth_manager.get_auth_url(bot_type, CALLBACK_URL)
        session['bot_type'] = bot_type
        return redirect(auth_url)
    except Exception as e:
        logger.error(f"Twitter auth error: {e}")
        return redirect(TWITTER_AUTH_FAILURE_URL)

@app.route('/callback')
def twitter_callback():
    try:
        bot_type = session.get('bot_type')
        if not bot_type:
            raise ValueError("No bot type in session")

        oauth_token = request.args.get('oauth_token')
        oauth_verifier = request.args.get('oauth_verifier')
        
        if not oauth_token or not oauth_verifier:
            raise ValueError("Missing OAuth parameters")

        twitter_auth_manager.handle_callback(
            bot_type, 
            oauth_token, 
            oauth_verifier,
            angel if bot_type == 'angel' else devil
        )
        
        return redirect(TWITTER_AUTH_SUCCESS_URL)
    except Exception as e:
        logger.error(f"Twitter callback error: {e}")
        return redirect(TWITTER_AUTH_FAILURE_URL)

# Message Generation Routes
@app.route('/generate/<bot_type>', methods=['GET'])
@async_route
async def generate_message(bot_type):
    try:
        if bot_type.lower() == 'angel':
            response = await angel.generate_response()
        elif bot_type.lower() == 'devil':
            response = await devil.generate_response()
        else:
            return jsonify({'error': 'Invalid bot type'}), 400
            
        return jsonify({'message': response})
    except Exception as e:
        logger.error(f"Error generating message: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/respond/<bot_type>/<message>', methods=['GET'])
@async_route
async def respond_to_message(bot_type, message):
    try:
        if bot_type.lower() == 'angel':
            response = await angel.generate_response(message)
        elif bot_type.lower() == 'devil':
            response = await devil.generate_response(message)
        else:
            return jsonify({'error': 'Invalid bot type'}), 400
            
        return jsonify({'message': response})
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        return jsonify({'error': str(e)}), 500

# Conversation Management Routes
@app.route('/start_conversation', methods=['GET'])
@async_route
async def start_new_conversation():
    try:
        conversation_id = await conversation_manager.start_conversation()
        return jsonify({
            'status': 'success', 
            'conversation_id': conversation_id
        })
    except Exception as e:
        logger.error(f"Error starting conversation: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/get_conversation/<conversation_id>', methods=['GET'])
def get_conversation(conversation_id):
    try:
        conversation = conversation_manager.tracker.conversations.get(conversation_id)
        if not conversation:
            return jsonify({'error': 'Conversation not found'}), 404
        return jsonify({'conversation': conversation})
    except Exception as e:
        logger.error(f"Error retrieving conversation: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/list_conversations', methods=['GET'])
def list_conversations():
    try:
        conversations = {
            id: {
                'start_time': conv['start_time'].isoformat(),
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

@app.route('/stop_conversation/<conversation_id>', methods=['POST'])
def stop_conversation(conversation_id):
    try:
        if conversation_id not in conversation_manager.tracker.conversations:
            return jsonify({'error': 'Conversation not found'}), 404
            
        conversation_manager.tracker.conversations[conversation_id]['status'] = 'completed'
        return jsonify({
            'status': 'success',
            'message': 'Conversation stopped'
        })
    except Exception as e:
        logger.error(f"Error stopping conversation: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/conversation_stats/<conversation_id>', methods=['GET'])
def get_conversation_stats(conversation_id):
    try:
        stats = conversation_manager.get_conversation_timing_stats(conversation_id)
        if not stats:
            return jsonify({'error': 'Conversation not found'}), 404
        return jsonify({
            'conversation_id': conversation_id,
            'statistics': stats
        })
    except Exception as e:
        logger.error(f"Error getting conversation stats: {e}")
        return jsonify({'error': str(e)}), 500

# Status and Health Check Routes
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'components': {
            'angel_bot': bool(angel),
            'devil_bot': bool(devil),
            'conversation_manager': bool(conversation_manager),
            'twitter_auth': bool(twitter_auth_manager)
        }
    })

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if asyncio.iscoroutine(obj):
            return str(obj)
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        return super().default(obj)

app.json_encoder = CustomJSONEncoder

if __name__ == "__main__":
    port = int(os.getenv('PORT', 3000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    # Ensure all required environment variables are set
    required_vars = [
        'GROK_API_KEY',
        'TWITTER_ANGEL_API_KEY',
        'TWITTER_ANGEL_API_SECRET',
        'TWITTER_DEVIL_API_KEY',
        'TWITTER_DEVIL_API_SECRET'
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug,
        use_reloader=debug
    )