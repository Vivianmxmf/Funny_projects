import os
import requests
from typing import Dict, List
import json

class SingleChatbot:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:5000",  # Your website URL
        }
        
        # Chatbot Profile Settings
        self.profile = {
            "name": "Luna",
            "role": "AI Research Assistant",
            "expertise": [
                "Scientific Research",
                "Data Analysis",
                "Academic Writing",
                "Literature Review"
            ],
            "personality_traits": [
                "Professional",
                "Detail-oriented",
                "Patient",
                "Encouraging"
            ],
            "communication_style": "Clear, concise, and academic",
            "background": """Luna is an advanced AI research assistant with expertise in multiple scientific domains. 
            She specializes in helping researchers, students, and academics with their work."""
        }
        
        # Initialize conversation history
        self.conversation_history: List[Dict] = []
        
    def update_profile(self, new_profile: Dict):
        """Update chatbot profile settings"""
        self.profile.update(new_profile)
        
    def get_profile(self) -> Dict:
        """Get current chatbot profile"""
        return self.profile
        
    def generate_system_prompt(self) -> str:
        """Generate system prompt from profile"""
        return f"""You are {self.profile['name']}, {self.profile['role']}. 
        Background: {self.profile['background']}
        Expertise: {', '.join(self.profile['expertise'])}
        Communication Style: {self.profile['communication_style']}
        Please maintain this persona in all interactions."""
        
    def chat(self, user_input: str, model: str = "anthropic/claude-2") -> str:
        """Send message to chatbot and get response"""
        
        # Prepare messages
        messages = [
            {"role": "system", "content": self.generate_system_prompt()},
            *self.conversation_history,
            {"role": "user", "content": user_input}
        ]
        
        # Prepare request
        data = {
            "model": model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        try:
            # Make API call
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=data
            )
            response.raise_for_status()
            
            # Extract assistant's response
            result = response.json()
            assistant_message = result['choices'][0]['message']['content']
            
            # Update conversation history
            self.conversation_history.extend([
                {"role": "user", "content": user_input},
                {"role": "assistant", "content": assistant_message}
            ])
            
            return assistant_message
            
        except requests.exceptions.RequestException as e:
            return f"Error: {str(e)}"
            
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []

# Example usage
if __name__ == "__main__":
    # Initialize chatbot with your API key
    api_key = "YOUR_OPENROUTER_API_KEY"
    chatbot = SingleChatbot(api_key)
    
    # Optional: Update profile
    new_profile = {
        "name": "Dr. Watson",
        "role": "Medical AI Assistant",
        "expertise": ["Medicine", "Healthcare", "Medical Research"],
        "communication_style": "Professional and empathetic"
    }
    chatbot.update_profile(new_profile)
    
    # Example conversation
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['exit', 'quit']:
            break
            
        response = chatbot.chat(user_input)
        print(f"{chatbot.profile['name']}: {response}") 