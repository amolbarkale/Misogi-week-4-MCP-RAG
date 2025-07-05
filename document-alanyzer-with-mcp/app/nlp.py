from transformers import pipeline
import spacy
import yake
import textstat
from sklearn.feature_extraction.text import TfidfVectorizer
from typing import List, Dict, Tuple
import re

sentiment_pipeline = pipeline("sentiment-analysis")
nlp_spacy = spacy.load("en_core_web_sm")

# Initialize YAKE keyword extractor
yake_extractor = yake.KeywordExtractor(
    lan="en",
    n=3,        # Max n-gram length
    dedupLim=0.7,  # Deduplication threshold
    top=20      # Number of keywords to extract
)

def get_sentiment(text: str) -> dict:
    chunks = [text[i:i+500] for i in range(0, len(text), 500)]
    results = sentiment_pipeline(chunks)
    
    scores = {"POSITIVE": 0, "NEGATIVE": 0}
    for r in results:
        label = r["label"]
        scores[label] += r["score"]

    # Return majority label
    final_label = max(scores, key=scores.get)
    return {"label": final_label, "score": round(scores[final_label] / len(results), 3)}

def get_word_stats(text: str) -> dict:
    doc = nlp_spacy(text)
    sentences = list(doc.sents)
    words = [t for t in doc if t.is_alpha]
    
    # Calculate reading time (average 200 words per minute)
    reading_time = len(words) / 200
    
    return {
        "word_count": len(words),
        "sentence_count": len(sentences),
        "reading_time_minutes": round(reading_time, 2),
        "avg_sentence_length": round(len(words) / len(sentences), 1) if sentences else 0
    }

def extract_keywords_yake(text: str, limit: int = 10) -> List[Dict[str, float]]:
    """Extract keywords using YAKE algorithm"""
    try:
        # Extract keywords with scores
        keywords = yake_extractor.extract_keywords(text)
        
        # Convert to structured format and limit results
        results = []
        for keyword, score in keywords[:limit]:
            results.append({
                "keyword": keyword,
                "score": round(score, 4),  # Lower score = more relevant
                "relevance": round(1 / (1 + score), 4)  # Convert to relevance (higher = better)
            })
        
        return results
    except Exception as e:
        print(f"YAKE extraction error: {e}")
        return []

def extract_keywords_tfidf(text: str, limit: int = 10) -> List[Dict[str, float]]:
    """Extract keywords using TF-IDF with spaCy preprocessing"""
    try:
        # Preprocess text with spaCy
        doc = nlp_spacy(text)
        
        # Extract meaningful tokens (no stop words, punctuation, spaces)
        tokens = [
            token.lemma_.lower() 
            for token in doc 
            if not token.is_stop 
            and not token.is_punct 
            and not token.is_space
            and token.is_alpha
            and len(token.text) > 2
        ]
        
        if not tokens:
            return []
        
        # Create sentences for TF-IDF
        sentences = [sent.text for sent in doc.sents]
        
        if len(sentences) < 2:
            # If only one sentence, use token frequency
            from collections import Counter
            token_counts = Counter(tokens)
            results = []
            for token, count in token_counts.most_common(limit):
                results.append({
                    "keyword": token,
                    "score": count,
                    "relevance": count / len(tokens)
                })
            return results
        
        # Use TF-IDF
        vectorizer = TfidfVectorizer(
            max_features=limit * 3,  # Get more features to filter
            ngram_range=(1, 2),      # Unigrams and bigrams
            stop_words='english'
        )
        
        tfidf_matrix = vectorizer.fit_transform(sentences)
        feature_names = vectorizer.get_feature_names_out()
        
        # Calculate mean TF-IDF scores
        mean_scores = tfidf_matrix.mean(axis=0).A1
        
        # Get top keywords
        top_indices = mean_scores.argsort()[-limit:][::-1]
        
        results = []
        for idx in top_indices:
            if mean_scores[idx] > 0:
                results.append({
                    "keyword": feature_names[idx],
                    "score": round(mean_scores[idx], 4),
                    "relevance": round(mean_scores[idx], 4)
                })
        
        return results
    
    except Exception as e:
        print(f"TF-IDF extraction error: {e}")
        return []

