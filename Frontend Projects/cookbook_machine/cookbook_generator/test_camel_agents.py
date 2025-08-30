#!/usr/bin/env python3
"""
Test Suite for CAMEL AI Cookbook Generator

This comprehensive test suite validates the CAMEL AI multi-agent system
implementation including environment setup, imports, configuration,
and agent creation.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

class TestEnvironmentSetup(unittest.TestCase):
    """Test environment configuration and API key validation"""
    
    def test_python_version(self):
        """Ensure Python version is 3.8 or higher"""
        self.assertGreaterEqual(sys.version_info.major, 3)
        self.assertGreaterEqual(sys.version_info.minor, 8)
    
    @patch.dict(os.environ, {'GOOGLE_API_KEY': 'test_google_key', 'ANTHROPIC_API_KEY': 'test_anthropic_key'})
    def test_api_keys_validation(self):
        """Test API key validation with mock environment variables"""
        from camel_config import camel_config
        
        # Should not raise an exception with both keys set
        try:
            camel_config.validate_environment()
            validation_passed = True
        except ValueError:
            validation_passed = False
        
        self.assertTrue(validation_passed, "Environment validation should pass with both API keys set")
    
    def test_missing_api_keys(self):
        """Test validation fails when API keys are missing"""
        from camel_config import camel_config
        
        # Clear environment variables for this test
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError) as context:
                camel_config.validate_environment()
            
            error_msg = str(context.exception)
            self.assertIn("GOOGLE_API_KEY", error_msg)
            self.assertIn("ANTHROPIC_API_KEY", error_msg)

class TestCAMELImports(unittest.TestCase):
    """Test that all required CAMEL AI components can be imported"""
    
    def test_camel_models_import(self):
        """Test CAMEL AI ModelFactory import"""
        try:
            from camel.models import ModelFactory
            self.assertTrue(True, "ModelFactory imported successfully")
        except ImportError as e:
            self.fail(f"Failed to import ModelFactory: {e}")
    
    def test_camel_types_import(self):
        """Test CAMEL AI types import"""
        try:
            from camel.types import ModelPlatformType
            self.assertTrue(True, "ModelPlatformType imported successfully")
        except ImportError as e:
            self.fail(f"Failed to import ModelPlatformType: {e}")
    
    def test_camel_agents_import(self):
        """Test CAMEL AI ChatAgent import"""
        try:
            from camel.agents import ChatAgent
            self.assertTrue(True, "ChatAgent imported successfully")
        except ImportError as e:
            self.fail(f"Failed to import ChatAgent: {e}")
    
    def test_camel_messages_import(self):
        """Test CAMEL AI BaseMessage import"""
        try:
            from camel.messages import BaseMessage
            self.assertTrue(True, "BaseMessage imported successfully")
        except ImportError as e:
            self.fail(f"Failed to import BaseMessage: {e}")

class TestConfigurationSystem(unittest.TestCase):
    """Test the CAMEL AI configuration system"""
    
    def test_config_import(self):
        """Test configuration module import"""
        try:
            from camel_config import camel_config
            self.assertTrue(True, "Configuration imported successfully")
        except ImportError as e:
            self.fail(f"Failed to import configuration: {e}")
    
    def test_agent_configs_exist(self):
        """Test that all agent configurations are defined"""
        from camel_config import CAMELConfig
        
        # Check that all required configurations exist
        self.assertTrue(hasattr(CAMELConfig, 'PLANNER_CONFIG'))
        self.assertTrue(hasattr(CAMELConfig, 'WRITER_CONFIG'))
        self.assertTrue(hasattr(CAMELConfig, 'ASSEMBLER_CONFIG'))
    
    def test_model_config_structure(self):
        """Test that model configurations have required fields"""
        from camel_config import camel_config
        
        for agent_type in ['planner', 'writer', 'assembler']:
            config = camel_config.get_model_config(agent_type)
            
            # Check required fields
            self.assertIn('model_platform', config)
            self.assertIn('model_type', config)
            self.assertIn('temperature', config)
            self.assertIn('max_tokens', config)
            
            # Check max_tokens is 60000 as requested
            self.assertEqual(config['max_tokens'], 60000)
    
    def test_planner_uses_gemini(self):
        """Test that planner agent uses Gemini platform"""
        from camel_config import camel_config
        from camel.types import ModelPlatformType
        
        config = camel_config.get_model_config('planner')
        self.assertEqual(config['model_platform'], ModelPlatformType.GEMINI)
        self.assertIn('gemini', config['model_type'].lower())
    
    def test_writer_and_assembler_use_gemini(self):
        """Test that writer and assembler agents use Gemini platform"""
        from camel_config import camel_config
        from camel.types import ModelPlatformType
        
        for agent_type in ['writer', 'assembler']:
            config = camel_config.get_model_config(agent_type)
            self.assertEqual(config['model_platform'], ModelPlatformType.GEMINI)
            self.assertIn('gemini', config['model_type'].lower())

class TestAgentCreation(unittest.TestCase):
    """Test CAMEL AI agent creation and initialization"""
    
    @patch.dict(os.environ, {'GOOGLE_API_KEY': 'test_google_key', 'ANTHROPIC_API_KEY': 'test_anthropic_key'})
    @patch('camel.models.ModelFactory.create')
    def test_planner_agent_creation(self, mock_model_factory):
        """Test planner agent can be created"""
        # Mock the model creation
        mock_model = MagicMock()
        mock_model_factory.return_value = mock_model
        
        try:
            from camel_config import camel_config
            from camel.agents import ChatAgent
            from camel.messages import BaseMessage
            
            config = camel_config.get_model_config('planner')
            
            # This should not raise an exception
            model = mock_model_factory(
                model_platform=config['model_platform'],
                model_type=config['model_type'],
                model_config_dict={
                    'temperature': config['temperature'],
                    'max_tokens': config['max_tokens']
                }
            )
            
            agent = ChatAgent(
                system_message=BaseMessage.make_assistant_message(
                    role_name="Test Planner",
                    content="Test system message"
                ),
                model=model
            )
            
            self.assertTrue(True, "Planner agent created successfully")
            
        except Exception as e:
            self.fail(f"Failed to create planner agent: {e}")
    
    @patch.dict(os.environ, {'GOOGLE_API_KEY': 'test_google_key', 'ANTHROPIC_API_KEY': 'test_anthropic_key'})
    @patch('camel.models.ModelFactory.create')
    def test_writer_agent_creation(self, mock_model_factory):
        """Test writer agent can be created"""
        # Mock the model creation
        mock_model = MagicMock()
        mock_model_factory.return_value = mock_model
        
        try:
            from camel_config import camel_config
            from camel.agents import ChatAgent
            from camel.messages import BaseMessage
            
            config = camel_config.get_model_config('writer')
            
            # This should not raise an exception
            model = mock_model_factory(
                model_platform=config['model_platform'],
                model_type=config['model_type'],
                model_config_dict={
                    'temperature': config['temperature'],
                    'max_tokens': config['max_tokens']
                }
            )
            
            agent = ChatAgent(
                system_message=BaseMessage.make_assistant_message(
                    role_name="Test Writer",
                    content="Test system message"
                ),
                model=model
            )
            
            self.assertTrue(True, "Writer agent created successfully")
            
        except Exception as e:
            self.fail(f"Failed to create writer agent: {e}")

class TestPromptTemplates(unittest.TestCase):
    """Test that prompt templates are properly configured"""
    
    def test_planner_prompt_import(self):
        """Test planner prompt template import"""
        try:
            from prompts.planner_prompt import PLANNER_PROMPT
            self.assertIsInstance(PLANNER_PROMPT, str)
            self.assertGreater(len(PLANNER_PROMPT), 0)
        except ImportError as e:
            self.fail(f"Failed to import planner prompt: {e}")
    
    def test_writer_prompt_import(self):
        """Test writer prompt template import"""
        try:
            from prompts.writer_prompt import WRITER_PROMPT
            self.assertIsInstance(WRITER_PROMPT, str)
            self.assertGreater(len(WRITER_PROMPT), 0)
        except ImportError as e:
            self.fail(f"Failed to import writer prompt: {e}")

def run_tests():
    """Run all tests and display results"""
    
    print("🧪 CAMEL AI Cookbook Generator - Test Suite")
    print("=" * 50)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestEnvironmentSetup,
        TestCAMELImports, 
        TestConfigurationSystem,
        TestAgentCreation,
        TestPromptTemplates
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 50)
    print("🎯 Test Summary:")
    print(f"✅ Tests Run: {result.testsRun}")
    print(f"❌ Failures: {len(result.failures)}")
    print(f"⚠️  Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ Failures:")
        for test, failure in result.failures:
            print(f"  - {test}: {failure}")
    
    if result.errors:
        print("\n⚠️  Errors:")
        for test, error in result.errors:
            print(f"  - {test}: {error}")
    
    if result.wasSuccessful():
        print("\n🎉 All tests passed! CAMEL AI system is ready.")
    else:
        print("\n🔧 Some tests failed. Please check the configuration.")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1) 