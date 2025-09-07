from typing import Dict, List, Optional, Tuple

class GemStandardizer:
    # Standard tone values
    TONES = {
        'Vivid', 'Royal', 'Ice', 'Medium', 'Pastel', 'Light',
        'Dark', 'Deep', 'Intense', 'Hot'
    }

    # Standard basic colors - extracted from complex color descriptions
    BASIC_COLORS = {
        'Blue', 'Red', 'Pink', 'Yellow', 'Green', 'White',
        'Orange', 'Purple', 'Brown', 'Grey', 'Black'
    }

    # Color modifiers
    MODIFIERS = {
        'Greenish', 'Bluish', 'Yellowish', 'Pinkish', 'Orangish',
        'Purplish', 'Reddish'
    }

    # Standard gem types and their variations - only types with sufficient data (200+ records)
    GEM_TYPES = {
        'Sapphire': [
            'Blue Sapphire',
            'Pink Sapphire', 
            'Yellow Sapphire',
            'White Sapphire',
            'Green Sapphire',
            'Orange Sapphire',
            'Teal Sapphire',
            'Padparadscha',
            'Purple Sapphire'
        ],
        'Spinel': [
            'Blue Spinel',
            'Pink Spinel',
            'Red Spinel',
            'Purple Spinel',
            'Cobalt Spinel'
        ],
        'Garnet': [
            'Rhodolite Garnet',
            'Hessonite Garnet', 
            'Almandine Garnet',
            'Spessartite Garnet',
            'Red Garnet',
            'Orange Garnet'
        ],
        'Moonstone': ['Moonstone'],
        'Zircon': ['Blue Zircon', 'White Zircon', 'Yellow Zircon'],
        'Citrine': ['Citrine'],
        'Chrysoberyl': ['Chrysoberyl', 'Alexandrite']
    }

    # Gem type grouping - map specific types to their base category
    GEM_TYPE_MAPPING = {
        # Garnet family
        'Rhodolite Garnet': 'Garnet',
        'Hessonite Garnet': 'Garnet', 
        'Almandine Garnet': 'Garnet',
        'Spessartite Garnet': 'Garnet',
        'Garnet': 'Garnet',
        
        # Spinel family
        'Cobalt Spinel': 'Spinel',
        'Spinel': 'Spinel',
        
        # Chrysoberyl family
        'Alexandrite': 'Chrysoberyl',
        'Chrysoberyl': 'Chrysoberyl',
        
        # Other single-type categories
        'Sapphire': 'Sapphire',
        'Moonstone': 'Moonstone',
        'Zircon': 'Zircon', 
        'Citrine': 'Citrine'
    }

    @classmethod
    def extract_basic_color(cls, color_str: str) -> str:
        """
        Extract basic color from complex color descriptions.
        Examples: 'Pinkish Purple' -> 'Purple', 'Bluish Green' -> 'Green'
        
        Args:
            color_str: The complex color string
            
        Returns:
            Basic color string or empty if not found
        """
        if not color_str or not isinstance(color_str, str):
            return ''
        
        color_str = color_str.strip()
        
        # Direct match first
        if color_str in cls.BASIC_COLORS:
            return color_str
        
        # Look for basic colors in the string, prioritize the last one mentioned
        found_colors = []
        for basic_color in cls.BASIC_COLORS:
            if basic_color in color_str:
                found_colors.append((color_str.index(basic_color), basic_color))
        
        if found_colors:
            # Return the last mentioned color (usually the primary)
            found_colors.sort(reverse=True)
            return found_colors[0][1]
        
        # Special cases
        special_cases = {
            'Padparadscha': 'Orange',
            'Color Change': 'Purple',
            'Bi Color': 'Yellow',  # Default for bi-color
            'Rainbow': 'Yellow',   # Default for rainbow
            'Golden': 'Yellow',
            'Swiss Blue': 'Blue',
            'Sky Blue': 'Blue',
            'Watermelon': 'Pink',
            'Smoky': 'Grey'
        }
        
        for special, basic in special_cases.items():
            if special in color_str:
                return basic
        
        return ''

    @classmethod
    def standardize_treatment(cls, treatment_str: str) -> str:
        """
        Standardize treatment descriptions, filtering out 'Not Specified'.
        
        Args:
            treatment_str: The treatment string to standardize
            
        Returns:
            Standardized treatment string or empty if should be filtered
        """
        if not treatment_str or not isinstance(treatment_str, str):
            return ''
        
        treatment = treatment_str.strip()
        
        # Filter out unspecified treatments
        if treatment in ['Not Specified', 'Unknown', '']:
            return ''
        
        # Standardization mapping
        treatment_mapping = {
            'Heat Treated': 'Heat Treated',
            'No Enhancement': 'No Enhancement',
            'Heated': 'Heat Treated',
            'Heat': 'Heat Treated',
            'Traditional Heat': 'Heat Treated',
            'Unheated': 'No Enhancement',
            'No Treatment': 'No Enhancement',
            'Natural': 'No Enhancement',
            'Untreated': 'No Enhancement',
            'Not Treated': 'No Enhancement',
            'None': 'No Enhancement',
            'Beryllium Diffused': 'Beryllium Diffused',
            'Vapor-Infused Coating': 'Vapor-Infused Coating',
            'Irradiation': 'Irradiation'
        }
        
        return treatment_mapping.get(treatment, treatment)
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
        Groups similar gem types (e.g., all garnets under 'Garnet').
        
        Args:
            gem_type: The gem type string to standardize
            
        Returns:
            Tuple of (base_type, variety)
        """
        if not gem_type or not isinstance(gem_type, str):
            return ('', '')

        gem_type = gem_type.strip()
        
        # Check if it's in our mapping (for grouping)
        if gem_type in cls.GEM_TYPE_MAPPING:
            base_type = cls.GEM_TYPE_MAPPING[gem_type]
            variety = gem_type if gem_type != base_type else ''
            return (base_type, variety)

        # Check if it's a known variety
        for base_type, varieties in cls.GEM_TYPES.items():
            if gem_type in varieties:
                return (base_type, gem_type)
            if gem_type == base_type:
                return (base_type, '')

        # Handle Sapphire variations
        if 'Sapphire' in gem_type:
            return ('Sapphire', gem_type)
            
        # Handle Garnet variations
        if 'Garnet' in gem_type:
            return ('Garnet', gem_type)
            
        # Handle Spinel variations  
        if 'Spinel' in gem_type:
            return ('Spinel', gem_type)

        # If not in our supported types, return empty (will be filtered out)
        return ('', '')

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
        Get all valid gem type options - only types with sufficient data (200+ records).
        
        Returns:
            Dictionary with base types and their varieties
        """
        return {k: sorted(v) for k, v in cls.GEM_TYPES.items()}
    
    @classmethod
    def get_filtered_gem_types_from_dataset(cls, df) -> Dict[str, List[str]]:
        """
        Get gem types from dataset, filtered by count and grouped appropriately.
        Only includes gem types with 200+ records (after grouping).
        
        Args:
            df: DataFrame with gem data
            
        Returns:
            Dictionary with base types and their varieties from actual data
        """
        # Get all gem types and their counts
        gem_type_counts = df['Gem Type'].value_counts().to_dict()
        
        # Group similar gem types and sum their counts
        grouped_counts = {}
        varieties_by_base = {}
        
        for gem_type, count in gem_type_counts.items():
            base_type, variety = cls.standardize_gem_type(gem_type)
            
            if base_type:  # Only include supported types
                if base_type not in grouped_counts:
                    grouped_counts[base_type] = 0
                    varieties_by_base[base_type] = []
                
                grouped_counts[base_type] += count
                if variety and variety not in varieties_by_base[base_type]:
                    varieties_by_base[base_type].append(variety)
                elif not variety and gem_type not in varieties_by_base[base_type]:
                    varieties_by_base[base_type].append(gem_type)
        
        # Filter by 200+ record requirement
        filtered_types = {}
        for base_type, total_count in grouped_counts.items():
            if total_count >= 200:
                filtered_types[base_type] = sorted(varieties_by_base[base_type])
        
        return filtered_types
