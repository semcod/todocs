"""Parse README.md into structured sections using regex-based markdown parsing."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, Optional, List


_SECTION_ALIASES = {
    "install": "installation",
    "installing": "installation",
    "setup": "installation",
    "getting started": "installation",
    "quick start": "usage",
    "quickstart": "usage",
    "how to use": "usage",
    "examples": "usage",
    "example": "usage",
    "usage": "usage",
    "features": "features",
    "api": "api",
    "api reference": "api",
    "configuration": "configuration",
    "config": "configuration",
    "contributing": "contributing",
    "contribute": "contributing",
    "license": "license",
    "licence": "license",
    "architecture": "architecture",
    "design": "architecture",
    "roadmap": "roadmap",
    "todo": "roadmap",
    "changelog": "changelog",
    "changes": "changelog",
    "description": "description",
    "overview": "description",
    "about": "description",
    "introduction": "description",
    "what is": "description",
}


class ReadmeParser:
    """Extract structured sections from a README.md file."""

    def __init__(self, project_path: Path):
        self.root = Path(project_path)
        self._nltk_available = self._check_nltk()

    def _check_nltk(self) -> bool:
        """Check if NLTK is available for NLP processing."""
        try:
            import nltk
            # Check if required NLTK data is available
            try:
                nltk.data.find('tokenizers/punkt')
                nltk.data.find('taggers/averaged_perceptron_tagger')
            except LookupError:
                # Download required data silently
                try:
                    nltk.download('punkt', quiet=True)
                    nltk.download('averaged_perceptron_tagger', quiet=True)
                except:
                    return False
            return True
        except ImportError:
            return False

    def parse(self) -> Dict[str, str]:
        """Parse README and return section_name -> content dict."""
        readme_path = self._find_readme()
        if not readme_path:
            return {}

        try:
            text = readme_path.read_text(errors="replace")
        except Exception:
            return {}

        return self._parse_sections(text)

    def _find_readme(self) -> Optional[Path]:
        for name in ["README.md", "readme.md", "Readme.md", "README.rst", "README.txt", "README"]:
            fp = self.root / name
            if fp.exists():
                return fp
        return None

    def _parse_sections(self, text: str) -> Dict[str, str]:
        """Split markdown by headings into sections."""
        sections: Dict[str, str] = {}

        desc_text = self._extract_description(text)
        if desc_text:
            # Extract more text and use NLP to summarize if available
            if self._nltk_available:
                sections["description"] = self._summarize_with_nlp(desc_text, max_chars=2000)
            else:
                sections["description"] = desc_text[:2000]

        sections.update(self._extract_heading_sections(text))
        return sections

    def _extract_description(self, text: str) -> str:
        """Extract description from text before first heading or between h1 and h2."""
        lines = text.split("\n")

        preamble = self._extract_preamble(lines)
        post_h1 = self._extract_post_h1(lines)

        desc_lines = preamble if len(preamble) >= len(post_h1) else post_h1
        desc_text = "\n".join(desc_lines).strip()

        # If no good description found, try to extract from first paragraph after h2
        if not desc_text or len(desc_text) < 20:
            desc_text = self._extract_after_h2(lines)

        if desc_text:
            desc_text = re.sub(r"\*\*(.+?)\*\*", r"\1", desc_text)
            desc_text = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", desc_text)
            # Filter out code blocks and examples
            desc_text = re.sub(r"```[\s\S]*?```", "", desc_text)
            # Filter out lines that look like code (contain def, import, etc.)
            filtered_lines = []
            for line in desc_text.split("\n"):
                line_stripped = line.strip()
                # Skip lines that look like code
                if any(keyword in line_stripped for keyword in ["def ", "import ", "from ", "class ", "tokens = count_tokens", "# ", "    "]):
                    continue
                # Skip lines that are too short or just symbols
                if len(line_stripped) < 3:
                    continue
                # Skip lines that are just URLs or file paths
                if line_stripped.startswith("http") or line_stripped.startswith("/") or line_stripped.startswith("./"):
                    continue
                filtered_lines.append(line)
            desc_text = "\n".join(filtered_lines).strip()

        return desc_text

    def _extract_preamble(self, lines: list) -> list:
        """Extract text before any heading."""
        preamble = []
        in_badges = True
        for line in lines:
            if re.match(r"^#{1,3}\s", line):
                break
            stripped = line.strip()
            # Skip badges, images, and metadata blocks at the start
            if in_badges:
                if not stripped:
                    continue
                if stripped.startswith(("[![", "[!", "![", "<img", "<a href", "<p align")):
                    continue
                if stripped.startswith("- 🤖") or stripped.startswith("- 👤"):
                    continue
                if re.match(r"^[A-Za-z\s]+$", stripped) and len(stripped.split()) <= 3:
                    # Skip single-word badge labels like "PyPI Version"
                    continue
                # Once we find a real sentence, stop skipping
                if len(stripped) > 20 or (stripped and not re.match(r"^[A-Za-z\s]+$", stripped)):
                    in_badges = False
                    preamble.append(line)
            else:
                preamble.append(line)
        return preamble

    def _extract_post_h1(self, lines: list) -> list:
        """Extract text between first h1 and first h2/h3."""
        post_h1 = []
        found_h1 = False
        for line in lines:
            if re.match(r"^#\s", line) and not found_h1:
                found_h1 = True
                continue
            if found_h1:
                if re.match(r"^#{1,3}\s", line):
                    break
                if line.strip() and not line.strip().startswith(("[![", "[!")):
                    post_h1.append(line)
        return post_h1

    def _extract_after_h2(self, lines: list) -> str:
        """Extract first paragraph after first h2 heading."""
        found_h2 = False
        paragraph = []
        for line in lines:
            if re.match(r"^##\s", line):
                found_h2 = True
                continue
            if found_h2:
                if re.match(r"^#{1,3}\s", line):
                    break
                if line.strip():
                    paragraph.append(line)
                elif paragraph:  # Empty line ends the paragraph
                    break
        return "\n".join(paragraph).strip()

    def _extract_heading_sections(self, text: str) -> Dict[str, str]:
        """Extract sections based on markdown headings."""
        sections: Dict[str, str] = {}
        heading_pattern = re.compile(r"^(#{1,3})\s+(.+)", re.MULTILINE)
        matches = list(heading_pattern.finditer(text))

        for i, m in enumerate(matches):
            title = m.group(2).strip()
            title_lower = re.sub(r"[^a-z0-9\s]", "", title.lower()).strip()
            canonical = _SECTION_ALIASES.get(title_lower, title_lower)

            start = m.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            content = text[start:end].strip()

            # Increase limit and use NLP summarization for important sections
            if len(content) > 2000:
                if self._nltk_available and canonical in ["features", "description"]:
                    content = self._summarize_with_nlp(content, max_chars=2000)
                else:
                    content = content[:2000] + "..."

            if canonical and content and canonical not in sections:
                sections[canonical] = content

        return sections

    def get_first_paragraph(self) -> str:
        """Get the first meaningful paragraph from README."""
        sections = self.parse()
        desc = sections.get("description", "")
        if desc:
            # Return first paragraph
            paras = desc.split("\n\n")
            return paras[0].strip() if paras else ""
        return ""

    def _clean_text_for_nlp(self, text: str) -> str:
        """Clean markdown formatting for NLP processing."""
        text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
        text = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", text)
        text = re.sub(r"`([^`]+)`", r"\1", text)
        text = re.sub(r"```[\s\S]*?```", "", text)  # Remove code blocks
        text = re.sub(r"[^\w\s\.\,\-]", " ", text)  # Remove special chars
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def _score_sentence(self, sentence: str, index: int, important_keywords: list) -> int:
        """Score a sentence based on length, keywords, and position."""
        score = 0
        words = sentence.lower().split()
        # Length penalty (prefer medium-length sentences)
        if 5 <= len(words) <= 25:
            score += 1
        # Keyword matching
        for kw in important_keywords:
            if kw in sentence.lower():
                score += 2
        # Position preference (earlier sentences often more important)
        score += max(0, 5 - index * 0.5)
        return score

    def _select_top_sentences(self, sentences: list, sentence_scores: list, max_count: int = 3) -> list:
        """Select and reorder top sentences by original position."""
        # Sort by score and take top sentences
        sentence_scores.sort(key=lambda x: x[0], reverse=True)
        top_sentences = [sent for score, sent in sentence_scores[:5]]

        # Reorder by original position
        original_order = []
        for sent in sentences:
            if sent in top_sentences:
                original_order.append(sent)
                top_sentences.remove(sent)
                if len(original_order) >= max_count:
                    break

        return original_order

    def _summarize_with_nlp(self, text: str, max_chars: int = 2000) -> str:
        """Summarize text using NLP to extract key information."""
        if not self._nltk_available:
            # Fallback: take first N characters
            return text[:max_chars] + "..." if len(text) > max_chars else text

        try:
            import nltk

            # Clean markdown formatting
            text = self._clean_text_for_nlp(text)

            # Split into sentences
            sentences = nltk.sent_tokenize(text)
            if not sentences:
                return text[:max_chars] + "..." if len(text) > max_chars else text

            # Score sentences based on important keywords
            important_keywords = [
                "feature", "tool", "library", "framework", "system", "platform",
                "provides", "enables", "allows", "supports", "integrates",
                "automatically", "analyze", "generate", "detect", "validate",
                "management", "automation", "processing", "validation"
            ]

            sentence_scores = []
            for i, sent in enumerate(sentences):
                score = self._score_sentence(sent, i, important_keywords)
                sentence_scores.append((score, sent))

            # Select and reorder top sentences
            original_order = self._select_top_sentences(sentences, sentence_scores)

            summary = " ".join(original_order)
            if len(summary) > max_chars:
                summary = summary[:max_chars] + "..."

            return summary
        except Exception as e:
            # Fallback on any error
            return text[:max_chars] + "..." if len(text) > max_chars else text

    def _extract_features_with_nltk(self, text: str, max_features: int) -> List[str]:
        """Extract features using NLTK sentence tokenization."""
        import nltk

        feature_keywords = [
            "feature", "provides", "enables", "allows", "supports",
            "integrates", "automatically", "analyze", "generate",
            "detect", "validate", "management", "automation"
        ]

        sentences = nltk.sent_tokenize(text)
        feature_sentences = []

        for sent in sentences:
            sent_lower = sent.lower()
            if any(kw in sent_lower for kw in feature_keywords):
                clean_sent = re.sub(r"\s+", " ", sent).strip()
                if len(clean_sent) > 10 and len(clean_sent) < 200:
                    feature_sentences.append(clean_sent)

        return feature_sentences[:max_features]

    def _extract_features_from_bullets(self, text: str, max_features: int) -> List[str]:
        """Extract features from bullet points as fallback."""
        lines = text.split("\n")
        features = []
        for line in lines:
            line = line.strip()
            if line.startswith("-") or line.startswith("*"):
                clean = re.sub(r"^[-*]\s+", "", line)
                clean = re.sub(r"`[^`]+`", "", clean)
                clean = clean.strip()
                if len(clean) > 5 and len(clean) < 200:
                    features.append(clean)
                    if len(features) >= max_features:
                        break

        return features[:max_features]

    def extract_key_features(self, max_features: int = 5) -> List[str]:
        """Extract key features from README using NLP."""
        sections = self.parse()
        features_section = sections.get("features", "")
        description = sections.get("description", "")

        text = features_section if features_section else description
        if not text:
            return []

        # Clean markdown
        text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
        text = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", text)
        text = re.sub(r"[^\w\s\.\,\-\n]", " ", text)

        if self._nltk_available:
            try:
                return self._extract_features_with_nltk(text, max_features)
            except Exception:
                pass

        # Fallback: extract bullet points or short lines
        return self._extract_features_from_bullets(text, max_features)
