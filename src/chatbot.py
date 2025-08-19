import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords, wordnet
from nltk.stem import WordNetLemmatizer
import string
import json
import os
import time
import re
import time as time_module
from typing import Optional, Dict, List, Any
from .models import Intent, ConversationTurn

class ChatBot:
    def __init__(self):
        # Initialize NLP tools
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        self.punctuation = set(string.punctuation)
        
        # Initialize conversation state
        self.user_data_file = "user_data.json"
        self.user_name = self.load_user_data()
        self.conversation_history: List[ConversationTurn] = []
        self.session_start = time_module.time()
        self.awaiting_name_confirmation = False

        # Load intent patterns from separate config file
        self.intent_patterns = self._load_intent_patterns()

    def _load_intent_patterns(self) -> Dict[str, Dict[str, List[str]]]:
        """Load intent patterns from configuration file"""
        return {
            'greeting': {
                'patterns': ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening'],
                'responses': ['Hello! How can I help you today?', 'Hi there! What can I do for you?']
            },
            'farewell': {
                'patterns': ['bye', 'goodbye', 'see you', 'farewell', 'quit', 'exit'],
                'responses': ['Goodbye! Have a great day!', 'Bye! Come back if you need anything else.']
            },
            'name_set': {
                'patterns': ['my name is', 'call me', 'i am called', '{name}'],
                'responses': ['Nice to meet you, {name}!', 'Hello {name}, pleasure to meet you!']
            },
            'name_get': {
                'patterns': ['what is my name', 'who am i', 'do you know my name'],
                'responses': ['Your name is {name}!', 'You\'re {name}!']
            },
            'name_change': {
                'patterns': ['change my name', 'call me something else', 'i want a different name'],
                'responses': ['I\'ll now call you {name} instead of {old_name}!']
            },
            'help': {
                'patterns': ['help', 'what can you do', 'how do you work'],
                'responses': ['I can help you with:\n- Setting and remembering your name\n- Basic conversation\n- Task assistance\nJust let me know what you need!']
            },
            'confirm': {
            'patterns': ['yes', 'yeah', 'yep', 'correct', 'that\'s right', 'that is me', 'still me', 'it\'s me'],
            'responses': ['Welcome back! How can I help you today?']
            },
            'deny': {
            'patterns': ['no', 'nope', 'not me', 'different person', 'someone else', 'wrong person'],
            'responses': ['Oh, I apologize! Would you like to tell me your name?']
            }
        }

    def load_user_data(self) -> Optional[str]:
        """Load user data from JSON file"""
        try:
            if os.path.exists(self.user_data_file):
                with open(self.user_data_file, 'r') as f:
                    data = json.load(f)
                    return data.get('name')
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading user data: {e}")
            # Create backup of corrupted file
            if os.path.exists(self.user_data_file):
                os.rename(self.user_data_file, f"{self.user_data_file}.bak")
        return None

    def save_user_data(self) -> bool:
        """Save user data to JSON file"""
        try:
            data = {'name': self.user_name}
            with open(self.user_data_file, 'w') as f:
                json.dump(data, f)
            return True
        except IOError as e:
            print(f"Error saving user data: {e}")
            return False

    def preprocess_text(self, text: str) -> List[str]:
        """Preprocess user input text"""
        try:
            text = text.lower().strip()
            tokens = word_tokenize(text)
            tokens = [
                self.lemmatizer.lemmatize(token)
                for token in tokens
                if token not in self.stop_words and token not in self.punctuation
            ]
            return tokens
        except Exception as e:
            print(f"Error preprocessing text: {e}")
            return []

    def match_intent(self, text: str) -> Intent:
        """Match input text to an intent with improved confidence scoring"""
        try:
            tokens = self.preprocess_text(text)
            if not tokens:
                return Intent.UNKNOWN

            intent_scores = {}
            
            for intent_name in Intent:
                if intent_name == Intent.UNKNOWN:
                    continue
                    
                patterns = self.intent_patterns.get(intent_name.name.lower(), {}).get('patterns', [])
                max_pattern_score = 0
                
                for pattern in patterns:
                    # Exact match check
                    if pattern.lower() in text.lower():
                        max_pattern_score = 1.0
                        break
                        
                    # Token similarity check
                    pattern_tokens = self.preprocess_text(pattern)
                    if pattern_tokens:
                        similarity = self._calculate_token_similarity(tokens, pattern_tokens)
                        max_pattern_score = max(max_pattern_score, similarity)
                
                intent_scores[intent_name] = max_pattern_score
            
            # Get the intent with highest score above threshold
            best_intent, best_score = max(intent_scores.items(), key=lambda x: x[1])
            return best_intent if best_score >= 0.2 else Intent.UNKNOWN
            
        except Exception as e:
            print(f"Error matching intent: {e}")
            return Intent.UNKNOWN

    def _calculate_token_similarity(self, tokens1: List[str], tokens2: List[str]) -> float:
        """Calculate similarity between two sets of tokens"""
        if not tokens1 or not tokens2:
            return 0.0
            
        similarities = []
        for t1 in tokens1:
            token_similarities = []
            for t2 in tokens2:
                similarity = self.get_word_similarity(t1, t2)
                if similarity:
                    token_similarities.append(similarity)
            if token_similarities:
                similarities.append(max(token_similarities))
                
        return sum(similarities) / len(similarities) if similarities else 0.0

    def process_input(self, user_input: str) -> str:
        """Process user input and generate appropriate response"""
        try:
            intent = self.match_intent(user_input)
            
            # Log the interaction
            self.conversation_history.append(ConversationTurn(
                timestamp=time.time(),
                user_input=user_input,
                response="",  # Will be set after processing
                intent=intent
            ))
            
            response = self._handle_intent(intent, user_input)
            
            # Update the response in history
            self.conversation_history[-1].response = response
            return response
            
        except Exception as e:
            print(f"Error processing input: {e}")
            return "I'm having trouble processing your request. Could you try again?"

    def _handle_intent(self, intent: Intent, user_input: str) -> str:
        """Handle different intents with improved logic"""
        if self.awaiting_name_confirmation:
            return self._handle_name_confirmation(intent, user_input)
            
        handlers = {
            Intent.NAME_SET: self._handle_name_set,
            Intent.NAME_GET: self._handle_name_get,
            Intent.FAREWELL: self._handle_farewell,
            Intent.GREETING: self._handle_greeting,
            Intent.HELP: self._handle_help,
            Intent.UNKNOWN: lambda _: "I'm not sure what you mean. Could you rephrase that?"
        }
        
        handler = handlers.get(intent, handlers[Intent.UNKNOWN])
        return handler(user_input)
    
    def get_word_similarity(self, word1: str, word2: str) -> float:
        """Calculate word similarity using WordNet"""
        try:
            synsets1 = wordnet.synsets(word1)
            synsets2 = wordnet.synsets(word2)
            
            if not synsets1 or not synsets2:
                return 0.0
                
            similarity = synsets1[0].path_similarity(synsets2[0])
            return similarity if similarity is not None else 0.0
        except Exception:
            return 0.0

    def _get_welcome_message(self) -> str:
        """Generate appropriate welcome message based on user state"""
        if self.user_name:
            self.awaiting_name_confirmation = True
            return f"Am I still talking to {self.user_name}?"
        return "Hello! I'm your assistant. What's your name?"

    def _handle_name_confirmation(self, intent: Intent, user_input: str) -> str:
        """Handle name confirmation flow"""
        self.awaiting_name_confirmation = False
        
        if intent == Intent.CONFIRM:
            capabilities = self._get_capabilities_message()
            return f"Welcome back {self.user_name}! {capabilities}"
        elif intent == Intent.DENY:
            old_name = self.user_name
            self.user_name = None
            self.save_user_data()
            return "I apologize for the confusion. Would you like to tell me your name?"
        elif intent == Intent.NAME_SET:
            name = self.extract_name(user_input)
            if name:
                old_name = self.user_name
                self.user_name = name
                self.save_user_data()
                capabilities = self._get_capabilities_message()
                return f"Nice to meet you, {name}! {capabilities}"
        
        # Default case for unclear response
        self.user_name = None
        self.save_user_data()
        return "I apologize for the confusion. Would you like to tell me your name?"

    def extract_name(self, text: str) -> Optional[str]:
        """Extract name from input text with improved pattern matching"""
        patterns = [
            r"my name is (\w+)",
            r"call me (\w+)",
            r"i am (\w+)",
            r"i'm (\w+)",
            r"name'?s (\w+)"
        ]
        
        text = text.lower()
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).capitalize()
        
        # If no pattern matches, try to find a capitalized word
        words = text.split()
        for word in words:
            if word.capitalize() != word.lower():  # Check if word is potentially a name
                return word.capitalize()
        
        return None

    def _handle_name_set(self, user_input: str) -> str:
        """Handle name setting intent"""
        name = self.extract_name(user_input)
        if name:
            old_name = self.user_name
            self.user_name = name
            self.save_user_data()
            capabilities = self._get_capabilities_message()
            if old_name:
                return f"I'll now call you {name} instead of {old_name}! {capabilities}"
            return f"Nice to meet you, {name}!"
        return "I didn't catch your name. Could you say it again?"

    def _handle_name_get(self, user_input: str) -> str:
        """Handle name getting intent"""
        if self.user_name:
            return f"Your name is {self.user_name}!"
        return "I don't know your name yet. Would you like to tell me?"

    def _handle_farewell(self, user_input: str) -> str:
        """Handle farewell intent"""
        if self.user_name:
            return f"Goodbye {self.user_name}! Have a great day!"
        return "Goodbye! Have a great day!"

    def _handle_greeting(self, user_input: str) -> str:
        """Handle greeting intent"""
        if self.user_name:
            return f"Hello {self.user_name}! How can I help you today?"
        return "Hello! Would you like to tell me your name?"

    def _handle_help(self, user_input: str) -> str:
        """Handle help intent"""
        help_message = (
            "I can help you with:\n"
            "1. Remembering your name and personalizing our conversation\n"
            "2. Basic conversation and greetings\n"
            "3. Providing information about my capabilities\n"
            f"{'4. Continuing our previous conversation' if self.user_name else '4. Getting to know you better'}"
        )
        return help_message
    
    def _get_capabilities_message(self) -> str:
        """Get a friendly message about the chatbot's capabilities"""
        return (
            "I'm here to help you! I can:\n"
            "1. Remember your name and personalize our conversation\n"
            "2. Engage in friendly chat and greetings\n"
            "3. Answer questions about what I can do\n"
            "Just let me know what you'd like to talk about!"
        )

    def run(self):
        """Main chat loop"""
        try:
            welcome_msg = self._get_welcome_message()
            print("Chatbot:", welcome_msg)
            
            while True:
                try:
                    user_input = input("You: ").strip()
                    
                    if not user_input:
                        print("Chatbot: I didn't catch that. Could you please say something?")
                        continue
                    
                    response = self.process_input(user_input)
                    print("Chatbot:", response)
                    
                    if self.match_intent(user_input) == Intent.FAREWELL:
                        break
                        
                except KeyboardInterrupt:
                    print("\nChatbot: Goodbye!")
                    break
                except Exception as e:
                    print(f"Error in chat loop: {e}")
                    print("Chatbot: I encountered an error. Let's continue our conversation.")
                    
        finally:
            # Save conversation history or perform cleanup
            self.save_user_data()
