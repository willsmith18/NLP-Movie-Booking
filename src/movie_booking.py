from .chatbot import ChatBot
from .models import Movie, ShowTime, Booking, Intent
from datetime import datetime
from typing import Dict, Optional, List

class MovieBookingState:
    def __init__(self):
        self.selected_movie: Optional[Movie] = None
        self.selected_showtime: Optional[ShowTime] = None
        self.selected_seats: List[str] = []
        self.booking: Optional[Booking] = None
        self.current_step: str = "INIT"

class MovieBookingChatBot(ChatBot):
    def __init__(self):
        super().__init__()
        self.booking_state = MovieBookingState()
        
        # Load movie data (in practice, this would come from a database)
        self.movies: Dict[str, Movie] = self._load_movies()
        self.showtimes: Dict[str, ShowTime] = self._load_showtimes()
        self.bookings: Dict[str, Booking] = {}
        
        # Extend intent patterns
        self.intent_patterns.update(self._load_booking_intent_patterns())

    def _load_booking_intent_patterns(self) -> Dict[str, Dict[str, List[str]]]:
        return {
            'movie_search': {
                'patterns': ['show movies', 'what movies', 'available movies', 'movie list', 'find movie'],
                'responses': ['Here are the available movies:\n{movies_list}']
            },
            'movie_select': {
                'patterns': ['book', 'want to watch', 'select movie', 'choose movie'],
                'responses': ['You\'ve selected {movie_title}. Would you like to see available showtimes?']
            },
            'show_time_select': {
                'patterns': ['show times', 'available times', 'when', 'what time'],
                'responses': ['Here are the available showtimes for {movie_title}:\n{showtimes_list}']
            },
            'seat_select': {
                'patterns': ['select seat', 'choose seat', 'book seat', 'seat number'],
                'responses': ['Available seats for your selected show:\n{seats_list}']
            },
            'booking_confirm': {
                'patterns': ['confirm booking', 'book tickets', 'proceed', 'pay'],
                'responses': ['Booking confirmed! Your booking ID is {booking_id}']
            },
            'booking_cancel': {
                'patterns': ['cancel booking', 'cancel tickets', 'cancel reservation'],
                'responses': ['Your booking has been cancelled.']
            },
            'booking_status': {
                'patterns': ['booking status', 'my booking', 'check booking'],
                'responses': ['Your booking details:\n{booking_details}']
            }
        }

    def _load_movies(self) -> Dict[str, Movie]:
        # Sample data - in practice, this would come from a database
        return {
            "mov1": Movie("mov1", "The Matrix", 150, "English", "Sci-Fi"),
            "mov2": Movie("mov2", "Inception", 148, "English", "Sci-Fi"),
            "mov3": Movie("mov3", "Interstellar", 169, "English", "Sci-Fi")
        }

    def _load_showtimes(self) -> Dict[str, ShowTime]:
        # Sample data - in practice, this would come from a database
        return {
            "st1": ShowTime("st1", "mov1", 
                          datetime.now().replace(hour=14, minute=30),
                          ["A1", "A2", "B1", "B2"], 12.99),
            "st2": ShowTime("st2", "mov1",
                          datetime.now().replace(hour=18, minute=30),
                          ["A1", "A2", "B1", "B2"], 14.99)
        }

    def _handle_movie_search(self, user_input: str) -> str:
        movies_list = "\n".join(
            f"- {movie.title} ({movie.duration} mins, {movie.language})"
            for movie in self.movies.values()
        )
        return f"Here are the available movies:\n{movies_list}"

    def _handle_movie_select(self, user_input: str) -> str:
        # Extract movie title from user input
        for movie in self.movies.values():
            if movie.title.lower() in user_input.lower():
                self.booking_state.selected_movie = movie
                self.booking_state.current_step = "MOVIE_SELECTED"
                return f"You've selected {movie.title}. Would you like to see available showtimes?"
        
        return "I couldn't find that movie. Please select from the available movies list."

    def _handle_show_time_select(self, user_input: str) -> str:
        if not self.booking_state.selected_movie:
            return "Please select a movie first."

        available_showtimes = [
            st for st in self.showtimes.values()
            if st.movie_id == self.booking_state.selected_movie.id
        ]

        if not available_showtimes:
            return "No showtimes available for this movie."

        for showtime in available_showtimes:
            time_str = showtime.datetime.strftime("%I:%M %p")
            if time_str.lower() in user_input.lower():
                self.booking_state.selected_showtime = showtime
                self.booking_state.current_step = "SHOWTIME_SELECTED"
                return f"Selected showtime: {time_str}. Would you like to select seats?"

        # If no time was selected, show available times
        times_list = "\n".join(
            f"- {st.datetime.strftime('%I:%M %p')} ({len(st.available_seats)} seats available)"
            for st in available_showtimes
        )
        return f"Available showtimes:\n{times_list}"

    def _handle_seat_select(self, user_input: str) -> str:
        if not self.booking_state.selected_showtime:
            return "Please select a showtime first."

        # Extract seat numbers from user input
        requested_seats = []
        for seat in self.booking_state.selected_showtime.available_seats:
            if seat.lower() in user_input.lower():
                requested_seats.append(seat)

        if requested_seats:
            self.booking_state.selected_seats = requested_seats
            self.booking_state.current_step = "SEATS_SELECTED"
            total = len(requested_seats) * self.booking_state.selected_showtime.price
            return f"Selected seats: {', '.join(requested_seats)}. Total: ${total:.2f}. Would you like to confirm your booking?"

        # Show available seats
        seats_list = ", ".join(self.booking_state.selected_showtime.available_seats)
        return f"Available seats: {seats_list}"

    def _handle_booking_confirm(self, user_input: str) -> str:
        if not all([
            self.booking_state.selected_movie,
            self.booking_state.selected_showtime,
            self.booking_state.selected_seats
        ]):
            return "Please complete your selection first."

        # Create booking
        booking_id = f"BK{len(self.bookings) + 1}"
        total_amount = len(self.booking_state.selected_seats) * self.booking_state.selected_showtime.price
        
        booking = Booking(
            id=booking_id,
            user_name=self.user_name or "Guest",
            movie_id=self.booking_state.selected_movie.id,
            showtime_id=self.booking_state.selected_showtime.id,
            seats=self.booking_state.selected_seats,
            total_amount=total_amount,
            status="CONFIRMED",
            timestamp=datetime.now()
        )
        
        self.bookings[booking_id] = booking
        
        # Update available seats
        for seat in self.booking_state.selected_seats:
            self.booking_state.selected_showtime.available_seats.remove(seat)
        
        # Reset booking state
        self.booking_state = MovieBookingState()
        
        return (
            f"Booking confirmed!\n"
            f"Booking ID: {booking_id}\n"
            f"Movie: {self.movies[booking.movie_id].title}\n"
            f"Time: {self.showtimes[booking.showtime_id].datetime.strftime('%I:%M %p')}\n"
            f"Seats: {', '.join(booking.seats)}\n"
            f"Total: ${booking.total_amount:.2f}"
        )

    def _handle_booking_cancel(self, user_input: str) -> str:
        # Extract booking ID from input
        booking_id = None
        for word in user_input.split():
            if word.upper().startswith("BK"):
                booking_id = word.upper()
                break
        
        if not booking_id or booking_id not in self.bookings:
            return "Please provide a valid booking ID."
        
        booking = self.bookings[booking_id]
        if booking.status == "CANCELLED":
            return "This booking is already cancelled."
        
        # Return seats to available pool
        showtime = self.showtimes[booking.showtime_id]
        showtime.available_seats.extend(booking.seats)
        showtime.available_seats.sort()
        
        # Update booking status
        booking.status = "CANCELLED"
        
        return f"Booking {booking_id} has been cancelled."

    def _handle_booking_status(self, user_input: str) -> str:
        if not self.user_name:
            return "Please tell me your name first."
            
        user_bookings = [
            booking for booking in self.bookings.values()
            if booking.user_name == self.user_name
        ]
        
        if not user_bookings:
            return "You don't have any bookings."
            
        status_list = []
        for booking in user_bookings:
            movie = self.movies[booking.movie_id]
            showtime = self.showtimes[booking.showtime_id]
            status_list.append(
                f"Booking ID: {booking.id}\n"
                f"Movie: {movie.title}\n"
                f"Time: {showtime.datetime.strftime('%I:%M %p')}\n"
                f"Seats: {', '.join(booking.seats)}\n"
                f"Status: {booking.status}\n"
                f"Total: ${booking.total_amount:.2f}\n"
            )
        
        return "Your bookings:\n" + "\n".join(status_list)

    def _handle_intent(self, intent: Intent, user_input: str) -> str:
        """Extended handler for movie booking intents"""
        # First check booking-specific intents
        booking_handlers = {
            Intent.MOVIE_SEARCH: self._handle_movie_search,
            Intent.MOVIE_SELECT: self._handle_movie_select,
            Intent.SHOW_TIME_SELECT: self._handle_show_time_select,
            Intent.SEAT_SELECT: self._handle_seat_select,
            Intent.BOOKING_CONFIRM: self._handle_booking_confirm,
            Intent.BOOKING_CANCEL: self._handle_booking_cancel,
            Intent.BOOKING_STATUS: self._handle_booking_status,
        }
        
        if intent in booking_handlers:
            return booking_handlers[intent](user_input)
            
        # Fall back to parent class handlers for basic intents
        return super()._handle_intent(intent, user_input)

    def _get_capabilities_message(self) -> str:
        """Extended capabilities message including movie booking features"""
        return (
            super()._get_capabilities_message() + "\n"
            "I can also help you:\n"
            "1. Search for available movies\n"
            "2. Book movie tickets\n"
            "3. Select showtimes and seats\n"
            "4. Check your booking status\n"
            "5. Cancel bookings"
        )