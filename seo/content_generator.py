#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
OWL AI Agency Content Generator
-------------------------------
An AI-powered content generation system that identifies trending legal technology topics,
generates SEO-optimized content briefs, suggests keyword clusters, and creates
title and meta description variations for A/B testing.

This tool helps maintain a consistent content strategy aligned with SEO goals
while preserving the website's theme and structure.
"""

import os
import json
import random
import requests
import pandas as pd
from datetime import datetime
from collections import Counter
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import openai

# Initialize NLTK components
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

# Configuration
CONFIG = {
    "openai_api_key": os.environ.get("OPENAI_API_KEY", ""),
    "news_api_key": os.environ.get("NEWS_API_KEY", ""),
    "target_keywords": [
        "legal research automation",
        "batch processing legal research",
        "AI legal research",
        "legal document automation",
        "legal tech innovation",
        "law firm efficiency",
        "legal case analysis automation",
        "legal document analysis AI",
        "legal research tools",
        "automated legal citation"
    ],
    "competitor_blogs": [
        "https://www.lexisnexis.com/community/insights/legal/b/legal-technology",
        "https://www.thomsonreuters.com/en/artificial-intelligence.html",
        "https://www.clio.com/blog/",
        "https://www.lawgeex.com/resources/blog/",
        "https://blog.rossintelligence.com/"
    ],
    "output_directory": "content_briefs"
}

class ContentGenerator:
    """AI-powered content generation system for legal technology topics."""
    
    def __init__(self, config=None):
        """Initialize the ContentGenerator with configuration."""
        self.config = config or CONFIG
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        
        # Set up OpenAI API
        if self.config["openai_api_key"]:
            openai.api_key = self.config["openai_api_key"]
        
        # Create output directory if it doesn't exist
        os.makedirs(self.config["output_directory"], exist_ok=True)
    
    def get_trending_topics(self, limit=5):
        """
        Identify trending legal technology topics from news sources.
        
        Args:
            limit (int): Number of trending topics to return
            
        Returns:
            list: List of trending topic dictionaries with title, description, and url
        """
        if not self.config["news_api_key"]:
            print("Warning: News API key not set. Using sample trending topics.")
            return self._get_sample_trending_topics(limit)
        
        # Query NewsAPI for legal technology news
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": "legal technology OR legal automation OR legal AI",
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": 30,
            "apiKey": self.config["news_api_key"]
        }
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            if data.get("status") == "ok":
                articles = data.get("articles", [])
                
                # Process and rank articles by relevance to target keywords
                scored_articles = []
                for article in articles:
                    score = 0
                    title = article.get("title", "").lower()
                    description = article.get("description", "").lower()
                    content = f"{title} {description}"
                    
                    for keyword in self.config["target_keywords"]:
                        if keyword.lower() in content:
                            score += 1
                    
                    scored_articles.append({
                        "title": article.get("title"),
                        "description": article.get("description"),
                        "url": article.get("url"),
                        "published_at": article.get("publishedAt"),
                        "score": score
                    })
                
                # Sort by score and recency
                sorted_articles = sorted(
                    scored_articles, 
                    key=lambda x: (x["score"], x["published_at"]), 
                    reverse=True
                )
                
                return sorted_articles[:limit]
            else:
                print(f"Error fetching news: {data.get('message')}")
                return self._get_sample_trending_topics(limit)
                
        except Exception as e:
            print(f"Error fetching trending topics: {e}")
            return self._get_sample_trending_topics(limit)
    
    def _get_sample_trending_topics(self, limit=5):
        """Provide sample trending topics when API is unavailable."""
        sample_topics = [
            {
                "title": "How AI is Transforming Legal Research in 2025",
                "description": "New developments in AI are changing how law firms approach legal research, with automation leading to 70% time savings.",
                "url": "https://example.com/ai-legal-research-2025",
                "published_at": "2025-03-20T10:30:00Z",
                "score": 5
            },
            {
                "title": "The Rise of Batch Processing in Legal Document Analysis",
                "description": "Law firms are increasingly turning to batch processing to handle multiple cases simultaneously, improving efficiency by 85%.",
                "url": "https://example.com/batch-processing-legal",
                "published_at": "2025-03-18T14:15:00Z",
                "score": 4
            },
            {
                "title": "Automated Citation Formatting: The End of Manual Bluebook Citations",
                "description": "New tools are eliminating the need for manual citation formatting, reducing errors and saving associates hours of work.",
                "url": "https://example.com/automated-citations",
                "published_at": "2025-03-15T09:45:00Z",
                "score": 4
            },
            {
                "title": "Legal Document Merging: Combining Multiple Briefs with AI",
                "description": "Advanced document merging techniques allow for the seamless integration of multiple case briefs into comprehensive reports.",
                "url": "https://example.com/document-merging-ai",
                "published_at": "2025-03-12T11:20:00Z",
                "score": 3
            },
            {
                "title": "Interactive Legal Reports: The Future of Client Communication",
                "description": "Interactive elements in legal reports are transforming how law firms communicate complex findings to clients.",
                "url": "https://example.com/interactive-legal-reports",
                "published_at": "2025-03-10T16:05:00Z",
                "score": 3
            },
            {
                "title": "Template Customization in Legal AI: Balancing Efficiency and Branding",
                "description": "How law firms are maintaining their unique brand identity while leveraging AI templates for document generation.",
                "url": "https://example.com/template-customization-legal",
                "published_at": "2025-03-08T13:40:00Z",
                "score": 3
            }
        ]
        return sample_topics[:limit]
    
    def extract_keywords(self, text, top_n=10):
        """
        Extract important keywords from text.
        
        Args:
            text (str): Text to extract keywords from
            top_n (int): Number of top keywords to return
            
        Returns:
            list: List of top keywords
        """
        # Tokenize and clean text
        tokens = word_tokenize(text.lower())
        
        # Remove stopwords and lemmatize
        filtered_tokens = []
        for token in tokens:
            if token.isalnum() and token not in self.stop_words:
                filtered_tokens.append(self.lemmatizer.lemmatize(token))
        
        # Count word frequencies
        word_freq = Counter(filtered_tokens)
        
        # Get top keywords
        top_keywords = [word for word, _ in word_freq.most_common(top_n)]
        
        return top_keywords
    
    def generate_keyword_clusters(self, seed_keyword, num_clusters=3, keywords_per_cluster=5):
        """
        Generate keyword clusters around a seed keyword using AI.
        
        Args:
            seed_keyword (str): The main keyword to build clusters around
            num_clusters (int): Number of clusters to generate
            keywords_per_cluster (int): Number of keywords per cluster
            
        Returns:
            dict: Dictionary of keyword clusters
        """
        if not self.config["openai_api_key"]:
            print("Warning: OpenAI API key not set. Using sample keyword clusters.")
            return self._get_sample_keyword_clusters(seed_keyword)
        
        try:
            # Use OpenAI to generate keyword clusters
            prompt = f"""
            Generate {num_clusters} keyword clusters for content about "{seed_keyword}" in the legal technology domain.
            Each cluster should have {keywords_per_cluster} related keywords.
            Format the response as a JSON object with cluster names as keys and arrays of keywords as values.
            Make the clusters distinct but related to the main topic.
            """
            
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an SEO expert specializing in legal technology content."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            # Parse the response
            content = response.choices[0].message.content
            clusters = json.loads(content)
            
            return clusters
            
        except Exception as e:
            print(f"Error generating keyword clusters: {e}")
            return self._get_sample_keyword_clusters(seed_keyword)
    
    def _get_sample_keyword_clusters(self, seed_keyword):
        """Provide sample keyword clusters when API is unavailable."""
        sample_clusters = {
            "Efficiency Benefits": [
                "time-saving legal research",
                "law firm productivity tools",
                "legal research efficiency metrics",
                "automated case analysis benefits",
                "legal workflow optimization"
            ],
            "Technical Implementation": [
                "legal AI integration steps",
                "law firm technology adoption",
                "legal research API implementation",
                "document analysis algorithms",
                "legal tech infrastructure requirements"
            ],
            "Practical Applications": [
                "case law automation examples",
                "legal brief generation tools",
                "statute analysis automation",
                "legal precedent identification",
                "automated legal citation systems"
            ]
        }
        return sample_clusters
    
    def generate_content_brief(self, topic, keyword_clusters=None):
        """
        Generate a comprehensive content brief for a given topic.
        
        Args:
            topic (dict): Topic dictionary with title and description
            keyword_clusters (dict): Optional pre-generated keyword clusters
            
        Returns:
            dict: Content brief with structure, keywords, and suggestions
        """
        title = topic.get("title", "")
        description = topic.get("description", "")
        
        # Extract main keyword from title
        main_keyword = self.extract_keywords(title, top_n=1)[0]
        
        # Generate keyword clusters if not provided
        if not keyword_clusters:
            keyword_clusters = self.generate_keyword_clusters(main_keyword)
        
        if not self.config["openai_api_key"]:
            print("Warning: OpenAI API key not set. Using sample content brief.")
            return self._get_sample_content_brief(topic, keyword_clusters)
        
        try:
            # Use OpenAI to generate the content brief
            prompt = f"""
            Create a detailed content brief for an article titled "{title}" with the description: "{description}".
            
            The article should target these keyword clusters:
            {json.dumps(keyword_clusters, indent=2)}
            
            Include the following in your brief:
            1. Article structure with H2 and H3 headings
            2. Key points to cover under each heading
            3. Types of statistics or examples to include
            4. Internal linking suggestions to other legal research topics
            5. Call-to-action recommendations
            6. 3 title variations for A/B testing
            7. 3 meta description variations for A/B testing
            
            Format the response as a JSON object with these sections clearly defined.
            """
            
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert content strategist for a legal technology company."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            # Parse the response
            content = response.choices[0].message.content
            brief = json.loads(content)
            
            # Add metadata
            brief["topic"] = topic
            brief["keyword_clusters"] = keyword_clusters
            brief["generated_at"] = datetime.now().isoformat()
            
            return brief
            
        except Exception as e:
            print(f"Error generating content brief: {e}")
            return self._get_sample_content_brief(topic, keyword_clusters)
    
    def _get_sample_content_brief(self, topic, keyword_clusters):
        """Provide a sample content brief when API is unavailable."""
        title = topic.get("title", "Sample Title")
        
        sample_brief = {
            "topic": topic,
            "keyword_clusters": keyword_clusters,
            "generated_at": datetime.now().isoformat(),
            "article_structure": {
                "introduction": "Overview of the topic and why it matters to legal professionals",
                "h2_sections": [
                    {
                        "heading": "Current Challenges in Legal Research",
                        "key_points": [
                            "Time constraints facing legal professionals",
                            "Volume and complexity of legal documents",
                            "Accuracy requirements in legal research",
                            "Cost implications of traditional methods"
                        ]
                    },
                    {
                        "heading": "How AI Transforms the Research Process",
                        "key_points": [
                            "Pattern recognition in case law",
                            "Natural language processing applications",
                            "Automated citation and reference checking",
                            "Integration with existing legal databases"
                        ],
                        "h3_sections": [
                            {
                                "heading": "Time Savings Analysis",
                                "key_points": [
                                    "Comparison of manual vs. automated research times",
                                    "Case studies from law firms",
                                    "ROI calculations"
                                ]
                            },
                            {
                                "heading": "Accuracy Improvements",
                                "key_points": [
                                    "Error rate comparisons",
                                    "Consistency metrics",
                                    "Quality control mechanisms"
                                ]
                            }
                        ]
                    },
                    {
                        "heading": "Implementation Strategies for Law Firms",
                        "key_points": [
                            "Assessment of current workflows",
                            "Technology integration steps",
                            "Staff training requirements",
                            "Measuring success and optimization"
                        ]
                    },
                    {
                        "heading": "Future Developments in Legal Research Automation",
                        "key_points": [
                            "Emerging technologies on the horizon",
                            "Predictive analytics in legal outcomes",
                            "Cross-jurisdictional research capabilities",
                            "Ethical considerations and best practices"
                        ]
                    }
                ],
                "conclusion": "Summary of benefits and call to action for implementing legal research automation"
            },
            "statistics_to_include": [
                "Percentage time savings from automated research (aim for 60-70% figure)",
                "Accuracy improvement rates (30-40% range)",
                "Cost reduction metrics (25-35% range)",
                "Adoption rates among AmLaw 100 firms"
            ],
            "examples_to_include": [
                "Case study of a mid-size firm implementing research automation",
                "Before/after comparison of a complex research task",
                "ROI calculation example for a typical law firm"
            ],
            "internal_linking_suggestions": [
                {"anchor_text": "batch processing for legal research", "target": "/blog/batch-processing-legal-research.html"},
                {"anchor_text": "document template customization", "target": "/legal-research.html#customization"},
                {"anchor_text": "legal citation formatting", "target": "/services.html#citation-services"}
            ],
            "call_to_action_recommendations": [
                "Schedule a demo of our legal research automation platform",
                "Download our white paper on implementing legal AI",
                "Sign up for a free trial of our batch processing feature"
            ],
            "title_variations": [
                f"{title}",
                f"{title}: A Guide for Modern Law Firms",
                f"How {title} is Revolutionizing Legal Practice"
            ],
            "meta_description_variations": [
                f"Discover how {title.lower()} can transform your law firm's efficiency, accuracy, and bottom line. Learn implementation strategies and success metrics.",
                f"Struggling with legal research workloads? Learn how {title.lower()} can reduce research time by 70% while improving accuracy and consistency.",
                f"Explore the benefits, implementation strategies, and ROI of {title.lower()} in this comprehensive guide for forward-thinking law firms."
            ]
        }
        
        return sample_brief
    
    def save_content_brief(self, brief, filename=None):
        """
        Save a content brief to a JSON file.
        
        Args:
            brief (dict): Content brief to save
            filename (str): Optional filename, defaults to a generated name
            
        Returns:
            str: Path to the saved file
        """
        if not filename:
            # Generate filename from title
            title = brief.get("topic", {}).get("title", "content-brief")
            safe_title = "".join(c if c.isalnum() or c in [' ', '-'] else '' for c in title).lower()
            safe_title = safe_title.replace(' ', '-')
            date_str = datetime.now().strftime("%Y%m%d")
            filename = f"{date_str}-{safe_title}.json"
        
        # Ensure the file has a .json extension
        if not filename.endswith('.json'):
            filename += '.json'
        
        # Create the full path
        filepath = os.path.join(self.config["output_directory"], filename)
        
        # Save the brief
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(brief, f, indent=2, ensure_ascii=False)
        
        print(f"Content brief saved to {filepath}")
        return filepath
    
    def generate_title_variations(self, base_title, num_variations=3):
        """
        Generate variations of a title for A/B testing.
        
        Args:
            base_title (str): The original title
            num_variations (int): Number of variations to generate
            
        Returns:
            list: List of title variations
        """
        if not self.config["openai_api_key"]:
            print("Warning: OpenAI API key not set. Using sample title variations.")
            return self._get_sample_title_variations(base_title, num_variations)
        
        try:
            prompt = f"""
            Generate {num_variations} variations of the following title for A/B testing:
            "{base_title}"
            
            The variations should:
            1. Maintain the core meaning and keywords
            2. Use different emotional appeals (curiosity, urgency, benefit-focused)
            3. Vary in structure (question, how-to, listicle, etc.)
            4. Be optimized for SEO and click-through rates
            
            Return only the list of variations, with no additional text.
            """
            
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert copywriter specializing in SEO-optimized headlines."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Parse the response and extract variations
            content = response.choices[0].message.content
            variations = [line.strip().strip('"\'') for line in content.strip().split('\n') if line.strip()]
            
            return variations[:num_variations]
            
        except Exception as e:
            print(f"Error generating title variations: {e}")
            return self._get_sample_title_variations(base_title, num_variations)
    
    def _get_sample_title_variations(self, base_title, num_variations=3):
        """Provide sample title variations when API is unavailable."""
        prefixes = [
            "The Ultimate Guide to",
            "How to Master",
            "5 Ways",
            "Why Every Law Firm Needs",
            "The Future of",
            "Transforming Legal Practice with"
        ]
        
        suffixes = [
            ": A Complete Guide",
            " in 2025",
            " for Modern Law Firms",
            ": What You Need to Know",
            " That Actually Works",
            ": Case Studies & Results"
        ]
        
        variations = []
        for _ in range(num_variations):
            prefix = random.choice(prefixes)
            suffix = random.choice(suffixes)
            
            # Avoid using the same prefix or suffix twice
            prefixes.remove(prefix)
            suffixes.remove(suffix)
            
            # Create variation
            if random.choice([True, False]):
                variation = f"{prefix} {base_title}"
            else:
                variation = f"{base_title}{suffix}"
            
            variations.append(variation)
        
        return variations
    
    def generate_meta_description_variations(self, base_description, num_variations=3):
        """
        Generate variations of a meta description for A/B testing.
        
        Args:
            base_description (str): The original meta description
            num_variations (int): Number of variations to generate
            
        Returns:
            list: List of meta description variations
        """
        if not self.config["openai_api_key"]:
            print("Warning: OpenAI API key not set. Using sample meta description variations.")
            return self._get_sample_meta_description_variations(base_description, num_variations)
        
        try:
            prompt = f"""
            Generate {num_variations} variations of the following meta description for A/B testing:
            "{base_description}"
            
            The variations should:
            1. Be under 160 characters
            2. Include the main keywords
            3. Have a clear value proposition
            4. Include a call-to-action
            5. Be optimized for click-through rate
            
            Return only the list of variations, with no additional text.
            """
            
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert SEO copywriter specializing in meta descriptions."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Parse the response and extract variations
            content = response.choices[0].message.content
            variations = [line.strip().strip('"\'') for line in content.strip().split('\n') if line.strip()]
            
            return variations[:num_variations]
            
        except Exception as e:
            print(f"Error generating meta description variations: {e}")
            return self._get_sample_meta_description_variations(base_description, num_variations)
    
    def _get_sample_meta_description_variations(self, base_description, num_variations=3):
        """Provide sample meta description variations when API is unavailable."""
        intros = [
            "Discover how",
            "Learn why",
            "Find out how",
            "See how leading law firms use",
            "Explore the benefits of",
            "Transform your legal practice with"
        ]
        
        outros = [
            "Start improving your efficiency today.",
            "Get started with a free consultation.",
            "Learn more about implementation strategies.",
            "See real results from law firms like yours.",
            "Download our free guide to learn more.",
            "Schedule a demo to see it in action."
        ]
        
        variations = []
        for _ in range(num_variations):
            intro = random.choice(intros)
            outro = random.choice(outros)
            
            # Avoid using the same intro or outro twice
            intros.remove(intro)
            outros.remove(outro)
            
            # Extract core message (simplified approach)
            core_message = base_description.split('.')[0] if '.' in base_description else base_description
            
            # Ensure it's not too long (roughly 160 chars)
            max_core_length = 160 - len(intro) - len(outro) - 2  # 2 for spaces
            if len(core_message) > max_core_length:
                core_message = core_message[:max_core_length-3] + "..."
            
            # Create variation
            variation = f"{intro} {core_message}. {outro}"
            
            variations.append(variation)
        
        return variations
    
    def run_content_generation_pipeline(self, num_topics=3):
        """
        Run the complete content generation pipeline.
        
        Args:
            num_topics (int): Number of topics to generate content for
            
        Returns:
            list: Paths to the generated content briefs
        """
        # 1. Get trending topics
        print(f"Finding {num_topics} trending legal technology topics...")
        trending_topics = self.get_trending_topics(limit=num_topics)
        
        # 2. Generate content briefs for each topic
        generated_files = []
        for topic in trending_topics:
            print(f"\nGenerating content brief for: {topic['title']}")
            
            # Extract main keyword
            main_keyword = self.extract_keywords(topic['title'], top_n=1)[0]
            
            # Generate keyword clusters
            print(f"Generating keyword clusters for: {main_keyword}")
            keyword_clusters = self.generate_keyword_clusters(main_keyword)
            
            # Generate content brief
            print("Creating comprehensive content brief...")
            brief = self.generate_content_brief(topic, keyword_clusters)
            
            # Save brief to file
            filepath = self.save_content_brief(brief)
            generated_files.append(filepath)
            
            print(f"Completed brief for: {topic['title']}")
        
        print(f"\nContent generation complete. Generated {len(generated_files)} content briefs.")
        return generated_files

def main():
    """Run the content generator as a standalone script."""
    print("OWL AI Agency Content Generator")
    print("===============================")
    
    # Check for API keys
    if not CONFIG["openai_api_key"]:
        print("Warning: OpenAI API key not set. Set the OPENAI_API_KEY environment variable for full functionality.")
    if not CONFIG["news_api_key"]:
        print("Warning: News API key not set. Set the NEWS_API_KEY environment variable for full functionality.")
    
    # Initialize and run the content generator
    generator = ContentGenerator()
    generator.run_content_generation_pipeline(num_topics=3)

if __name__ == "__main__":
    main()
