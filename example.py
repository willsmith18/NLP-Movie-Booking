#!/usr/bin/env python3
"""
Simple example showing how to use the NLP Movie Booking Chatbot

This script demonstrates the core functionality without requiring
interactive input - perfect for quick testing or demonstrations.
"""

from src import MovieBookingChatBot

def run_conversation_example():
    """Run a pre-scripted conversation to show chatbot capabilities"""
    
    print("🎬 NLP Movie Booking Chatbot - Example Usage")
    print("=" * 50)
    print("This example shows a complete movie booking conversation\n")
    
    # Create chatbot instance
    bot = MovieBookingChatBot()
    
    # Example conversation flow
    conversation = [
        "Hello there!",
        "My name is Alex Demo",
        "What can you help me with?",
        "Show me available movies",
        "I want to book The Matrix",
        "What showtimes are available?",
        "I'll take the 2:30 PM show", 
        "I want seat A1",
        "Yes, confirm my booking",
        "What's my booking status?",
        "Thank you, goodbye!"
    ]
    
    print("Starting conversation...\n")
    
    for i, user_input in enumerate(conversation, 1):
        print(f"👤 User: {user_input}")
        
        # Process input and get response
        response = bot.process_input(user_input)
        print(f"🤖 Bot: {response}")
        
        # Add separator between exchanges for readability
        if i < len(conversation):
            print("-" * 40)
        print()
    
    # Show final booking status
    if bot.bookings:
        print("📋 Final Booking Summary:")
        booking = list(bot.bookings.values())[0]
        print(f"   Booking ID: {booking.id}")
        print(f"   Movie: {bot.movies[booking.movie_id].title}")
        print(f"   Seats: {', '.join(booking.seats)}")
        print(f"   Total: ${booking.total_amount:.2f}")
        print(f"   Status: {booking.status}")

def demonstrate_intent_recognition():
    """Show how the chatbot recognizes different types of user input"""
    
    print("\n" + "=" * 50)
    print("🎯 Intent Recognition Examples")
    print("=" * 50)
    
    bot = MovieBookingChatBot()
    
    test_inputs = [
        ("Hello there!", "Greeting"),
        ("Show me movies", "Movie Search"),
        ("Book The Matrix", "Movie Selection"),
        ("I want seat A1", "Seat Selection"), 
        ("My name is John", "Name Setting"),
        ("What's my booking?", "Booking Status"),
        ("Cancel my reservation", "Booking Cancellation"),
        ("Help me please", "Help Request"),
        ("Goodbye!", "Farewell")
    ]
    
    print("Testing different types of user input:\n")
    
    for user_input, expected_category in test_inputs:
        intent = bot.match_intent(user_input)
        print(f"Input: '{user_input}'")
        print(f"Detected Intent: {intent.name}")
        print(f"Category: {expected_category}")
        print("-" * 30)

def show_api_usage():
    """Demonstrate programmatic usage of the chatbot"""
    
    print("\n" + "=" * 50) 
    print("💻 Programmatic API Usage")
    print("=" * 50)
    
    bot = MovieBookingChatBot()
    
    print("1. Initialize chatbot and set user name:")
    bot.user_name = "API User"
    print(f"   User name set to: {bot.user_name}\n")
    
    print("2. Get available movies:")
    movies_response = bot._handle_movie_search("")
    print(f"   {movies_response}\n")
    
    print("3. Check conversation history:")
    print(f"   Conversation turns logged: {len(bot.conversation_history)}")
    
    print("4. Access movie data directly:")
    for movie_id, movie in bot.movies.items():
        print(f"   {movie.title} ({movie.duration} mins, {movie.genre})")

def main():
    """Main example runner"""
    
    try:
        # Run the main conversation example
        run_conversation_example()
        
        # Show intent recognition capabilities  
        demonstrate_intent_recognition()
        
        # Show API usage
        show_api_usage()
        
        print("\n🎉 Example completed successfully!")
        print("\nTo run the interactive chatbot, use: python src/main.py")
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("Make sure you're running from the project root directory")
        print("and that NLTK data is downloaded:")
        print("python -c \"import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet')\"")
        
    except Exception as e:
        print(f"❌ Error running example: {e}")
        print("Please check that all dependencies are installed correctly")

if __name__ == "__main__":
    main()