import re
from pathlib import Path

def parse_discord_export(file_path):
    """
    Parse Discord export text file and extract pure message content.
    Skips timestamps, authors, call logs, and header information.
    
    Args:
        file_path: Path to the Discord export .txt file
        
    Returns:
        List of cleaned message strings
    """
    messages = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip header lines
        if line.startswith('=') or line.startswith('Guild:') or line.startswith('Channel:'):
            i += 1
            continue
        
        # Look for message pattern: [timestamp] username
        message_pattern = r'^\[\d+/\d+/\d+\s+\d+:\d+\s+[AP]M\]\s+(.+)$'
        match = re.match(message_pattern, line)
        
        if match:
            username = match.group(1)
            i += 1
            
            # Next line should be the message content
            if i < len(lines):
                content = lines[i].strip()
                
                # Skip call logs and empty messages
                if content and not content.startswith('Started a call') and not content.startswith('{Embed}') and not content.startswith('http'):
                    # Handle multi-line messages (check if next line continues the message)
                    full_message = content
                    i += 1
                    
                    # Keep adding lines until we hit a new timestamp or empty line
                    while i < len(lines):
                        next_line = lines[i].strip()
                        if not next_line or re.match(message_pattern, next_line):
                            break
                        # Skip URLs and embed markers
                        if not next_line.startswith('http') and not next_line.startswith('{Embed}'):
                            full_message += ' ' + next_line
                        i += 1
                    
                    messages.append(full_message)
                else:
                    i += 1
            else:
                i += 1
        else:
            i += 1
    
    return messages


def parse_all_files_in_folder(folder_path):
    """
    Parse all .txt files in a folder and return combined messages.
    
    Args:
        folder_path: Path to folder containing Discord export .txt files
        
    Returns:
        Dictionary mapping filenames to lists of messages
    """
    folder = Path(folder_path)
    all_messages = {}
    
    for file_path in folder.glob('*.txt'):
        print(f"Parsing {file_path.name}...")
        messages = parse_discord_export(file_path)
        all_messages[file_path.name] = messages
        print(f"  Extracted {len(messages)} messages")
    
    return all_messages


if __name__ == '__main__':
    # Test the parser with the provided file
    test_file = 'attached_assets/Direct Messages - liv! [1072729769428398080]_1761063206293.txt'
    messages = parse_discord_export(test_file)
    
    print(f"\nTotal messages extracted: {len(messages)}")
    print("\nFirst 5 messages:")
    for i, msg in enumerate(messages[:5], 1):
        print(f"{i}. {msg}")
    
    print("\nLast 5 messages:")
    for i, msg in enumerate(messages[-5:], 1):
        print(f"{i}. {msg}")
