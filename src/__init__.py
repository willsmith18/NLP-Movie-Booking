"""
NLP Conversational Chatbot Package

A conversational AI system with natural language processing capabilities
and movie booking functionality.
"""

__version__ = "1.0.0"
__author__ = "William Smith"

from .chatbot import ChatBot
from .movie_booking import MovieBookingChatBot
from .models import Intent, Movie, ShowTime, Booking

__all__ = [
    'ChatBot',
    'MovieBookingChatBot', 
    'Intent',
    'Movie',
    'ShowTime',
    'Booking'
]