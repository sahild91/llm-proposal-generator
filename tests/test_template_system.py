"""
Test Template System - Pytest Compatible
Comprehensive test suite for template data classes and validation
"""

import sys
import os
from pathlib import Path
import tempfile
import yaml
import pytest

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from template_system import (
    DocumentTemplate, TemplateSection, UsageStats,
    IndustryType, CompanySize, ToneStyle, DocumentType, ComplexityLevel,
    TemplateValidationError, validate_template_file, load_template_from_file
)


class TestEnumDefinitions:
    """Test all enum definitions"""
    
    def test_industry_type_enum(self):
        """Test IndustryType enum"""
        industries = [e.value for e in IndustryType]
        expected_industries = ['technology', 'manufacturing', 'services', 'business', 
                              'healthcare', 'education', 'retail', 'logistics', 'finance', 'legal']
        
        for expected in expected_industries:
            assert expected in industries, f"IndustryType should contain {expected}"
        assert len(industries) == len(expected_industries)
    
    def test_company_size_enum(self):
        """Test CompanySize enum"""
        sizes = [e.value for e in CompanySize]
        expected_sizes = ['startup', 'small', 'medium', 'large', 'enterprise']
        
        for expected in expected_sizes:
            assert expected in sizes, f"CompanySize should contain {expected}"
        assert len(sizes) == len(expected_sizes)
    
    def test_tone_style_enum(self):
        """Test ToneStyle enum"""
        tones = [e.value for e in ToneStyle]
        expected_tones = ['formal_corporate', 'startup_agile', 'government_compliance', 
                         'academic_research', 'consulting_professional']
        
        for expected in expected_tones:
            assert expected in tones, f"ToneStyle should contain {expected}"
        assert len(tones) == len(expected_tones)
    
    def test_document_type_enum(self):
        """Test DocumentType enum"""
        doc_types = [e.value for e in DocumentType]
        expected_doc_types = ['proposal', 'report', 'manual', 'plan', 'specification', 'policy', 'agreement']
        
        for expected in expected_doc_types:
            assert expected in doc_types, f"DocumentType should contain {expected}"
        assert len(doc_types) == len(expected_doc_types)
    
    def test_complexity_level_enum(self):
        """Test ComplexityLevel enum"""
        complexities = [e.value for e in ComplexityLevel]
        expected_complexities = ['low', 'medium', 'high']
        
        for expected in expected_complexities:
            assert expected in complexities, f"ComplexityLevel should contain {expected}"
        assert len(complexities) == len(expected_complexities)


class TestTemplateSection:
    """Test TemplateSection data class"""
    
    def test_valid_section_creation(self):
        """Test creating a valid TemplateSection"""
        section = TemplateSection(
            id="test_section",
            title="Test Section",
            required=True,
            order=1,
            prompt_template="This is a test prompt template for the section."
        )
        
        assert section.id == "test_section"
        assert section.title == "Test Section"
        assert section.required is True
        assert section.order == 1
        assert "test prompt template" in section.prompt_template.lower()
    
    def test_empty_section_id_raises_error(self):
        """Test that empty section ID raises ValueError"""
        with pytest.raises(ValueError, match="Section ID cannot be empty"):
            TemplateSection(
                id="",
                title="Test",
                required=True,
                order=1,
                prompt_template="Test prompt"
            )
    
    def test_empty_section_title_raises_error(self):
        """Test that empty section title raises ValueError"""
        with pytest.raises(ValueError, match="Section title cannot be empty"):
            TemplateSection(
                id="test",
                title="",
                required=True,
                order=1,
                prompt_template="Test prompt"
            )
    
    def test_invalid_section_order_raises_error(self):
        """Test that invalid section order raises ValueError"""
        with pytest.raises(ValueError, match="Section order must be >= 1"):
            TemplateSection(
                id="test",
                title="Test",
                required=True,
                order=0,
                prompt_template="Test prompt"
            )


class TestUsageStats:
    """Test UsageStats data class"""
    
    def test_default_usage_stats(self):
        """Test default UsageStats creation"""
        stats = UsageStats()
        assert stats.created_date == ""
        assert stats.last_modified == ""
        assert stats.usage_count == 0
        assert stats.success_rate == 0.0
    
    def test_custom_usage_stats(self):
        """Test custom UsageStats creation"""
        stats = UsageStats(
            created_date="2024-01-01",
            last_modified="2024-01-02",
            usage_count=10,
            success_rate=0.95
        )
        assert stats.created_date == "2024-01-01"
        assert stats.last_modified == "2024-01-02"
        assert stats.usage_count == 10
        assert stats.success_rate == 0.95


