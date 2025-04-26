import requests
import json
from datetime import datetime
import os
import re
from bs4 import BeautifulSoup
import time

class BostonBlackEventsScraper:
    def __init__(self):
        # API keys (you'll need to register for these)
        self.eventbrite_token = os.environ.get('EVENTBRITE_TOKEN', 'YOUR_EVENTBRITE_API_TOKEN')
        self.meetup_token = os.environ.get('MEETUP_TOKEN', 'YOUR_MEETUP_API_TOKEN')
        
        # Keywords to filter events (can be customized)
        self.keywords = [
            'black', 'african', 'african american', 'diaspora', 
            'afro', 'urban', 'soul', 'heritage', 'afrocentric',
            'melanin', 'juneteenth', 'kwanzaa', 'black history'
        ]
        
        # Boston neighborhoods for location filtering
        self.boston_areas = [
            'roxbury', 'dorchester', 'mattapan', 'jamaica plain',
            'roslindale', 'hyde park', 'south end', 'back bay',
            'fenway', 'boston', 'cambridge', 'somerville'
        ]
        
        # Output file path
        self.output_file = 'events_data.json'

    def fetch_eventbrite_events(self):
        """Fetch events from Eventbrite API"""
        print("Fetching events from Eventbrite...")
        events = []
        
        # Base URL for Eventbrite API
        url = "https://www.eventbriteapi.com/v3/events/search/"
        
        # Parameters for Boston area events
        params = {
            'location.address': 'Boston, MA',
            'location.within': '25mi',
            'expand': 'venue,organizer,ticket_availability',
            'page_size': 50,  # Maximum allowed by API
        }
        
        headers = {"Authorization": f"Bearer {self.eventbrite_token}"}
        
        try:
            # Initial request
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            events.extend(data['events'])
            
            # Paginate through results if needed
            page_count = data['pagination']['page_count']
            for page in range(2, min(page_count + 1, 5)):  # Limit to 5 pages to avoid rate limiting
                params['page'] = page
                response = requests.get(url, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
                events.extend(data['events'])
                time.sleep(1)  # Be nice to the API
            
            return self._process_eventbrite_events(events)
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching from Eventbrite: {e}")
            return []

    def _process_eventbrite_events(self, raw_events):
        """Process and filter Eventbrite events"""
        filtered_events = []
        
        for event in raw_events:
            # Extract event details
            try:
                event_name = event['name']['text'].lower()
                description = event['description']['text'].lower() if 'description' in event and 'text' in event['description'] else ''
                
                # Check if event matches our keywords
                if any(keyword in event_name or keyword in description for keyword in self.keywords):
                    # Format the event information
                    start_time = datetime.strptime(event['start']['local'], "%Y-%m-%dT%H:%M:%S")
                    
                    # Create venue info
                    venue = event.get('venue', {})
                    venue_name = venue.get('name', 'TBA') if venue else 'TBA'
                    venue_address = f"{venue.get('address', {}).get('address_1', '')}, {venue.get('address', {}).get('city', 'Boston')}" if venue and 'address' in venue else 'TBA'
                    
                    # Get ticket info
                    ticket_info = event.get('ticket_availability', {})
                    is_free = ticket_info.get('is_free', False)
                    has_available_tickets = ticket_info.get('has_available_tickets', True)
                    
                    # Get image if available
                    image_url = event.get('logo', {}).get('original', {}).get('url', '') if 'logo' in event and event['logo'] else ''
                    
                    filtered_event = {
                        'id': event['id'],
                        'name': event['name']['text'],
                        'description': event['description']['text'] if 'description' in event and 'text' in event['description'] else '',
                        'summary': self._generate_summary(event['description']['text']) if 'description' in event and 'text' in event['description'] else '',
                        'start_date': start_time.strftime("%Y-%m-%d"),
                        'start_time': start_time.strftime("%H:%M:%S"),
                        'display_date': start_time.strftime("%a, %b %d • %I:%M %p"),
                        'url': event['url'],
                        'venue_name': venue_name,
                        'venue_address': venue_address,
                        'is_free': is_free,
                        'has_available_tickets': has_available_tickets,
                        'image_url': image_url,
                        'source': 'eventbrite'
                    }
                    
                    filtered_events.append(filtered_event)
            except (KeyError, ValueError) as e:
                # Skip events with missing required fields
                continue
                
        return filtered_events

    def fetch_meetup_events(self):
        """Fetch events from Meetup API"""
        print("Fetching events from Meetup...")
        # Implement Meetup API integration here
        # Similar structure to Eventbrite function
        return []

    def scrape_boston_calendar(self):
        """Scrape events from The Boston Calendar website"""
        print("Scraping The Boston Calendar...")
        events = []
        url = "https://www.thebostoncalendar.com/"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            event_elements = soup.select('.event-list-item')
            
            for element in event_elements:
                try:
                    title_elem = element.select_one('.event-title')
                    if not title_elem:
                        continue
                        
                    title = title_elem.text.strip()
                    description = element.select_one('.event-description').text.strip() if element.select_one('.event-description') else ''
                    
                    # Combined text for keyword matching
                    combined_text = (title + ' ' + description).lower()
                    
                    # Check if event matches our keywords
                    if any(keyword in combined_text for keyword in self.keywords):
                        # Extract date and time
                        date_elem = element.select_one('.event-date')
                        date_text = date_elem.text.strip() if date_elem else ''
                        
                        # Extract venue
                        venue_elem = element.select_one('.event-venue')
                        venue = venue_elem.text.strip() if venue_elem else 'TBA'
                        
                        # Extract URL
                        url_elem = element.select_one('a')
                        event_url = url_elem['href'] if url_elem and 'href' in url_elem.attrs else ''
                        if event_url and not event_url.startswith('http'):
                            event_url = 'https://www.thebostoncalendar.com' + event_url
                        
                        # Parse date (this would need to be adjusted based on the actual format)
                        try:
                            # Example format: "Saturday, May 4, 2024 | 8:00PM"
                            date_parts = date_text.split('|')
                            date_str = date_parts[0].strip()
                            time_str = date_parts[1].strip() if len(date_parts) > 1 else ''
                            
                            # Convert to datetime object (adjust format as needed)
                            date_format = "%A, %B %d, %Y"
                            date_obj = datetime.strptime(date_str, date_format)
                            display_date = date_obj.strftime("%a, %b %d")
                            
                            if time_str:
                                display_date += f" • {time_str}"
                        except ValueError:
                            display_date = date_text
                        
                        event = {
                            'id': f"bostoncal-{hash(title)}",
                            'name': title,
                            'description': description,
                            'summary': self._generate_summary(description),
                            'display_date': display_date,
                            'venue_name': venue,
                            'venue_address': venue,
                            'url': event_url,
                            'is_free': 'free' in combined_text,
                            'has_available_tickets': True,
                            'image_url': '',
                            'source': 'bostoncalendar'
                        }
                        
                        events.append(event)
                        
                except Exception as e:
                    # Skip this event if there's an error
                    continue
                    
            return events
            
        except requests.exceptions.RequestException as e:
            print(f"Error scraping The Boston Calendar: {e}")
            return []

    def _generate_summary(self, description, max_length=150):
        """Generate a short summary from a longer description"""
        if not description:
            return ""
            
        # Clean up HTML tags if present
        clean_text = re.sub(r'<[^>]+>', '', description)
        
        # Get first few sentences
        sentences = re.split(r'(?<=[.!?])\s+', clean_text)
        summary = ""
        
        for sentence in sentences:
            if len(summary) + len(sentence) <= max_length:
                summary += sentence + " "
            else:
                break
                
        return summary.strip()

    def run(self):
        """Run the full scraping process"""
        all_events = []
        
        # Fetch events from different sources
        eventbrite_events = self.fetch_eventbrite_events()
        meetup_events = self.fetch_meetup_events()
        boston_cal_events = self.scrape_boston_calendar()
        
        # Combine all events
        all_events.extend(eventbrite_events)
        all_events.extend(meetup_events)
        all_events.extend(boston_cal_events)
        
        # Sort events by date
        all_events.sort(key=lambda x: x.get('start_date', '9999-99-99') + x.get('start_time', '00:00:00'))
        
        # Save to JSON file
        with open(self.output_file, 'w') as f:
            json.dump(all_events, f, indent=2)
            
        print(f"Saved {len(all_events)} events to {self.output_file}")
        
        # Generate HTML from template
        self.generate_html(all_events)
        
    def generate_html(self, events):
        """Generate HTML from events data"""
        print("Generating HTML...")
        
        # Read HTML template (you would create this separately)
        try:
            with open('template.html', 'r') as f:
                template = f.read()
                
            # Generate event cards HTML
            event_cards = ""
            for event in events:
                card = f"""
                <div class="event-card">
                    <div class="event-image" style="background-image: url('{event['image_url'] or '/api/placeholder/400/320'}')"></div>
                    <div class="event-details">
                        <div class="event-date">{event['display_date']}</div>
                        <h3 class="event-title">{event['name']}</h3>
                        <div class="event-location">{event['venue_name']}</div>
                        <p class="event-description">{event['summary']}</p>
                        <a href="{event['url']}" class="event-link" target="_blank">{'Get Tickets' if not event['is_free'] else 'RSVP'}</a>
                    </div>
                </div>
                """
                event_cards += card
                
            # Replace placeholder in template
            html = template.replace('<!-- EVENT_CARDS_PLACEHOLDER -->', event_cards)
            
            # Update the last updated date
            current_date = datetime.now().strftime("%B %d, %Y")
            html = html.replace('<!-- LAST_UPDATED_DATE -->', current_date)
            
            # Write to index.html
            with open('index.html', 'w') as f:
                f.write(html)
                
            print("HTML generated successfully!")
            
        except Exception as e:
            print(f"Error generating HTML: {e}")

if __name__ == "__main__":
    scraper = BostonBlackEventsScraper()
    scraper.run()