def extract_keywords(text: str, limit: int = 10, method: str = "combined") -> Dict[str, any]:
    """
    Extract keywords using multiple methods
    
    Args:
        text: Input text
        limit: Maximum number of keywords to return
        method: 'yake', 'tfidf', or 'combined'
    
    Returns:
        Dictionary with extracted keywords and metadata
    """
    if not text or not text.strip():
        return {
            "keywords": [],
            "method": method,
            "text_length": 0,
            "error": "Empty text provided"
        }
    
    # Clean text
    text = re.sub(r'\s+', ' ', text.strip())
    
    results = {
        "method": method,
        "text_length": len(text),
        "word_count": len(text.split()),
        "keywords": []
    }
    
    try:
        if method == "yake":
            results["keywords"] = extract_keywords_yake(text, limit)
        elif method == "tfidf":
            results["keywords"] = extract_keywords_tfidf(text, limit)
        else:  # combined
            # Get keywords from both methods
            yake_keywords = extract_keywords_yake(text, limit)
            tfidf_keywords = extract_keywords_tfidf(text, limit)
            
            # Combine and deduplicate
            combined_keywords = {}
            
            # Add YAKE keywords
            for kw in yake_keywords:
                combined_keywords[kw["keyword"]] = {
                    "keyword": kw["keyword"],
                    "yake_score": kw["score"],
                    "yake_relevance": kw["relevance"],
                    "tfidf_score": 0,
                    "combined_score": kw["relevance"]
                }
            
            # Add TF-IDF keywords
            for kw in tfidf_keywords:
                if kw["keyword"] in combined_keywords:
                    combined_keywords[kw["keyword"]]["tfidf_score"] = kw["score"]
                    # Average the scores
                    combined_keywords[kw["keyword"]]["combined_score"] = (
                        combined_keywords[kw["keyword"]]["yake_relevance"] + kw["relevance"]
                    ) / 2
                else:
                    combined_keywords[kw["keyword"]] = {
                        "keyword": kw["keyword"],
                        "yake_score": 0,
                        "yake_relevance": 0,
                        "tfidf_score": kw["score"],
                        "combined_score": kw["relevance"]
                    }
            
            # Sort by combined score and limit
            sorted_keywords = sorted(
                combined_keywords.values(),
                key=lambda x: x["combined_score"],
                reverse=True
            )[:limit]
            
            results["keywords"] = sorted_keywords
    
    except Exception as e:
        results["error"] = str(e)
        results["keywords"] = []
    
    return results

def get_reading_level(score: float) -> str:
    """Convert Flesch Reading Ease score to reading level"""
    if score >= 90:
        return "Very Easy (5th grade)"
    elif score >= 80:
        return "Easy (6th grade)"
    elif score >= 70:
        return "Fairly Easy (7th grade)"
    elif score >= 60:
        return "Standard (8th-9th grade)"
    elif score >= 50:
        return "Fairly Difficult (10th-12th grade)"
    elif score >= 30:
        return "Difficult (college level)"
    else:
        return "Very Difficult (graduate level)"

def analyze_readability(text: str) -> Dict[str, any]:
    """
    Analyze text readability using multiple metrics
    
    Returns:
        Dictionary with various readability scores and interpretations
    """
    if not text or not text.strip():
        return {
            "error": "Empty text provided",
            "text_length": 0
        }
    
    # Clean text
    text = re.sub(r'\s+', ' ', text.strip())
    
    try:
        # Basic text statistics
        word_count = len(text.split())
        sentence_count = textstat.sentence_count(text)
        syllable_count = textstat.syllable_count(text)
        
        # Core readability metrics
        flesch_ease = textstat.flesch_reading_ease(text)
        flesch_grade = textstat.flesch_kincaid_grade(text)
        gunning_fog = textstat.gunning_fog(text)
        smog_index = textstat.smog_index(text)
        ari = textstat.automated_readability_index(text)
        coleman_liau = textstat.coleman_liau_index(text)
        
        # Composite metrics
        reading_time = word_count / 200  # Average 200 words per minute
        avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
        avg_syllables_per_word = syllable_count / word_count if word_count > 0 else 0
        
        # Reading level interpretation
        reading_level = get_reading_level(flesch_ease)
        
        # Determine difficulty category
        if flesch_ease >= 70:
            difficulty = "Easy"
        elif flesch_ease >= 50:
            difficulty = "Moderate"
        elif flesch_ease >= 30:
            difficulty = "Difficult"
        else:
            difficulty = "Very Difficult"
        
        # Grade level average (from multiple metrics)
        grade_levels = [flesch_grade, gunning_fog, smog_index, ari, coleman_liau]
        avg_grade_level = sum(grade_levels) / len(grade_levels)
        
        return {
            "text_statistics": {
                "word_count": word_count,
                "sentence_count": sentence_count,
                "syllable_count": syllable_count,
                "avg_sentence_length": round(avg_sentence_length, 1),
                "avg_syllables_per_word": round(avg_syllables_per_word, 2),
                "reading_time_minutes": round(reading_time, 2)
            },
            "readability_scores": {
                "flesch_reading_ease": round(flesch_ease, 1),
                "flesch_kincaid_grade": round(flesch_grade, 1),
                "gunning_fog_index": round(gunning_fog, 1),
                "smog_index": round(smog_index, 1),
                "automated_readability_index": round(ari, 1),
                "coleman_liau_index": round(coleman_liau, 1),
                "average_grade_level": round(avg_grade_level, 1)
            },
            "interpretation": {
                "reading_level": reading_level,
                "difficulty": difficulty,
                "grade_level_description": f"Grade {round(avg_grade_level, 1)} level",
                "recommendations": get_readability_recommendations(flesch_ease, avg_grade_level)
            }
        }
    
    except Exception as e:
        return {
            "error": f"Readability analysis failed: {str(e)}",
            "text_length": len(text)
        }

