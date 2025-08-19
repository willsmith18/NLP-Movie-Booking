"""
NLP Conversational Chatbot with Movie Booking Capabilities

A sophisticated conversational AI system that demonstrates natural language
processing, intent recognition, and state management for movie booking tasks.

Author: William Smith
Institution: University of Nottingham
"""

from src import MovieBookingChatBot

def main():
    """Main entry point for the chatbot application"""
    print("🎬 NLP Movie Booking Chatbot")
    print("=" * 50)
    print("Features:")
    print("• Natural language understanding with NLTK")
    print("• Intent recognition with semantic similarity")
    print("• Movie booking with seat selection")
    print("• Persistent conversation state")
    print("=" * 50)
    print("Type 'help' to see what I can do, or 'bye' to exit.")
    print()
    
    try:
        bot = MovieBookingChatBot()
        bot.run()
    except KeyboardInterrupt:
        print("\n👋 Goodbye! Thanks for using the chatbot!")
    except Exception as e:
        print(f"❌ Error starting chatbot: {e}")
        print("Please make sure NLTK data is downloaded:")
        print("python -c \"import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet')\"")

if __name__ == "__main__":
    main()