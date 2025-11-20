"""
Core prompt enhancement logic with heuristics and analysis.
"""
import re
from typing import List, Dict


class PromptEnhancer:
    """
    Core prompt enhancement logic using heuristics and pattern analysis.
    """

    ENHANCEMENT_MODES = {
        "basic": "Improve clarity and add key details",
        "detailed": "Comprehensive enhancement with examples and context",
        "creative": "Expand creatively with vivid descriptions",
        "technical": "Optimize for technical accuracy and precision",
    }

    def __init__(self):
        self.vague_words = {
            'write': ['write clearly', 'compose', 'create a well-structured'],
            'make': ['create', 'develop', 'build'],
            'do': ['implement', 'execute', 'perform'],
            'get': ['retrieve', 'obtain', 'extract'],
            'show': ['display', 'present', 'demonstrate'],
            'thing': ['element', 'component', 'item'],
            'good': ['high-quality', 'excellent', 'well-crafted'],
            'bad': ['poor-quality', 'inadequate', 'substandard'],
            'nice': ['appealing', 'well-designed', 'elegant'],
            'really': ['very', 'significantly', 'substantially'],
        }

    def analyze_prompt(self, prompt: str) -> Dict[str, any]:
        """
        Analyze a prompt and identify improvement areas.

        Args:
            prompt: The prompt to analyze

        Returns:
            Dictionary with analysis results
        """
        analysis = {
            "length": len(prompt.split()),
            "char_count": len(prompt),
            "has_question": "?" in prompt,
            "has_specifics": self._check_specificity(prompt),
            "has_context": self._check_context(prompt),
            "has_constraints": self._check_constraints(prompt),
            "vague_words_found": self._find_vague_words(prompt),
            "improvement_areas": self._identify_improvements(prompt),
        }
        return analysis

    def _check_specificity(self, prompt: str) -> bool:
        """Check if prompt has specific details."""
        specificity_indicators = [
            r'\d+', r'(how|what|when|where|why)',
            r'(specific|particular|exact)', r'(example|case|scenario)',
        ]
        return any(re.search(pattern, prompt, re.IGNORECASE) for pattern in specificity_indicators)

    def _check_context(self, prompt: str) -> bool:
        """Check if prompt provides context."""
        context_indicators = [
            r'(for|to|audience|user|reader|background)',
            r'(scenario|situation|context|setting)',
        ]
        return any(re.search(pattern, prompt, re.IGNORECASE) for pattern in context_indicators)

    def _check_constraints(self, prompt: str) -> bool:
        """Check if prompt specifies constraints."""
        constraint_indicators = [
            r'(length|format|style|tone|limit|maximum)',
            r'(word|character|sentence|paragraph)',
            r'(json|markdown|csv|html|xml)',
        ]
        return any(re.search(pattern, prompt, re.IGNORECASE) for pattern in constraint_indicators)

    def _find_vague_words(self, prompt: str) -> List[str]:
        """Find vague words in the prompt."""
        found = []
        lower_prompt = prompt.lower()
        for vague_word in self.vague_words.keys():
            if re.search(rf'\b{vague_word}\b', lower_prompt):
                found.append(vague_word)
        return found

    def _identify_improvements(self, prompt: str) -> List[str]:
        """Identify areas for improvement."""
        improvements = []

        if len(prompt.split()) < 10:
            improvements.append("Prompt is brief - consider adding more context")

        vague = self._find_vague_words(prompt)
        if vague:
            improvements.append(f"Vague words found: {', '.join(vague)}")

        if not self._check_specificity(prompt):
            improvements.append("Add specific details or examples")

        if not self._check_context(prompt):
            improvements.append("Specify target audience or use case")

        if not self._check_constraints(prompt):
            improvements.append("Consider specifying format or constraints")

        if not re.search(r'[.!?:]$', prompt):
            improvements.append("Add proper punctuation")

        return improvements

    def get_enhancement_suggestions(self, prompt: str, mode: str = "detailed") -> List[str]:
        """
        Get specific enhancement suggestions based on mode.

        Args:
            prompt: The prompt to enhance
            mode: Enhancement mode (basic, detailed, creative, technical)

        Returns:
            List of specific suggestions
        """
        analysis = self.analyze_prompt(prompt)
        suggestions = []

        if mode == "basic":
            if analysis["vague_words_found"]:
                suggestions.append(
                    f"Replace vague words ({', '.join(analysis['vague_words_found'])}) with more specific terms"
                )
            if analysis["char_count"] < 50:
                suggestions.append("Add more detail to make the prompt clearer")

        elif mode == "detailed":
            suggestions.extend(analysis["improvement_areas"])
            if not analysis["has_specifics"]:
                suggestions.append("Include specific examples or scenarios")
            if not analysis["has_constraints"]:
                suggestions.append("Specify expected format or output length")

        elif mode == "creative":
            suggestions.append("Add sensory details and emotional context")
            suggestions.append("Expand with related themes or variations")
            suggestions.append("Include narrative structure or storytelling elements")

        elif mode == "technical":
            suggestions.append("Define technical requirements explicitly")
            suggestions.append("Specify programming language or framework if applicable")
            suggestions.append("Include error handling or edge case specifications")

        return suggestions

    def apply_heuristic_enhancement(self, prompt: str) -> str:
        """
        Apply heuristic-based improvements to a prompt.

        Args:
            prompt: The original prompt

        Returns:
            Heuristically enhanced prompt
        """
        enhanced = prompt.strip()

        # Fix punctuation
        if enhanced and enhanced[-1] not in '.!?:':
            enhanced += '.'

        # Replace common vague words
        replacements = {
            r'\bwrite\b': 'write clearly',
            r'\bmake\b': 'create',
            r'\bdo\b': 'implement',
            r'\bget\b': 'retrieve',
            r'\bshow\b': 'display',
            r'\breally\b': 'significantly',
            r'\bnice\b': 'well-designed',
            r'\bgood\b': 'high-quality',
        }

        for pattern, replacement in replacements.items():
            enhanced = re.sub(pattern, replacement, enhanced, flags=re.IGNORECASE)

        return enhanced


if __name__ == "__main__":
    enhancer = PromptEnhancer()

    # Test
    test_prompt = "Write a story"
    print(f"Original: {test_prompt}")

    analysis = enhancer.analyze_prompt(test_prompt)
    print(f"\nAnalysis: {analysis}")

    suggestions = enhancer.get_enhancement_suggestions(test_prompt, mode="detailed")
    print(f"\nSuggestions: {suggestions}")

    heuristic = enhancer.apply_heuristic_enhancement(test_prompt)
    print(f"\nHeuristic Enhancement: {heuristic}")