def get_readability_recommendations(flesch_ease: float, grade_level: float) -> List[str]:
    """Get recommendations for improving readability"""
    recommendations = []
    
    if flesch_ease < 30:
        recommendations.append("Text is very difficult. Consider using shorter sentences and simpler words.")
    elif flesch_ease < 50:
        recommendations.append("Text is moderately difficult. Try breaking up long sentences.")
    elif flesch_ease < 70:
        recommendations.append("Text is at a good reading level for most adults.")
    else:
        recommendations.append("Text is easy to read and accessible to most readers.")
    
    if grade_level > 12:
        recommendations.append("Reading level is above high school. Consider simplifying vocabulary.")
    elif grade_level > 8:
        recommendations.append("Reading level is appropriate for high school students.")
    elif grade_level > 6:
        recommendations.append("Reading level is suitable for middle school students.")
    else:
        recommendations.append("Reading level is accessible to elementary school students.")
    
    return recommendations

def analyze_text_comprehensive(text: str, include_keywords: bool = True, keyword_limit: int = 10, keyword_method: str = "combined") -> Dict[str, any]:
    """
    Comprehensive text analysis combining all NLP capabilities
    
    Args:
        text: Input text to analyze
        include_keywords: Whether to include keyword extraction
        keyword_limit: Maximum number of keywords to extract
        keyword_method: Method for keyword extraction ('yake', 'tfidf', 'combined')
    
    Returns:
        Dictionary with comprehensive analysis results
    """
    if not text or not text.strip():
        return {
            "error": "Empty text provided",
            "text_length": 0,
            "analysis_timestamp": None
        }
    
    from datetime import datetime
    
    # Initialize results
    results = {
        "analysis_timestamp": datetime.now().isoformat(),
        "input_metadata": {
            "text_length": len(text),
            "text_preview": text[:200] + "..." if len(text) > 200 else text
        },
        "basic_statistics": {},
        "sentiment_analysis": {},
        "readability_analysis": {},
        "keyword_analysis": {},
        "summary": {}
    }
    
    try:
        # 1. Basic Statistics
        print("📊 Running basic statistics...")
        stats = get_word_stats(text)
        results["basic_statistics"] = stats
        
        # 2. Sentiment Analysis
        print("😊 Running sentiment analysis...")
        sentiment = get_sentiment(text)
        results["sentiment_analysis"] = sentiment
        
        # 3. Readability Analysis
        print("📚 Running readability analysis...")
        readability = analyze_readability(text)
        results["readability_analysis"] = readability
        
        # 4. Keyword Analysis (if requested)
        if include_keywords:
            print(f"🔍 Running keyword extraction ({keyword_method})...")
            keywords = extract_keywords(text, keyword_limit, keyword_method)
            results["keyword_analysis"] = keywords
        
        # 5. Generate Summary
        results["summary"] = generate_analysis_summary(results)
        
        print("✅ Analysis complete!")
        
    except Exception as e:
        results["error"] = f"Analysis failed: {str(e)}"
        print(f"❌ Analysis error: {e}")
    
    return results