class TestDocumentTemplate:
    """Test DocumentTemplate creation and validation"""
    
    @pytest.fixture
    def valid_sections(self):
        """Fixture providing valid sections"""
        return [
            TemplateSection(
                id="section1",
                title="Section 1",
                required=True,
                order=1,
                prompt_template="First section prompt"
            ),
            TemplateSection(
                id="section2",
                title="Section 2", 
                required=False,
                order=2,
                prompt_template="Second section prompt"
            )
        ]
    
    def test_valid_template_creation(self, valid_sections):
        """Test creating a valid DocumentTemplate"""
        template = DocumentTemplate(
            template_id="test_template",
            name="Test Template",
            description="A test template for validation",
            version="1.0",
            industry=IndustryType.TECHNOLOGY,
            category="test_category",
            document_type=DocumentType.PROPOSAL,
            company_sizes=[CompanySize.STARTUP, CompanySize.SMALL],
            tone=ToneStyle.STARTUP_AGILE,
            sections=valid_sections
        )
        
        assert template.template_id == "test_template"
        assert template.name == "Test Template"
        assert len(template.sections) == 2
        assert template.industry == IndustryType.TECHNOLOGY
    
    def test_empty_template_id_raises_error(self, valid_sections):
        """Test that empty template ID raises ValueError"""
        with pytest.raises(ValueError, match="Template ID cannot be empty"):
            DocumentTemplate(
                template_id="",
                name="Test",
                description="Test",
                version="1.0",
                industry=IndustryType.TECHNOLOGY,
                category="test",
                document_type=DocumentType.PROPOSAL,
                company_sizes=[CompanySize.STARTUP],
                tone=ToneStyle.STARTUP_AGILE,
                sections=valid_sections
            )
    
    def test_invalid_section_ordering_raises_error(self):
        """Test that invalid section ordering raises ValueError"""
        invalid_sections = [
            TemplateSection("s1", "S1", True, 1, "prompt"),
            TemplateSection("s2", "S2", True, 3, "prompt")  # Gap in ordering
        ]
        
        with pytest.raises(ValueError, match="Section orders must be consecutive"):
            DocumentTemplate(
                template_id="test",
                name="Test",
                description="Test",
                version="1.0",
                industry=IndustryType.TECHNOLOGY,
                category="test",
                document_type=DocumentType.PROPOSAL,
                company_sizes=[CompanySize.STARTUP],
                tone=ToneStyle.STARTUP_AGILE,
                sections=invalid_sections
            )
    
    def test_no_required_sections_raises_error(self):
        """Test that templates with no required sections raise ValueError"""
        optional_sections = [
            TemplateSection("s1", "S1", False, 1, "prompt"),
            TemplateSection("s2", "S2", False, 2, "prompt")
        ]
        
        with pytest.raises(ValueError, match="at least one required section"):
            DocumentTemplate(
                template_id="test",
                name="Test",
                description="Test",
                version="1.0",
                industry=IndustryType.TECHNOLOGY,
                category="test",
                document_type=DocumentType.PROPOSAL,
                company_sizes=[CompanySize.STARTUP],
                tone=ToneStyle.STARTUP_AGILE,
                sections=optional_sections
            )


class TestYamlLoading:
    """Test YAML loading functionality"""
    
    @pytest.fixture
    def sample_yaml_data(self):
        """Sample YAML data for testing"""
        return {
            'template_id': 'yaml_test_template',
            'name': 'YAML Test Template',
            'description': 'A template for testing YAML loading',
            'version': '1.0',
            'industry': 'technology',
            'category': 'software_development',
            'document_type': 'proposal',
            'company_sizes': ['startup', 'small'],
            'tone': 'startup_agile',
            'structure': {
                'sections': [
                    {
                        'id': 'intro',
                        'title': 'Introduction',
                        'required': True,
                        'order': 1,
                        'prompt_template': 'Write an introduction section.'
                    },
                    {
                        'id': 'conclusion',
                        'title': 'Conclusion',
                        'required': False,
                        'order': 2,
                        'prompt_template': 'Write a conclusion section.'
                    }
                ]
            },
            'estimated_time_minutes': 30,
            'complexity_level': 'medium',
            'usage_stats': {
                'created_date': '2024-01-01',
                'usage_count': 5,
                'success_rate': 0.8
            }
        }
    
    def test_yaml_file_loading(self, sample_yaml_data, tmp_path):
        """Test loading template from YAML file"""
        # Create temporary YAML file
        yaml_file = tmp_path / "test_template.yaml"
        with open(yaml_file, 'w') as f:
            yaml.dump(sample_yaml_data, f, default_flow_style=False)
        
        # Load template
        template = DocumentTemplate.from_yaml_file(yaml_file)
        
        assert template.template_id == 'yaml_test_template'
        assert template.name == 'YAML Test Template'
        assert len(template.sections) == 2
        assert template.sections[0].id == 'intro'
        assert template.usage_stats.usage_count == 5
    
    def test_dictionary_conversion(self, sample_yaml_data):
        """Test template to dictionary conversion"""
        template = DocumentTemplate.from_dict(sample_yaml_data)
        template_dict = template.to_dict()
        
        assert template_dict['template_id'] == 'yaml_test_template'
        assert len(template_dict['structure']['sections']) == 2
    
    def test_nonexistent_file_raises_error(self, tmp_path):
        """Test that loading non-existent file raises FileNotFoundError"""
        non_existent = tmp_path / "does_not_exist.yaml"
        
        with pytest.raises(FileNotFoundError):
            DocumentTemplate.from_yaml_file(non_existent)
    
    def test_invalid_yaml_raises_error(self, tmp_path):
        """Test that invalid YAML raises ValueError"""
        invalid_yaml_file = tmp_path / "invalid.yaml"
        with open(invalid_yaml_file, 'w') as f:
            f.write("invalid: yaml: content: [[[")
        
        with pytest.raises(ValueError, match="Invalid YAML"):
            DocumentTemplate.from_yaml_file(invalid_yaml_file)


