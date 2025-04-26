# event_generator.py
import json
import os
from datetime import datetime

def generate_html():
    """Generate HTML from sample event data"""
    print("Generating HTML...")
    
    # Load sample data
    try:
        with open('sample_events.json', 'r') as f:
            events = json.load(f)
    except:
        # Use hardcoded events if file doesn't exist
        events = [
            {
                "id": "sample-1",
                "name": "Black Excellence Gala",
                "description": "Annual celebration honoring community leaders and entrepreneurs making an impact in Boston.",
                "summary": "Annual celebration honoring community leaders and entrepreneurs.",
                "display_date": "Sat, May 3 • 7:00 PM",
                "venue_name": "Roxbury Cultural Center",
                "venue_address": "1234 Washington St, Boston",
                "url": "#",
                "is_free": False,
                "image_url": ""
            },
            {
                "id": "sample-2",
                "name": "Diaspora Music Festival",
                "description": "Celebrating the sounds of the African diaspora featuring local artists and international performers.",
                "summary": "Celebrating the sounds of the African diaspora.",
                "display_date": "Sun, May 4 • 1:00 PM",
                "venue_name": "Franklin Park",
                "venue_address": "Franklin Park, Boston",
                "url": "#",
                "is_free": False,
                "image_url": ""
            },
            {
                "id": "sample-3",
                "name": "Black Authors Book Club",
                "description": "Monthly book discussion featuring works by contemporary Black authors.",
                "summary": "Monthly book discussion featuring works by contemporary Black authors.",
                "display_date": "Thu, May 8 • 6:30 PM",
                "venue_name": "Frugal Bookstore",
                "venue_address": "Roxbury, Boston",
                "url": "#",
                "is_free": True,
                "image_url": ""
            }
        ]
    
    # Generate event cards HTML
    event_cards = ""
    for event in events:
        ticket_text = 'RSVP' if event.get('is_free', False) else 'Get Tickets'
        card = f"""
        <div class="event-card">
            <div class="event-image"></div>
            <div class="event-details">
                <div class="event-date">{event['display_date']}</div>
                <h3 class="event-title">{event['name']}</h3>
                <div class="event-location">{event['venue_name']}</div>
                <p class="event-description">{event.get('summary', '')}</p>
                <a href="{event['url']}" class="event-link">{ticket_text}</a>
            </div>
        </div>
        """
        event_cards += card
    
    # Generate full HTML
    current_date = datetime.now().strftime("%B %d, %Y")
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Boston Black Events Guide</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <header>
        <div class="container">
            <h1>Boston Black Events Guide</h1>
            <p class="subtitle">Connecting the community to cultural events, celebrations, and gatherings</p>
        </div>
    </header>
    
    <div class="container">
        <div class="update-info">
            Last updated: {current_date}
        </div>
        
        <div class="categories">
            <button class="category-btn active">All Events</button>
            <button class="category-btn">Music</button>
            <button class="category-btn">Arts & Culture</button>
            <button class="category-btn">Community</button>
            <button class="category-btn">Food</button>
            <button class="category-btn">Business</button>
            <button class="category-btn">Education</button>
        </div>
        
        <div class="events-container">
            {event_cards}
        </div>
        
        <div class="newsletter">
            <h2>Never Miss an Event</h2>
            <p>Subscribe to our weekly newsletter to get the latest events delivered to your inbox.</p>
            <div class="form-group">
                <input type="email" placeholder="Enter your email">
                <button>Subscribe</button>
            </div>
        </div>
    </div>
    
    <footer>
        <div class="container">
            <p>© 2025 Boston Black Events Guide | <a href="#">About</a> | <a href="#">Contact</a> | <a href="#">Submit an Event</a></p>
        </div>
    </footer>
    
    <script src="script.js"></script>
</body>
</html>
    """
    
    # Write HTML to file
    with open('index.html', 'w') as f:
        f.write(html)
    
    print("HTML file generated successfully!")

if __name__ == "__main__":
    generate_html()