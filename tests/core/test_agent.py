# tests/core/test_agent.py
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from typing import Dict, Any, List, Optional

class TestAgent:
    def __init__(self):
        self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    
    def compare(self, expected: str, actual: str, 
                mandatory_words: Optional[List[str]] = None,
                optional_words: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Compare une réponse avec système mandatory/optional
        
        Args:
            expected: Réponse attendue
            actual: Réponse obtenue
            mandatory_words: Mots obligatoires (50% du score)
            optional_words: Mots optionnels pour la formulation (30% du score)
            
        Returns:
            Dict avec scores détaillés et résultat final
        """
        
        # 1. Similarité sémantique (20% du score)
        embeddings = self.model.encode([expected, actual])
        semantic_similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
        
        actual_lower = actual.lower()
        
        # 2. Score Mandatory Words (50% du score)
        mandatory_score = 0
        found_mandatory = []
        missing_mandatory = []
        
        if mandatory_words:
            for word in mandatory_words:
                if word.lower() in actual_lower:
                    mandatory_score += 1
                    found_mandatory.append(word)
                else:
                    missing_mandatory.append(word)
            mandatory_score = mandatory_score / len(mandatory_words)
        else:
            mandatory_score = 1.0  # Si pas de mots mandatory, score parfait
        
        # 3. Score Optional Words (30% du score) 
        optional_score = 0
        found_optional = []
        missing_optional = []
        
        if optional_words:
            for word in optional_words:
                if word.lower() in actual_lower:
                    optional_score += 1
                    found_optional.append(word)
                else:
                    missing_optional.append(word)
            optional_score = optional_score / len(optional_words)
        else:
            optional_score = 1.0  # Si pas de mots optionnels, score parfait
        
        # 4. Score Final Pondéré
        final_score = (
            mandatory_score * 0.5 +      # 50% pour les mots obligatoires
            optional_score * 0.3 +       # 30% pour les mots optionnels  
            semantic_similarity * 0.2    # 20% pour la similarité sémantique
        )
        
        # 5. Détermination du résultat
        # PASS si: 80% des mandatory + score final >= 0.7
        mandatory_threshold = 0.8
        passed = (mandatory_score >= mandatory_threshold and final_score >= 0.7)
        
        return {
            "final_score": round(final_score, 3),
            "breakdown": {
                "mandatory_score": round(mandatory_score, 3),
                "optional_score": round(optional_score, 3), 
                "semantic_score": round(semantic_similarity, 3)
            },
            "mandatory_analysis": {
                "found": found_mandatory,
                "missing": missing_mandatory,
                "coverage": f"{len(found_mandatory)}/{len(mandatory_words) if mandatory_words else 0}"
            },
            "optional_analysis": {
                "found": found_optional,
                "missing": missing_optional,
                "coverage": f"{len(found_optional)}/{len(optional_words) if optional_words else 0}"
            },
            "passed": passed,
            "grade": self._get_grade(final_score),
            "interpretation": self._get_interpretation(final_score, mandatory_score)
        }
    
    def _get_grade(self, score: float) -> str:
        """Convertit le score en note"""
        if score >= 0.9: return "A+"
        elif score >= 0.8: return "A"
        elif score >= 0.7: return "B"
        elif score >= 0.6: return "C"
        elif score >= 0.5: return "D"
        else: return "F"
    
    def _get_interpretation(self, final_score: float, mandatory_score: float) -> str:
        """Interprétation du résultat"""
        if mandatory_score < 0.8:
            return "Échec: Informations essentielles manquantes"
        elif final_score >= 0.9:
            return "Excellent: Réponse complète et bien formulée"
        elif final_score >= 0.8:
            return "Très bien: Informations présentes, bonne formulation"
        elif final_score >= 0.7:
            return "Bien: Informations correctes, formulation à améliorer"
        else:
            return "Insuffisant: Problèmes de contenu et formulation"