class TestTemplateValidation:
    """Test template validation functions"""
    
    def test_valid_template_validation(self, tmp_path):
        """Test validation of valid template"""
        valid_yaml = {
            'template_id': 'validation_test',
            'name': 'Validation Test Template',
            'description': 'Testing validation',
            'version': '1.0',
            'industry': 'technology',
            'category': 'software_development',
            'document_type': 'proposal',
            'company_sizes': ['startup'],
            'tone': 'startup_agile',
            'structure': {
                'sections': [
                    {
                        'id': 'section1',
                        'title': 'Section 1',
                        'required': True,
                        'order': 1,
                        'prompt_template': 'This is a sufficiently long prompt template for testing validation.'
                    }
                ]
            }
        }
        
        yaml_file = tmp_path / "valid_template.yaml"
        with open(yaml_file, 'w') as f:
            yaml.dump(valid_yaml, f, default_flow_style=False)
        
        issues = validate_template_file(yaml_file)
        assert len(issues) == 0, f"Valid template should have no issues, got: {issues}"
    
    def test_load_template_from_file_function(self, tmp_path):
        """Test load_template_from_file function"""
        valid_yaml = {
            'template_id': 'load_test',
            'name': 'Load Test Template',
            'description': 'Testing loading function',
            'version': '1.0',
            'industry': 'technology',
            'category': 'software_development',
            'document_type': 'proposal',
            'company_sizes': ['startup'],
            'tone': 'startup_agile',
            'structure': {
                'sections': [
                    {
                        'id': 'section1',
                        'title': 'Section 1',
                        'required': True,
                        'order': 1,
                        'prompt_template': 'Sufficient length prompt template for testing.'
                    }
                ]
            }
        }
        
        yaml_file = tmp_path / "load_test.yaml"
        with open(yaml_file, 'w') as f:
            yaml.dump(valid_yaml, f, default_flow_style=False)
        
        template = load_template_from_file(yaml_file)
        assert template.template_id == 'load_test'


class TestTemplateMethods:
    """Test template utility methods"""
    
    @pytest.fixture
    def sample_template(self):
        """Sample template for testing methods"""
        sections = [
            TemplateSection("req1", "Required 1", True, 1, "Required section 1"),
            TemplateSection("opt1", "Optional 1", False, 2, "Optional section 1"),
            TemplateSection("req2", "Required 2", True, 3, "Required section 2")
        ]
        
        return DocumentTemplate(
            template_id="method_test",
            name="Method Test Template",
            description="Testing methods",
            version="1.0",
            industry=IndustryType.TECHNOLOGY,
            category="test",
            document_type=DocumentType.PROPOSAL,
            company_sizes=[CompanySize.STARTUP, CompanySize.SMALL],
            tone=ToneStyle.STARTUP_AGILE,
            sections=sections
        )
    
    def test_get_sections_by_order(self, sample_template):
        """Test getting sections ordered by order field"""
        ordered_sections = sample_template.get_sections_by_order()
        assert len(ordered_sections) == 3
        assert ordered_sections[0].order == 1
        assert ordered_sections[2].order == 3
    
    def test_get_required_sections(self, sample_template):
        """Test getting only required sections"""
        required_sections = sample_template.get_required_sections()
        assert len(required_sections) == 2
        for section in required_sections:
            assert section.required is True
    
    def test_get_optional_sections(self, sample_template):
        """Test getting only optional sections"""
        optional_sections = sample_template.get_optional_sections()
        assert len(optional_sections) == 1
        for section in optional_sections:
            assert section.required is False
    
    def test_is_suitable_for_company(self, sample_template):
        """Test company size suitability check"""
        assert sample_template.is_suitable_for_company(CompanySize.STARTUP) is True
        assert sample_template.is_suitable_for_company(CompanySize.SMALL) is True
        assert sample_template.is_suitable_for_company(CompanySize.ENTERPRISE) is False
    
    def test_get_section_by_id(self, sample_template):
        """Test getting section by ID"""
        section = sample_template.get_section_by_id("req1")
        assert section is not None
        assert section.id == "req1"
        
        non_existent = sample_template.get_section_by_id("non_existent")
        assert non_existent is None
