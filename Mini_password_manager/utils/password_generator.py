import string
import random

class PasswordGenerator:
    @staticmethod
    def generate_password(length=12, use_uppercase=True, use_lowercase=True,
                         use_numbers=True, use_symbols=True):
        """Generate a secure random password"""
        characters = ''
        if use_uppercase:
            characters += string.ascii_uppercase
        if use_lowercase:
            characters += string.ascii_lowercase
        if use_numbers:
            characters += string.digits
        if use_symbols:
            characters += string.punctuation
            
        if not characters:
            characters = string.ascii_letters + string.digits
            
        password = ''.join(random.choice(characters) for _ in range(length))
        return password
    
    @staticmethod
    def check_strength(password):
        """Check password strength and return score and feedback"""
        score = 0
        feedback = []
        
        if len(password) >= 12:
            score += 2
        elif len(password) >= 8:
            score += 1
        else:
            feedback.append("Password is too short")
            
        if any(c.isupper() for c in password):
            score += 1
        else:
            feedback.append("Add uppercase letters")
            
        if any(c.islower() for c in password):
            score += 1
        else:
            feedback.append("Add lowercase letters")
            
        if any(c.isdigit() for c in password):
            score += 1
        else:
            feedback.append("Add numbers")
            
        if any(c in string.punctuation for c in password):
            score += 1
        else:
            feedback.append("Add special characters")
            
        return score, feedback 