"""
Simple test to verify the AI Ethics Testing Framework works correctly
"""

import asyncio
import tempfile
import os
from pathlib import Path

from src.models import EthicalDilemma, DilemmaCategory, EthicalStance
from src.database import EthicsDatabase, DilemmaLoader
from src.analysis import ResponseAnalyzer
from src.testing import MockAIModel, EthicsTestRunner


def test_models():
    """Test the core data models"""
    print("Testing data models...")
    
    # Test EthicalDilemma
    dilemma = EthicalDilemma(
        id="001",
        category=DilemmaCategory.AI_SELF_LIMITS,
        prompt="Test prompt?",
        tags=["test", "prompt"]
    )
    assert dilemma.id == "001"
    assert dilemma.category == DilemmaCategory.AI_SELF_LIMITS
    print("✅ EthicalDilemma model works")
    
    # Test analysis
    analyzer = ResponseAnalyzer()
    response = analyzer.analyze_response(
        "001", "test-model", "This is clearly unethical and wrong."
    )
    assert response.stance in [EthicalStance.OPPOSED, EthicalStance.STRONGLY_OPPOSED]
    assert response.sentiment_score < 0
    print("✅ Response analysis works")


def test_database():
    """Test database operations"""
    print("Testing database...")
    
    # Use temporary database
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    try:
        db = EthicsDatabase(db_path)
        
        # Test response saving
        analyzer = ResponseAnalyzer()
        response = analyzer.analyze_response(
            "001", "test-model", "This is a test response."
        )
        db.save_response(response)
        
        # Test retrieval
        responses = db.get_responses_for_prompt("001")
        assert len(responses) == 1
        assert responses[0].model == "test-model"
        print("✅ Database operations work")
        
    finally:
        os.unlink(db_path)


async def test_mock_model():
    """Test the mock AI model"""
    print("Testing mock AI model...")
    
    model = MockAIModel("test-ai")
    response = await model.get_response("Should we allow surveillance?")
    assert len(response) > 0
    assert "surveillance" in response.lower()
    print("✅ Mock AI model works")


async def test_integration():
    """Test full integration"""
    print("Testing full integration...")
    
    # Use temporary database
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    try:
        # Create test runner
        runner = EthicsTestRunner(db_path)
        
        # Test with just first 3 dilemmas
        model = MockAIModel("integration-test")
        
        # Test individual dilemma
        test_dilemma = EthicalDilemma(
            id="test",
            category=DilemmaCategory.AI_SELF_LIMITS,
            prompt="Is AI testing ethical?",
            tags=["testing"]
        )
        
        response = await runner.run_single_test(model, test_dilemma)
        assert response.model == "integration-test"
        assert response.prompt_id == "test"
        print("✅ Single test execution works")
        
        # Test statistics
        stats = runner.get_model_summary("integration-test")
        assert stats['model'] == "integration-test"
        print("✅ Statistics generation works")
        
    finally:
        os.unlink(db_path)


def test_dilemma_loading():
    """Test loading ethical dilemmas"""
    print("Testing dilemma loading...")
    
    # Check if the file exists
    dilemma_file = "ethical_dilemmas.json"
    if os.path.exists(dilemma_file):
        dilemmas = DilemmaLoader.load_dilemmas(dilemma_file)
        assert len(dilemmas) == 50
        assert all(isinstance(d, EthicalDilemma) for d in dilemmas)
        print("✅ Dilemma loading works")
    else:
        print("⚠️  Skipping dilemma loading test (file not found)")


async def run_all_tests():
    """Run all tests"""
    print("🧪 Running AI Ethics Framework Tests")
    print("=" * 50)
    
    test_models()
    test_database()
    await test_mock_model()
    await test_integration()
    test_dilemma_loading()
    
    print("\n🎉 All tests passed!")
    print("\nThe AI Ethics Testing Framework is ready to use!")
    print("\nNext steps:")
    print("- Run 'python demo.py' for a full demonstration")
    print("- Run 'python main.py web' to launch the dashboard")
    print("- Integrate real AI models for actual testing")


if __name__ == "__main__":
    asyncio.run(run_all_tests())
