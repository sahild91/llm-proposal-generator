"""
Pytest Configuration File
Shared fixtures and configuration for all tests
"""

import sys
import os
import pytest
import tempfile
import yaml
from pathlib import Path
from typing import Dict, Any

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.template_system import DocumentTemplate, TemplateSection, IndustryType, CompanySize, ToneStyle, DocumentType
from src.template_manager import TemplateManager


# =============================================================================
# PYTEST CONFIGURATION
# =============================================================================

def pytest_configure(config):
    """Configure pytest"""
    # Add custom markers
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection"""
    # Auto-mark slow tests
    for item in items:
        if "template_manager" in item.nodeid and "comprehensive" in item.name:
            item.add_marker(pytest.mark.slow)


# =============================================================================
# SHARED FIXTURES
# =============================================================================

@pytest.fixture(scope="session")
def project_root():
    """Get project root directory"""
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def templates_dir(project_root):
    """Get templates directory"""
    return project_root / "templates"


@pytest.fixture
def sample_template_data():
    """Sample template data for testing"""
    return {
        'template_id': 'test_template',
        'name': 'Test Template',
        'description': 'A template for testing purposes',
        'version': '1.0',
        'industry': 'technology',
        'category': 'software_development',
        'document_type': 'proposal',
        'company_sizes': ['startup', 'small'],
        'tone': 'startup_agile',
        'structure': {
            'sections': [
                {
                    'id': 'introduction',
                    'title': 'Introduction',
                    'required': True,
                    'order': 1,
                    'prompt_template': 'Write a compelling introduction that outlines the project objectives and value proposition.'
                },
                {
                    'id': 'approach',
                    'title': 'Technical Approach',
                    'required': True,
                    'order': 2,
                    'prompt_template': 'Detail the technical implementation approach including methodology and technology stack.'
                },
                {
                    'id': 'conclusion',
                    'title': 'Conclusion',
                    'required': False,
                    'order': 3,
                    'prompt_template': 'Summarize the key points and next steps for the project.'
                }
            ]
        },
        'estimated_time_minutes': 30,
        'complexity_level': 'medium',
        'prerequisites': ['Requirements defined', 'Stakeholders identified'],
        'compliance_requirements': ['Data protection compliance'],
        'usage_stats': {
            'created_date': '2024-01-01',
            'last_modified': '2024-01-01',
            'usage_count': 0,
            'success_rate': 0.0
        }
    }


@pytest.fixture
def sample_sections():
    """Sample template sections for testing"""
    return [
        TemplateSection(
            id="section1",
            title="First Section",
            required=True,
            order=1,
            prompt_template="This is the first section with a detailed prompt template for testing."
        ),
        TemplateSection(
            id="section2",
            title="Second Section",
            required=False,
            order=2,
            prompt_template="This is the second section with optional content for comprehensive testing."
        ),
        TemplateSection(
            id="section3",
            title="Third Section",
            required=True,
            order=3,
            prompt_template="This is the third section that provides additional required content for validation."
        )
    ]


@pytest.fixture
def sample_document_template(sample_sections):
    """Sample DocumentTemplate for testing"""
    return DocumentTemplate(
        template_id="sample_template",
        name="Sample Template",
        description="A sample template for testing purposes",
        version="1.0",
        industry=IndustryType.TECHNOLOGY,
        category="software_development",
        document_type=DocumentType.PROPOSAL,
        company_sizes=[CompanySize.STARTUP, CompanySize.SMALL],
        tone=ToneStyle.STARTUP_AGILE,
        sections=sample_sections
    )


@pytest.fixture
def temporary_yaml_file(sample_template_data):
    """Create a temporary YAML file with sample template data"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as tmp_file:
        yaml.dump(sample_template_data, tmp_file, default_flow_style=False)
        tmp_path = Path(tmp_file.name)
    
    yield tmp_path
    
    # Cleanup
    if tmp_path.exists():
        tmp_path.unlink()


