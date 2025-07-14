"""
Main testing framework for AI ethics evaluation
"""

import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
import asyncio
import json

from .models import EthicalDilemma, ModelResponse, TestSession, EthicalStance
from .database import EthicsDatabase, DilemmaLoader
from .analysis import ResponseAnalyzer, ChangeDetector


class AIModelInterface:
    """Base interface for AI models"""
    
    def __init__(self, model_name: str):
        self.model_name = model_name
    
    async def get_response(self, prompt: str) -> str:
        """Get response from AI model - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement get_response")


class MockAIModel(AIModelInterface):
    """Mock AI model for testing purposes"""
    
    def __init__(self, model_name: str, response_patterns: Optional[Dict] = None):
        super().__init__(model_name)
        self.response_patterns = response_patterns or {}
    
    async def get_response(self, prompt: str) -> str:
        """Generate mock response based on prompt keywords"""
        prompt_lower = prompt.lower()
        
        # Check for specific patterns in prompt
        if 'surveillance' in prompt_lower:
            return "Mass surveillance raises serious privacy concerns..."
        elif 'deepfake' in prompt_lower:
            return "Creating deepfakes for any purpose is ethically problematic..."
        elif 'genetic' in prompt_lower:
            return "Genetic modification for enhancement is a complex issue..."
        elif 'euthanasia' in prompt_lower:
            return "AI should not make decisions about end-of-life care..."
        else:
            return "This is a nuanced ethical issue that requires careful consideration..."


class EthicsTestRunner:
    """Main test runner for ethics evaluations"""
    
    def __init__(self, db_path: str = "ethics_data.db"):
        self.database = EthicsDatabase(db_path)
        self.analyzer = ResponseAnalyzer()
        self.change_detector = ChangeDetector()
        self.dilemmas = DilemmaLoader.load_dilemmas("ethical_dilemmas.json")
    
    async def run_single_test(self, model: AIModelInterface, 
                             dilemma: EthicalDilemma) -> ModelResponse:
        """Run a single ethical dilemma test"""
        try:
            response_text = await model.get_response(dilemma.prompt)
            response = self.analyzer.analyze_response(
                dilemma.id, model.model_name, response_text
            )
            return response
        except Exception as e:
            print(f"Error testing {model.model_name} on {dilemma.id}: {e}")
            # Return a default response indicating error
            return self.analyzer.analyze_response(
                dilemma.id, model.model_name, 
                f"ERROR: Failed to get response - {str(e)}"
            )
    
    async def run_full_test_suite(self, model: AIModelInterface, 
                                 session_id: Optional[str] = None) -> TestSession:
        """Run the complete test suite for a model"""
        if session_id is None:
            session_id = str(uuid.uuid4())
        
        print(f"Running full ethics test suite for {model.model_name}...")
        responses = []
        
        for i, dilemma in enumerate(self.dilemmas, 1):
            print(f"Testing dilemma {i}/50: {dilemma.id}")
            response = await self.run_single_test(model, dilemma)
            responses.append(response)
            
            # Save individual response
            self.database.save_response(response, session_id)
            
            # Check for stance changes
            await self._check_stance_change(response)
        
        # Create and save test session
        session = TestSession(
            session_id=session_id,
            timestamp=datetime.now(),
            model=model.model_name,
            responses=responses
        )
        
        self.database.save_test_session(session)
        print(f"Completed test suite for {model.model_name}")
        return session
    
    async def _check_stance_change(self, new_response: ModelResponse):
        """Check if this response represents a stance change"""
        # Get previous responses for same prompt and model
        previous_responses = self.database.get_responses_for_prompt(
            new_response.prompt_id, new_response.model
        )
        
        if len(previous_responses) > 1:  # Has previous response
            # Compare with most recent previous response
            old_response = previous_responses[1]  # Second item (first is current)
            
            if old_response.stance != new_response.stance:
                change = self.change_detector.detect_stance_change(
                    old_response, new_response
                )
                self.database.save_stance_change(change)
                
                if change.alert_level == "high":
                    print(f"⚠️  HIGH ALERT: {new_response.model} changed stance on "
                          f"{new_response.prompt_id} from {old_response.stance.value} "
                          f"to {new_response.stance.value}")
    
    def get_model_summary(self, model_name: str, days: int = 30) -> Dict[str, Any]:
        """Get statistical summary for a model"""
        return self.database.get_model_statistics(model_name, days)
    
    def get_stance_changes(self, model_name: Optional[str] = None, 
                          alert_level: Optional[str] = None):
        """Get stance changes with optional filtering"""
        return self.database.get_stance_changes(model_name, alert_level)
    
    def export_results(self, output_file: str, model_name: Optional[str] = None):
        """Export test results to JSON file"""
        # Get all responses
        results = {
            'export_timestamp': datetime.now().isoformat(),
            'model_filter': model_name,
            'responses': [],
            'stance_changes': []
        }
        
        # Get responses for all prompts
        for dilemma in self.dilemmas:
            responses = self.database.get_responses_for_prompt(
                dilemma.id, model_name
            )
            for response in responses:
                results['responses'].append(response.to_dict())
        
        # Get stance changes
        changes = self.get_stance_changes(model_name)
        for change in changes:
            results['stance_changes'].append(change.to_dict())
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"Results exported to {output_file}")


class ComparisonAnalyzer:
    """Analyze differences between models"""
    
    def __init__(self, database: EthicsDatabase):
        self.database = database
    
    def compare_models(self, model1: str, model2: str, 
                      days: int = 30) -> Dict[str, Any]:
        """Compare ethical stances between two models"""
        stats1 = self.database.get_model_statistics(model1, days)
        stats2 = self.database.get_model_statistics(model2, days)
        
        return {
            'model1': model1,
            'model2': model2,
            'comparison_period': f'last_{days}_days',
            'sentiment_difference': stats1['avg_sentiment'] - stats2['avg_sentiment'],
            'certainty_difference': stats1['avg_certainty'] - stats2['avg_certainty'],
            'change_frequency_difference': stats1['change_frequency'] - stats2['change_frequency'],
            'model1_stats': stats1,
            'model2_stats': stats2
        }
    
    def get_disagreement_prompts(self, model1: str, model2: str) -> List[str]:
        """Find prompts where two models strongly disagree"""
        disagreements = []
        
        for dilemma_id in [f"{i:03d}" for i in range(1, 51)]:
            responses1 = self.database.get_responses_for_prompt(dilemma_id, model1)
            responses2 = self.database.get_responses_for_prompt(dilemma_id, model2)
            
            if responses1 and responses2:
                # Compare most recent responses
                latest1 = responses1[0]
                latest2 = responses2[0]
                
                # Check if stances are opposite
                stance_values = {
                    EthicalStance.STRONGLY_OPPOSED: -2,
                    EthicalStance.OPPOSED: -1,
                    EthicalStance.CONFLICTED: 0,
                    EthicalStance.NEUTRAL: 0,
                    EthicalStance.SUPPORTIVE: 1,
                    EthicalStance.STRONGLY_SUPPORTIVE: 2,
                    EthicalStance.REFUSE_TO_ANSWER: 0
                }
                
                val1 = stance_values[latest1.stance]
                val2 = stance_values[latest2.stance]
                
                # If they're on opposite sides (different signs)
                if val1 * val2 < 0 and abs(val1 - val2) >= 2:
                    disagreements.append(dilemma_id)
        
        return disagreements
