import regex as re
import pandas as pd
from datetime import datetime
from typing import List, Dict, Tuple
import streamlit as st

class WhatsAppParser:
    """Parser for WhatsApp chat messages to extract user information and responses."""
    
    def __init__(self):
        # Turkish positive responses
        self.positive_patterns = [
            r'\b(geliyorum|gelirim|varım|varım|katılıyorum|katılırım|evet|tamam|ok|olur|geleceğim)\b',
            r'\b(yes|coming|will come|count me in|i\'m in)\b',
            r'\b(👍|✅|☑️|✓|👌|💪|⚽)\b',
            r'\b(ben\s+de\s+var|ben\s+varım|bende\s+varım)\b'
        ]
        
        # Turkish negative responses
        self.negative_patterns = [
            r'\b(gelemem|gelemiyorum|yokum|katılamam|katılamıyorum|hayır|olmaz|no|maalesef)\b',
            r'\b(can\'t|cannot|won\'t|will not|not coming|sorry)\b',
            r'\b(❌|❎|👎|😢|😞|🚫)\b',
            r'\b(maalesef\s+gelemem|üzgünüm\s+gelemem)\b'
        ]
        
        # Turkish maybe responses
        self.maybe_patterns = [
            r'\b(belki|muhtemelen|sanırım|galiba|bakacağım|deneyeceğim|emin\s+değilim)\b',
            r'\b(maybe|probably|might|not sure|will try|let me check)\b',
            r'\b(🤔|🤷|❓|❔|🤷‍♂️|🤷‍♀️)\b'
        ]
        
        # WhatsApp message pattern
        self.message_pattern = r'\[(\d{1,2}\/\d{1,2}\/\d{2,4},\s+\d{1,2}:\d{2}:\d{2}\s+(?:AM|PM))\]\s+([^:]+):\s+(.*)'
    
    def parse_messages(self, text: str) -> List[Dict]:
        """Parse WhatsApp messages and extract structured data."""
        messages = []
        
        # Split text into lines and process each line
        lines = text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Try to match WhatsApp message pattern
            match = re.match(self.message_pattern, line)
            
            if match:
                timestamp_str, sender, message = match.groups()
                
                # Clean sender name (remove phone numbers, extra spaces)
                sender = self._clean_name(sender)
                
                # Parse timestamp
                try:
                    timestamp = self._parse_timestamp(timestamp_str)
                except:
                    timestamp = datetime.now()
                
                messages.append({
                    'timestamp': timestamp,
                    'sender': sender,
                    'message': message.strip(),
                    'original_line': line
                })
        
        return messages
    
    def _clean_name(self, name: str) -> str:
        """Clean and normalize sender names."""
        # Remove common WhatsApp artifacts
        name = re.sub(r'\+\d+', '', name)  # Remove phone numbers
        name = re.sub(r'\s+', ' ', name)   # Normalize spaces
        name = name.strip()
        
        # Handle common patterns
        if name.startswith('~'):
            name = name[1:]
        
        return name.title()  # Capitalize properly
    
    def _parse_timestamp(self, timestamp_str: str) -> datetime:
        """Parse WhatsApp timestamp string."""
        # Try different timestamp formats
        formats = [
            '%m/%d/%y, %I:%M:%S %p',
            '%d/%m/%y, %H:%M:%S',
            '%m/%d/%Y, %I:%M:%S %p',
            '%d/%m/%Y, %H:%M:%S'
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(timestamp_str, fmt)
            except ValueError:
                continue
        
        # Fallback to current time
        return datetime.now()

class AttendanceTracker:
    """Track attendance based on parsed messages and detect responses."""
    
    def __init__(self):
        self.parser = WhatsAppParser()
    
    def extract_attendance(self, messages: List[Dict]) -> pd.DataFrame:
        """Extract attendance information from parsed messages."""
        attendance_data = []
        
        # Group messages by sender to get latest response
        sender_messages = {}
        
        for msg in messages:
            sender = msg['sender']
            if sender not in sender_messages:
                sender_messages[sender] = []
            sender_messages[sender].append(msg)
        
        # Analyze each sender's messages
        for sender, msgs in sender_messages.items():
            # Sort by timestamp to get chronological order
            msgs.sort(key=lambda x: x['timestamp'])
            
            # Analyze all messages for this sender
            response = self._analyze_responses(msgs)
            
            if response:
                # Get the most recent message for context
                latest_msg = msgs[-1]
                
                attendance_data.append({
                    'name': sender,
                    'response': response,
                    'message': latest_msg['message'],
                    'timestamp': latest_msg['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                    'message_count': len(msgs)
                })
        
        return pd.DataFrame(attendance_data)
    
    def _analyze_responses(self, messages: List[Dict]) -> str:
        """Analyze messages to determine attendance response."""
        # Combine all messages from this sender
        combined_text = ' '.join([msg['message'].lower() for msg in messages])
        
        # Count pattern matches
        positive_score = sum(len(re.findall(pattern, combined_text, re.IGNORECASE)) 
                            for pattern in self.parser.positive_patterns)
        negative_score = sum(len(re.findall(pattern, combined_text, re.IGNORECASE)) 
                            for pattern in self.parser.negative_patterns)
        maybe_score = sum(len(re.findall(pattern, combined_text, re.IGNORECASE)) 
                         for pattern in self.parser.maybe_patterns)
        
        # Determine response based on scores
        if positive_score > negative_score and positive_score > maybe_score:
            return 'Yes'
        elif negative_score > positive_score and negative_score > maybe_score:
            return 'No'
        elif maybe_score > 0:
            return 'Maybe'
        
        # If no clear pattern, try to detect based on context
        return self._contextual_analysis(combined_text)
    
    def _contextual_analysis(self, text: str) -> str:
        """Perform contextual analysis for unclear messages."""
        text = text.lower()
        
        # Look for specific Turkish phrases
        if any(phrase in text for phrase in ['geleceğim', 'orada olacağım', 'katılacağım']):
            return 'Yes'
        elif any(phrase in text for phrase in ['gidemem', 'olmaz', 'mümkün değil']):
            return 'No'
        elif any(phrase in text for phrase in ['emin değilim', 'bakacağım', 'sonra söylerim']):
            return 'Maybe'
        
        # Default to None if cannot determine
        return None

class RegistrationManager:
    """Manage player registration system with capacity limits."""
    
    def __init__(self):
        self.main_list_capacity = 10  # First 10 players - guaranteed to play
        self.total_capacity = 18      # Total players that can play
        
    def register_player(self, name: str, current_players: List[Dict]) -> Dict:
        """Register a new player with automatic list assignment."""
        from datetime import datetime
        
        # Check if player already registered
        for player in current_players:
            if player['name'].lower() == name.lower():
                return {
                    'success': False,
                    'message': f'{name} zaten kayıtlı!',
                    'player_list': current_players
                }
        
        # Determine position and list
        position = len(current_players) + 1
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Create new player entry
        new_player = {
            'name': name,
            'position': position,
            'timestamp': timestamp
        }
        
        # Add to list
        updated_list = current_players + [new_player]
        
        # Determine message based on position
        if position <= 10:
            message = f'{name} ana listeye eklendi! (Sıra: {position}/10) - Kesin oynayacaksınız! 🎯'
        elif position <= 18:
            message = f'{name} bekleme listesine eklendi! (Sıra: {position}/18) - Ana listeden biri gelmezse oynayacaksınız! ⏳'
        else:
            message = f'{name} yedek listesine eklendi! (Sıra: {position}) - 18 kişiden biri gelmezse sahaya alınacaksınız! 📝'
        
        return {
            'success': True,
            'message': message,
            'player_list': updated_list
        }
    
    def remove_player(self, name: str, current_players: List[Dict]) -> Dict:
        """Remove a player and reorder positions."""
        updated_list = [p for p in current_players if p['name'] != name]
        
        # Reorder positions
        for i, player in enumerate(updated_list):
            player['position'] = i + 1
        
        return {
            'success': True,
            'message': f'{name} kaydı silindi ve listeler yeniden sıralandı.',
            'player_list': updated_list
        }
    
    def reorder_positions(self, player_list: List[Dict]):
        """Reorder positions after removal."""
        for i, player in enumerate(player_list):
            player['position'] = i + 1
    
    def get_list_status(self, current_players: List[Dict]) -> Dict:
        """Get current status of all lists."""
        main_list = [p for p in current_players if p['position'] <= 10]
        waiting_list = [p for p in current_players if 10 < p['position'] <= 18]
        reserve_list = [p for p in current_players if p['position'] > 18]
        
        return {
            'main_list': main_list,
            'waiting_list': waiting_list,
            'reserve_list': reserve_list,
            'total_registered': len(current_players),
            'main_available': max(0, 10 - len(main_list)),
            'waiting_available': max(0, 18 - len(main_list) - len(waiting_list))
        }

class DataExporter:
    """Handle data export functionality."""
    
    @staticmethod
    def to_csv(df: pd.DataFrame) -> str:
        """Export DataFrame to CSV string."""
        return df.to_csv(index=False)
    
    @staticmethod
    def to_summary_text(df: pd.DataFrame) -> str:
        """Generate a summary text report."""
        total = len(df)
        yes_count = len(df[df['response'] == 'Yes'])
        maybe_count = len(df[df['response'] == 'Maybe'])
        no_count = len(df[df['response'] == 'No'])
        
        summary = f"""Futbol Sevenler - Attendance Summary
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📊 SUMMARY STATISTICS
Total Responses: {total}
Coming (Yes): {yes_count} ({yes_count/total*100:.1f}%)
Maybe: {maybe_count} ({maybe_count/total*100:.1f}%)
Not Coming (No): {no_count} ({no_count/total*100:.1f}%)

✅ COMING ({yes_count} people):
{chr(10).join([f"- {row['name']}" for _, row in df[df['response'] == 'Yes'].iterrows()])}

🤔 MAYBE ({maybe_count} people):
{chr(10).join([f"- {row['name']}" for _, row in df[df['response'] == 'Maybe'].iterrows()])}

❌ NOT COMING ({no_count} people):
{chr(10).join([f"- {row['name']}" for _, row in df[df['response'] == 'No'].iterrows()])}

📝 DETAILED RESPONSES:
"""
        
        for _, row in df.iterrows():
            summary += f"\n{row['name']} ({row['response']}): {row['message'][:50]}..."
        
        return summary

def validate_whatsapp_format(text: str) -> Tuple[bool, str]:
    """Validate if the input text appears to be WhatsApp chat format."""
    if not text.strip():
        return False, "No text provided"
    
    lines = text.strip().split('\n')
    whatsapp_lines = 0
    
    parser = WhatsAppParser()
    
    for line in lines:
        if re.match(parser.message_pattern, line):
            whatsapp_lines += 1
    
    if whatsapp_lines == 0:
        return False, "No WhatsApp message format detected. Please ensure messages follow the format: [date, time] Name: message"
    elif whatsapp_lines < len(lines) * 0.3:  # Less than 30% are proper WhatsApp messages
        return False, f"Only {whatsapp_lines} out of {len(lines)} lines appear to be WhatsApp messages"
    else:
        return True, f"Found {whatsapp_lines} WhatsApp messages"

# Utility functions for Streamlit components
def create_response_badge(response: str) -> str:
    """Create HTML badge for response status."""
    colors = {
        'Yes': '#28a745',
        'Maybe': '#ffc107', 
        'No': '#dc3545'
    }
    
    icons = {
        'Yes': '✅',
        'Maybe': '🤔',
        'No': '❌'
    }
    
    color = colors.get(response, '#6c757d')
    icon = icons.get(response, '❓')
    
    return f'<span style="background-color: {color}; color: white; padding: 0.2rem 0.5rem; border-radius: 10px; font-size: 0.8rem; font-weight: bold;">{icon} {response}</span>'