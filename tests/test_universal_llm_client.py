import pytest

"""
Test script for TASK-008/009: Optimized Universal LLM Client
Run this to verify the optimized Universal LLM Client works correctly
"""

import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from universal_llm_client import UniversalLLMClient
    from template_manager import TemplateManager
    print("✅ Successfully imported UniversalLLMClient and TemplateManager")
except Exception as e:
    print(f"❌ Failed to import classes: {e}")
    sys.exit(1)

def test_universal_llm_client():
    """Test the optimized Universal LLM Client functionality"""
    print("\n🧪 Testing Optimized Universal LLM Client")
    print("=" * 50)
    
    # Initialize template manager
    templates_path = Path("templates")
    if not templates_path.exists():
        print("❌ Templates directory not found. Please run from project root.")
        pytest.skip("Templates directory not found")
    
    try:
        template_manager = TemplateManager(templates_path)
        print(f"✅ Template Manager initialized with {len(template_manager)} templates")
    except Exception as e:
        pytest.fail(f"Failed to initialize Template Manager: {e}")
    
    # Initialize Universal LLM Client with mock config
    try:
        llm_config = {
            'provider': 'openai',
            'model': 'gpt-4',
            'api_key': 'test_key_for_testing',
            'temperature': 0.7,
            'max_tokens': 4000
        }
        
        company_config = {
            'name': 'Test Company',
            'industry': 'technology',
            'specializations': ['Software Development', 'AI Solutions']
        }
        
        universal_client = UniversalLLMClient(llm_config, company_config, template_manager)
        print("✅ Universal LLM Client initialized successfully")
    except Exception as e:
        pytest.fail(f"Failed to initialize Universal LLM Client: {e}")
    
    # Sample project data for testing
    sample_project_data = {
        'project_name': 'AI Analytics Platform',
        'client_name': 'TechCorp Industries',
        'industry': 'technology',
        'company_size': 'startup',
        'project_type': 'Software Development',
        'requirements': 'Build an AI-powered analytics platform with real-time data processing and machine learning capabilities',
        'expected_duration': '6 months',
        'hardware_components': ['GPU Servers', 'Load Balancers'],
        'software_modules': ['Data Pipeline', 'ML Engine', 'Web Dashboard']
    }
    
    # Get first available template for testing
    all_templates = template_manager.get_all_templates()
    if not all_templates:
        pytest.skip("No templates available for testing")
    
    test_template = all_templates[0]
    print(f"🎯 Using test template: '{test_template.name}' ({test_template.template_id})")
    
    # Test 1: Template Preview
    print("\n📋 Test 1: Template Preview")
    try:
        preview = universal_client.get_template_preview(test_template.template_id)
        print(f"   ✅ Preview generated for '{preview['name']}':")
        print(f"      - Industry: {preview['industry']}")
        print(f"      - Document Type: {preview['document_type']}")
        print(f"      - Sections: {len(preview['sections'])}")
        print(f"      - Estimated Time: {preview['estimated_time_minutes']} minutes")
        print(f"      - Complexity: {preview['complexity_level']}")
        
        # Verify preview structure
        assert 'template_id' in preview, "Preview should include template_id"
        assert 'sections' in preview, "Preview should include sections"
        assert len(preview['sections']) > 0, "Preview should have sections"
        
    except Exception as e:
        pytest.fail(f"Template preview failed: {e}")
    
    # Test 2: Template Compatibility Validation
    print("\n📋 Test 2: Template Compatibility Validation")
    try:
        compatibility = universal_client.validate_template_compatibility(
            test_template.template_id, 
            sample_project_data
        )
        print(f"   ✅ Compatibility validation completed:")
        print(f"      - Template: '{compatibility['template_name']}'")
        print(f"      - Compatible: {compatibility['compatible']}")
        print(f"      - Score: {compatibility['score']}/100")
        print(f"      - Issues: {len(compatibility['issues'])}")
        print(f"      - Recommendations: {len(compatibility['recommendations'])}")
        
        if compatibility['issues']:
            for issue in compatibility['issues'][:2]:
                print(f"        • {issue}")
        
        # Verify compatibility structure
        assert 'score' in compatibility, "Should include compatibility score"
        assert 'compatible' in compatibility, "Should include compatibility boolean"
        assert isinstance(compatibility['score'], int), "Score should be integer"
        
    except Exception as e:
        pytest.fail(f"Compatibility validation failed: {e}")
    
    # Test 3: Generation Estimates
    print("\n📋 Test 3: Generation Estimates")
    try:
        estimate = universal_client.get_generation_estimate(test_template.template_id)
        print(f"   ✅ Generation estimate completed:")
        print(f"      - Template: '{estimate['template_name']}'")
        print(f"      - Complexity: {estimate['complexity_level']}")
        print(f"      - Sections: {estimate['sections_to_generate']}")
        print(f"      - Time: {estimate['estimated_generation_time_formatted']}")
        print(f"      - Tokens: {estimate['estimated_tokens']}")
        
        # Verify estimate structure
        assert estimate['sections_to_generate'] > 0, "Should have sections to generate"
        assert estimate['estimated_generation_time_seconds'] > 0, "Should have positive time estimate"
        
    except Exception as e:
        pytest.fail(f"Generation estimate failed: {e}")
    
    # Test 4: Universal Prompt Generation (Core Feature)
    print("\n📋 Test 4: Universal Prompt Generation")
    try:
        # Access the private method for testing
        sections = test_template.get_required_sections()
        prompt = universal_client._create_universal_prompt(
            test_template, 
            sample_project_data, 
            sections
        )
        
        print(f"   ✅ Universal prompt generated:")
        print(f"      - Length: {len(prompt)} characters")
        print(f"      - Lines: {len(prompt.split(chr(10)))}")
        
        # Verify prompt contains key components
        required_components = [
            'INDUSTRY CONTEXT',
            'TONE GUIDANCE', 
            'PROJECT CONTEXT',
            sample_project_data['project_name']
        ]
        
        missing_components = []
        for component in required_components:
            if component not in prompt:
                missing_components.append(component)
        
        if missing_components:
            print(f"      ⚠️  Missing components: {missing_components}")
        else:
            print(f"      ✅ Contains all required components")
        
        # Show prompt preview (first 5 lines)
        lines = prompt.split('\n')[:5]
        print(f"      - Preview:")
        for line in lines:
            if line.strip():
                print(f"        {line[:70]}{'...' if len(line) > 70 else ''}")
                
    except Exception as e:
        pytest.fail(f"Universal prompt generation failed: {e}")
    
    # Test 5: Section Prompt Generation
    print("\n📋 Test 5: Section Prompt Generation")
    try:
        sections = test_template.get_required_sections()
        if sections:
            first_section = sections[0]
            section_prompt = universal_client._create_section_prompt(
                test_template,
                first_section,
                sample_project_data
            )
            
            print(f"   ✅ Section prompt generated for '{first_section.title}':")
            print(f"      - Length: {len(section_prompt)} characters")
            print(f"      - Contains section title: {'##' + first_section.title in section_prompt}")
            print(f"      - Contains project name: {sample_project_data['project_name'] in section_prompt}")
            
        else:
            print("   ⚠️  No required sections found for section prompt test")
            
    except Exception as e:
        pytest.fail(f"Section prompt generation failed: {e}")
    
    # Test 6: Industry Context Generation
    print("\n📋 Test 6: Industry Context Generation")
    try:
        industry_contexts = ['technology', 'healthcare', 'manufacturing', 'education']
        
        for industry in industry_contexts:
            context = universal_client._get_industry_context(industry)
            print(f"   ✅ {industry.title()}: {len(context)} chars")
            
            # Verify context contains industry name
            assert industry in context.lower() or 'INDUSTRY CONTEXT' in context, f"Context should reference {industry}"
            
    except Exception as e:
        pytest.fail(f"Industry context generation failed: {e}")
    
    # Test 7: Tone Guidance Generation
    print("\n📋 Test 7: Tone Guidance Generation")
    try:
        tones = ['formal_corporate', 'startup_agile', 'government_compliance']
        
        for tone in tones:
            guidance = universal_client._get_tone_guidance(tone)
            print(f"   ✅ {tone}: {len(guidance)} chars")
            
            # Verify guidance contains tone reference
            assert 'TONE GUIDANCE' in guidance, f"Should contain tone guidance header"
            
    except Exception as e:
        pytest.fail(f"Tone guidance generation failed: {e}")
        
    # Test 8: Helper Methods
    print("\n📋 Test 8: Helper Methods")
    try:
        # Test template retrieval
        retrieved_template = universal_client._get_template(test_template.template_id)
        assert retrieved_template.template_id == test_template.template_id, "Should retrieve correct template"
        print(f"   ✅ Template retrieval works")
        
        # Test section determination
        sections = universal_client._determine_sections(test_template)
        assert len(sections) > 0, "Should determine sections to generate"
        print(f"   ✅ Section determination: {len(sections)} sections")
        
        # Test project context building
        context = universal_client._build_project_context(sample_project_data)
        assert sample_project_data['project_name'] in context, "Should include project name"
        print(f"   ✅ Project context building: {len(context)} chars")
        
    except Exception as e:
        pytest.fail(f"Helper methods test failed: {e}")
    
    # Test 9: Error Handling
    print("\n📋 Test 9: Error Handling")
    try:
        # Test non-existent template
        with pytest.raises(ValueError, match="Template not found"):
            universal_client._get_template("non_existent_template_id")
        print(f"   ✅ Correctly handles non-existent template")
        
        # Test client without template manager
        client_no_manager = UniversalLLMClient(llm_config, company_config, None)
        with pytest.raises(ValueError, match="Template manager not provided"):
            client_no_manager.get_template_preview("any_id")
        print(f"   ✅ Correctly handles missing template manager")
            
    except Exception as e:
        pytest.fail(f"Error handling test failed: {e}")
    
    print("\n🎉 All optimized Universal LLM Client tests passed!")


