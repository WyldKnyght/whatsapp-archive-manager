"""
CSS generation for HTML chat export.
"""

from typing import Dict


class CSSGenerator:
    """
    Generates CSS styles for chat HTML.
    Single Responsibility: Only CSS generation.
    """
    
    @staticmethod
    def generate_base_css() -> str:
        """Generate base CSS styles."""
        return """
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #e5ddd5;
        }
        
        .chat-container {
            background-color: #f8f8f8;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .chat-header {
            text-align: center;
            padding-bottom: 20px;
            border-bottom: 1px solid #ddd;
            margin-bottom: 20px;
        }
        
        .chat-title {
            font-size: 24px;
            font-weight: bold;
            color: #075e54;
            margin: 0;
        }
        
        .chat-info {
            color: #666;
            font-size: 14px;
            margin-top: 5px;
        }
        
        .message {
            margin: 10px 0;
            padding: 8px 12px;
            border-radius: 8px;
            max-width: 70%;
            word-wrap: break-word;
            position: relative;
            clear: both;
        }
        
        .message.own {
            float: right;
            margin-left: auto;
        }
        
        .message.other {
            float: left;
            margin-right: auto;
        }
        
        .message-sender {
            font-weight: bold;
            font-size: 13px;
            margin-bottom: 2px;
        }
        
        .message-time {
            font-size: 11px;
            color: #888;
            margin-top: 4px;
        }
        
        .message-text {
            font-size: 14px;
            line-height: 1.4;
        }
        
        .message-attachment {
            margin-top: 8px;
        }
        
        .message-attachment img,
        .message-attachment video {
            max-width: 100%;
            border-radius: 5px;
        }
        
        .system-message {
            text-align: center;
            color: #888;
            font-size: 12px;
            font-style: italic;
            margin: 15px 0;
            clear: both;
        }
        
        .date-separator {
            text-align: center;
            color: #666;
            font-size: 12px;
            margin: 20px 0;
            clear: both;
        }
        
        .date-separator span {
            background-color: #fff;
            padding: 5px 15px;
            border-radius: 15px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        
        .clearfix::after {
            content: "";
            display: table;
            clear: both;
        }
        
        .attribution {
            text-align: center;
            color: #888;
            font-size: 11px;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
        }
        
        a {
            color: #075e54;
            text-decoration: none;
        }
        
        a:hover {
            text-decoration: underline;
        }
        """
    
    @staticmethod
    def generate_color_css(sender_color_map: Dict[str, str]) -> str:
        """
        Generate CSS for sender-specific colors.
        
        Args:
            sender_color_map: Dictionary mapping sender names to colors
            
        Returns:
            CSS string with color definitions
        """
        css = ""
        for sender, color in sender_color_map.items():
            # Create a safe CSS class name from sender name
            safe_class = CSSGenerator._create_safe_css_class(sender)
            css += f"\n.message.sender-{safe_class} {{\n"
            css += f"    background-color: {color};\n"
            css += "}\n"
        
        return css
    
    @staticmethod
    def _create_safe_css_class(name: str) -> str:
        """
        Create a safe CSS class name from a sender name.
        
        Args:
            name: Sender name
            
        Returns:
            Safe CSS class name
        """
        # Remove special characters and spaces, replace with hyphens
        import re
        safe = re.sub(r'[^a-zA-Z0-9_-]', '-', name)
        # Remove consecutive hyphens
        safe = re.sub(r'-+', '-', safe)
        # Remove leading/trailing hyphens
        safe = safe.strip('-')
        return safe.lower()
