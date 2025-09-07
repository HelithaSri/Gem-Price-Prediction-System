from typing import Dict, List, Optional, Tuple

class GemStandardizer:
    # Standard tone values
    TONES = {
        'Vivid', 'Royal', 'Ice', 'Medium', 'Pastel', 'Light',
        'Dark', 'Deep', 'Intense', 'Hot'
    }

    # Standard basic colors
    BASIC_COLORS = {
        'Blue', 'Red', 'Pink', 'Yellow', 'Green', 'White',
        'Orange', 'Purple', 'Brown'
    }

    # Color modifiers
    MODIFIERS = {
        'Greenish', 'Bluish', 'Yellowish', 'Pinkish', 'Orangish',
        'Purplish', 'Reddish'
    }

    # Standard gem types and their variations
    GEM_TYPES = {
        'Sapphire': [
            'Blue Sapphire',
            'Pink Sapphire',
            'Yellow Sapphire',
            'White Sapphire',
            'Green Sapphire',
            'Orange Sapphire',
            'Teal Sapphire',
            'Padparadscha'
        ],
        'Ruby': ['Ruby'],
        'Emerald': ['Emerald'],
        'Alexandrite': ['Alexandrite'],
        'Chrysoberyl': ['Chrysoberyl'],
        'Tanzanite': ['Tanzanite'],
        'Aquamarine': ['Aquamarine'],
        'Other': []
    }

    @classmethod
    def standardize_color(cls, color_str: str) -> Dict[str, str]:
        """
        Split a color string into tone, primary color, and modifier components.
        
        Args:
            color_str: The color string to standardize (e.g., "Vivid Blue", "Greenish Blue")
            
        Returns:
            Dictionary with tone, color, and modifier values
        """
        if not color_str or not isinstance(color_str, str):
            return {'tone': '', 'color': '', 'modifier': ''}

        words = color_str.strip().split()
        result = {'tone': '', 'color': '', 'modifier': ''}

        # Handle simple cases
        if len(words) == 1:
            if words[0] in cls.BASIC_COLORS:
                result['color'] = words[0]
            return result

        # Handle complex cases
        for word in words:
            if word in cls.TONES:
                result['tone'] = word
            elif word in cls.BASIC_COLORS:
                result['color'] = word
            elif word in cls.MODIFIERS:
                result['modifier'] = word

        return result

    @classmethod
    def standardize_gem_type(cls, gem_type: str) -> Tuple[str, str]:
        """
        Standardize a gem type string into base type and variety.
        
        Args:
            gem_type: The gem type string to standardize
            
        Returns:
            Tuple of (base_type, variety)
        """
        if not gem_type or not isinstance(gem_type, str):
            return ('', '')

        # First try exact match
        for base_type, varieties in cls.GEM_TYPES.items():
            if gem_type in varieties:
                return (base_type, gem_type)
            if gem_type == base_type:
                return (base_type, '')

        # Handle special cases
        if 'Sapphire' in gem_type:
            color_prefix = gem_type.replace('Sapphire', '').strip()
            variety = f"{color_prefix}Sapphire" if color_prefix else 'Sapphire'
            return ('Sapphire', variety)

        # Default to Other category
        return ('Other', gem_type)

    @classmethod
    def get_color_options(cls) -> Dict[str, List[str]]:
        """
        Get all valid color options.
        
        Returns:
            Dictionary with tones, colors, and modifiers
        """
        return {
            'tones': sorted(list(cls.TONES)),
            'colors': sorted(list(cls.BASIC_COLORS)),
            'modifiers': sorted(list(cls.MODIFIERS))
        }

    @classmethod
    def get_gem_type_options(cls) -> Dict[str, List[str]]:
        """
        Get all valid gem type options.
        
        Returns:
            Dictionary with base types and their varieties
        """
        return {k: sorted(v) for k, v in cls.GEM_TYPES.items()}