def generate_analysis_summary(analysis_results: Dict[str, any]) -> Dict[str, any]:
    """Generate a summary of the analysis results"""
    
    summary = {
        "overall_assessment": "Unknown",
        "key_insights": [],
        "recommendations": []
    }
    
    try:
        # Basic stats summary
        stats = analysis_results.get("basic_statistics", {})
        word_count = stats.get("word_count", 0)
        reading_time = stats.get("reading_time_minutes", 0)
        
        # Sentiment summary
        sentiment = analysis_results.get("sentiment_analysis", {})
        sentiment_label = sentiment.get("label", "Unknown")
        sentiment_score = sentiment.get("score", 0)
        
        # Readability summary
        readability = analysis_results.get("readability_analysis", {})
        readability_interpretation = readability.get("interpretation", {})
        difficulty = readability_interpretation.get("difficulty", "Unknown")
        grade_level = readability_interpretation.get("grade_level_description", "Unknown")
        
        # Keywords summary
        keywords = analysis_results.get("keyword_analysis", {})
        top_keywords = keywords.get("keywords", [])[:5]  # Top 5 keywords
        
        # Generate key insights
        summary["key_insights"] = [
            f"Document contains {word_count} words ({reading_time} min read)",
            f"Sentiment: {sentiment_label} (confidence: {sentiment_score})",
            f"Readability: {difficulty} - {grade_level}",
            f"Top keywords: {', '.join([kw.get('keyword', '') for kw in top_keywords[:3]])}"
        ]
        
        # Generate overall assessment
        if sentiment_label == "POSITIVE" and difficulty in ["Easy", "Moderate"]:
            summary["overall_assessment"] = "Positive and Accessible"
        elif sentiment_label == "NEGATIVE" and difficulty in ["Difficult", "Very Difficult"]:
            summary["overall_assessment"] = "Negative and Complex"
        elif difficulty in ["Easy", "Moderate"]:
            summary["overall_assessment"] = "Accessible Content"
        elif difficulty in ["Difficult", "Very Difficult"]:
            summary["overall_assessment"] = "Complex Content"
        else:
            summary["overall_assessment"] = "Standard Content"
        
        # Generate recommendations
        recommendations = []
        
        if word_count < 100:
            recommendations.append("Document is quite short - consider adding more content for better analysis")
        elif word_count > 5000:
            recommendations.append("Document is very long - consider breaking into sections")
        
        if difficulty == "Very Difficult":
            recommendations.append("Consider simplifying language for broader accessibility")
        elif difficulty == "Easy":
            recommendations.append("Text is very accessible - good for general audience")
        
        if sentiment_label == "NEGATIVE" and sentiment_score > 0.8:
            recommendations.append("Strong negative sentiment detected - review tone if unintended")
        
        summary["recommendations"] = recommendations
        
    except Exception as e:
        summary["error"] = f"Summary generation failed: {str(e)}"
    
    return summary

def quick_text_analysis(text: str) -> Dict[str, any]:
    """
    Quick analysis for performance-critical scenarios
    Returns essential metrics only
    """
    if not text or not text.strip():
        return {"error": "Empty text provided"}
    
    try:
        # Basic stats only
        doc = nlp_spacy(text)
        words = [t for t in doc if t.is_alpha]
        sentences = list(doc.sents)
        
        return {
            "word_count": len(words),
            "sentence_count": len(sentences),
            "reading_time_minutes": round(len(words) / 200, 2),
            "estimated_sentiment": "positive" if len([t for t in doc if t.sentiment > 0]) > len([t for t in doc if t.sentiment < 0]) else "negative",
            "complexity_score": round(len(words) / len(sentences), 1) if sentences else 0
        }
    except Exception as e:
        return {"error": f"Quick analysis failed: {str(e)}"}

def batch_analyze_texts(texts: List[str], max_workers: int = 3) -> List[Dict[str, any]]:
    """
    Analyze multiple texts in parallel for better performance
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed
    
    results = []
    
    try:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all analysis tasks
            future_to_index = {
                executor.submit(quick_text_analysis, text): i 
                for i, text in enumerate(texts)
            }
            
            # Collect results in order
            index_to_result = {}
            for future in as_completed(future_to_index):
                index = future_to_index[future]
                try:
                    result = future.result()
                    index_to_result[index] = result
                except Exception as e:
                    index_to_result[index] = {"error": str(e)}
            
            # Return results in original order
            results = [index_to_result[i] for i in range(len(texts))]
    
    except Exception as e:
        results = [{"error": f"Batch analysis failed: {str(e)}"} for _ in texts]
    
    return results