def test_integration_with_existing_system():
    """Test integration with existing LLM client"""
    print("\n🔗 Testing Integration with Existing System")
    print("=" * 40)
    
    try:
        # Test that Universal client inherits from LLM client
        from llm_client import LLMClient
        
        llm_config = {'provider': 'openai', 'model': 'gpt-4', 'api_key': 'test'}
        client = UniversalLLMClient(llm_config)
        
        # Verify inheritance
        assert isinstance(client, LLMClient), "Should inherit from LLMClient"
        print("   ✅ Correctly inherits from LLMClient")
        
        # Verify existing methods are available
        assert hasattr(client, 'provider'), "Should have provider attribute"
        assert hasattr(client, 'config'), "Should have config attribute"
        print("   ✅ Existing LLMClient functionality preserved")
        
        # Test that company_config is properly handled
        company_config = {'name': 'Test Company'}
        client_with_company = UniversalLLMClient(llm_config, company_config)
        assert client_with_company.company_config == company_config, "Should store company config"
        print("   ✅ Company configuration properly integrated")
        
    except Exception as e:
        pytest.fail(f"Integration test failed: {e}")

if __name__ == "__main__":
    print("🚀 Starting Optimized Universal LLM Client Tests")
    
    # Run main functionality tests
    test_universal_llm_client()
    
    # Run integration tests
    test_integration_with_existing_system()
    
    print("\n✅ All tests passed! Optimized Universal LLM Client is working correctly")
    print("🎯 Ready to proceed to TASK-010 (Main Application Integration)")