@pytest.fixture
def temporary_templates_dir(sample_template_data):
    """Create a temporary templates directory with sample templates"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        
        # Create directory structure
        tech_dir = tmp_path / "technology" / "software_development"
        tech_dir.mkdir(parents=True, exist_ok=True)
        
        # Create sample template file
        template_file = tech_dir / "sample_template.yaml"
        with open(template_file, 'w') as f:
            yaml.dump(sample_template_data, f, default_flow_style=False)
        
        # Create additional template for variety
        variant_data = sample_template_data.copy()
        variant_data['template_id'] = 'test_template_variant'
        variant_data['name'] = 'Test Template Variant'
        variant_data['tone'] = 'formal_corporate'
        
        variant_file = tech_dir / "sample_template_variant.yaml"
        with open(variant_file, 'w') as f:
            yaml.dump(variant_data, f, default_flow_style=False)
        
        yield tmp_path


@pytest.fixture
def template_manager(temporary_templates_dir):
    """Template manager with temporary templates"""
    return TemplateManager(temporary_templates_dir)


@pytest.fixture
def company_profile():
    """Sample company profile for testing"""
    return {
        'industry': 'technology',
        'size': 'startup',
        'tone': 'startup_agile'
    }


@pytest.fixture
def project_context():
    """Sample project context for testing"""
    return {
        'type': 'software development',
        'duration': '3 months',
        'complexity': 'medium'
    }


# =============================================================================
# UTILITY FIXTURES
# =============================================================================

@pytest.fixture
def assert_template_valid():
    """Fixture that provides template validation function"""
    def _assert_valid(template: DocumentTemplate):
        """Assert that a template is valid"""
        assert template.template_id, "Template should have an ID"
        assert template.name, "Template should have a name"
        assert template.description, "Template should have a description"
        assert template.sections, "Template should have sections"
        assert len(template.sections) > 0, "Template should have at least one section"
        
        # Validate sections
        for section in template.sections:
            assert section.id, "Section should have an ID"
            assert section.title, "Section should have a title"
            assert section.prompt_template, "Section should have a prompt template"
            assert section.order > 0, "Section order should be positive"
        
        # Validate section ordering
        orders = [s.order for s in template.sections]
        orders.sort()
        expected_orders = list(range(1, len(orders) + 1))
        assert orders == expected_orders, "Section orders should be consecutive starting from 1"
        
        # At least one required section
        required_sections = [s for s in template.sections if s.required]
        assert len(required_sections) > 0, "Template should have at least one required section"
    
    return _assert_valid


@pytest.fixture
def create_test_template():
    """Fixture that provides function to create test templates"""
    def _create_template(template_id: str = "test_template", 
                        sections_count: int = 3,
                        industry: str = "technology",
                        **kwargs) -> DocumentTemplate:
        """Create a test template with specified parameters"""
        
        # Create sections
        sections = []
        for i in range(1, sections_count + 1):
            section = TemplateSection(
                id=f"section_{i}",
                title=f"Section {i}",
                required=(i == 1),  # First section is required
                order=i,
                prompt_template=f"This is section {i} with a comprehensive prompt template for testing purposes."
            )
            sections.append(section)
        
        # Default template parameters
        defaults = {
            'name': f'Test Template {template_id}',
            'description': f'A test template for {template_id}',
            'version': '1.0',
            'industry': IndustryType(industry),
            'category': 'test_category',
            'document_type': DocumentType.PROPOSAL,
            'company_sizes': [CompanySize.STARTUP],
            'tone': ToneStyle.STARTUP_AGILE,
            'sections': sections
        }
        
        # Override with any provided kwargs
        defaults.update(kwargs)
        
        return DocumentTemplate(
            template_id=template_id,
            **defaults
        )
    
    return _create_template


@pytest.fixture
def mock_llm_response():
    """Mock LLM response for testing"""
    return """
# Test Document

## Introduction
This is a test document generated for testing purposes.

## Technical Approach
The technical approach involves using modern best practices and proven methodologies.

## Conclusion
This concludes the test document with key recommendations and next steps.
"""


# =============================================================================
# PARAMETRIZED FIXTURES
# =============================================================================

@pytest.fixture(params=[
    'technology',
    'manufacturing', 
    'services',
    'healthcare',
    'education'
])
def industry_type(request):
    """Parametrized fixture for different industry types"""
    return request.param


@pytest.fixture(params=[
    'startup',
    'small',
    'medium',
    'large',
    'enterprise'
])
def company_size(request):
    """Parametrized fixture for different company sizes"""
    return request.param


@pytest.fixture(params=[
    'formal_corporate',
    'startup_agile',
    'government_compliance',
    'academic_research',
    'consulting_professional'
])
def tone_style(request):
    """Parametrized fixture for different tone styles"""
    return request.param


@pytest.fixture(params=[
    'proposal',
    'report', 
    'manual',
    'plan',
    'specification'
])
def document_type(request):
    """Parametrized fixture for different document types"""
    return request.param


# =============================================================================
# PERFORMANCE TESTING FIXTURES
# =============================================================================

@pytest.fixture
def large_template_library(tmp_path):
    """Create a large template library for performance testing"""
    base_template = {
        'name': 'Performance Test Template',
        'description': 'Template for performance testing',
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
                    'prompt_template': 'Performance test section with adequate length for validation.'
                }
            ]
        }
    }
    
    # Create multiple template files
    tech_dir = tmp_path / "technology" / "software_development"
    tech_dir.mkdir(parents=True, exist_ok=True)
    
    for i in range(50):  # Create 50 templates
        template_data = base_template.copy()
        template_data['template_id'] = f'perf_template_{i:03d}'
        template_data['name'] = f'Performance Template {i:03d}'
        
        template_file = tech_dir / f"perf_template_{i:03d}.yaml"
        with open(template_file, 'w') as f:
            yaml.dump(template_data, f, default_flow_style=False)
    
    return tmp_path


# =============================================================================
# ERROR TESTING FIXTURES
# =============================================================================

@pytest.fixture
def invalid_template_data():
    """Invalid template data for error testing"""
    return {
        'template_id': '',  # Invalid: empty ID
        'name': 'Invalid Template',
        'description': 'Template with validation errors',
        'version': '1.0',
        'industry': 'invalid_industry',  # Invalid: not in enum
        'category': 'test',
        'document_type': 'proposal',
        'company_sizes': ['invalid_size'],  # Invalid: not in enum
        'tone': 'startup_agile',
        'structure': {
            'sections': [
                {
                    'id': 'section1',
                    'title': 'Section 1',
                    'required': True,
                    'order': 0,  # Invalid: order must be >= 1
                    'prompt_template': 'Short'  # Invalid: too short
                }
            ]
        }
    }


@pytest.fixture
def corrupted_yaml_file(tmp_path):
    """Create a corrupted YAML file for error testing"""
    corrupted_file = tmp_path / "corrupted.yaml"
    with open(corrupted_file, 'w') as f:
        f.write("invalid: yaml: content: [[[")  # Invalid YAML syntax
    
    return corrupted_file


# =============================================================================
# INTEGRATION TESTING FIXTURES
# =============================================================================

@pytest.fixture(scope="session")
def real_templates_available():
    """Check if real templates directory is available"""
    templates_path = Path("templates")
    return templates_path.exists() and any(templates_path.rglob("*.yaml"))


@pytest.fixture
def real_template_manager():
    """Real template manager (only if templates exist)"""
    templates_path = Path("templates")
    if not templates_path.exists():
        pytest.skip("Real templates directory not available")
    
    return TemplateManager(templates_path)


# =============================================================================
# CLEANUP HELPERS
# =============================================================================

@pytest.fixture(autouse=True)
def cleanup_temp_files():
    """Auto-cleanup fixture that runs after each test"""
    # Setup: nothing to do
    yield
    
    # Teardown: cleanup any temporary files that might have been missed
    import glob
    import os
    
    # Clean up any test files in current directory
    for pattern in ["test_*.json", "temp_*.yaml", "*.tmp"]:
        for file_path in glob.glob(pattern):
            try:
                os.unlink(file_path)
            except (OSError, PermissionError):
                pass  # Ignore cleanup errors


# =============================================================================
# PYTEST MARKERS CONFIGURATION
# =============================================================================

pytestmark = [
    pytest.mark.filterwarnings("ignore::DeprecationWarning"),
    pytest.mark.filterwarnings("ignore::PendingDeprecationWarning")
]


# =============================================================================
# CUSTOM ASSERTIONS
# =============================================================================

def pytest_assertrepr_compare(op, left, right):
    """Custom assertion representations"""
    if isinstance(left, DocumentTemplate) and isinstance(right, DocumentTemplate) and op == "==":
        return [
            "DocumentTemplate comparison failed:",
            f"   Left template_id: {left.template_id}",
            f"   Right template_id: {right.template_id}",
            f"   Left name: {left.name}",
            f"   Right name: {right.name}",
        ]