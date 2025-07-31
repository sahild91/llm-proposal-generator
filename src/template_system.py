"""
Template System Data Classes
Core data structures for the template system
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
import yaml
from pathlib import Path


class IndustryType(Enum):
    """Supported industry types"""
    TECHNOLOGY = "technology"
    MANUFACTURING = "manufacturing" 
    SERVICES = "services"
    BUSINESS = "business"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    RETAIL = "retail"
    LOGISTICS = "logistics"
    FINANCE = "finance"
    LEGAL = "legal"


class CompanySize(Enum):
    """Company size classifications"""
    STARTUP = "startup"      # 1-10 employees
    SMALL = "small"          # 11-50 employees
    MEDIUM = "medium"        # 51-250 employees
    LARGE = "large"          # 251-1000 employees
    ENTERPRISE = "enterprise" # 1000+ employees


class ToneStyle(Enum):
    """Document tone styles"""
    FORMAL_CORPORATE = "formal_corporate"
    STARTUP_AGILE = "startup_agile"
    GOVERNMENT_COMPLIANCE = "government_compliance"
    ACADEMIC_RESEARCH = "academic_research"
    CONSULTING_PROFESSIONAL = "consulting_professional"


class DocumentType(Enum):
    """Document type classifications"""
    PROPOSAL = "proposal"
    REPORT = "report"
    MANUAL = "manual"
    PLAN = "plan"
    SPECIFICATION = "specification"
    POLICY = "policy"
    AGREEMENT = "agreement"


class ComplexityLevel(Enum):
    """Template complexity levels"""
    LOW = "low"       # 15-30 minutes
    MEDIUM = "medium" # 30-60 minutes
    HIGH = "high"     # 60+ minutes


@dataclass
class TemplateSection:
    """Represents a single section within a template"""
    id: str
    title: str
    required: bool
    order: int
    prompt_template: str
    
    def __post_init__(self):
        """Validate section data after initialization"""
        if not self.id:
            raise ValueError("Section ID cannot be empty")
        if not self.title:
            raise ValueError("Section title cannot be empty")
        if not self.prompt_template:
            raise ValueError("Section prompt_template cannot be empty")
        if self.order < 1:
            raise ValueError("Section order must be >= 1")


@dataclass
class UsageStats:
    """Usage statistics for templates"""
    created_date: str = ""
    last_modified: str = ""
    usage_count: int = 0
    success_rate: float = 0.0


@dataclass
class DocumentTemplate:
    """Main template data structure"""
    # Required fields
    template_id: str
    name: str
    description: str
    version: str
    industry: IndustryType
    category: str
    document_type: DocumentType
    company_sizes: List[CompanySize]
    tone: ToneStyle
    sections: List[TemplateSection]
    
    # Optional fields
    variants: List[str] = field(default_factory=list)
    compliance_requirements: List[str] = field(default_factory=list)
    estimated_time_minutes: int = 30
    complexity_level: ComplexityLevel = ComplexityLevel.MEDIUM
    prerequisites: List[str] = field(default_factory=list)
    usage_stats: UsageStats = field(default_factory=UsageStats)
    
    def __post_init__(self):
        """Validate template data after initialization"""
        if not self.template_id:
            raise ValueError("Template ID cannot be empty")
        if not self.name:
            raise ValueError("Template name cannot be empty")
        if not self.sections:
            raise ValueError("Template must have at least one section")
        
        # Validate section orders are consecutive
        orders = [section.order for section in self.sections]
        orders.sort()
        expected_orders = list(range(1, len(orders) + 1))
        if orders != expected_orders:
            raise ValueError("Section orders must be consecutive starting from 1")
        
        # Validate at least one required section
        if not any(section.required for section in self.sections):
            raise ValueError("Template must have at least one required section")
    
    @classmethod
    def from_yaml_file(cls, file_path: Path) -> 'DocumentTemplate':
        """Create a DocumentTemplate from a YAML file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            return cls.from_dict(data)
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Template file not found: {file_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in template file {file_path}: {e}")
        except Exception as e:
            raise ValueError(f"Error loading template from {file_path}: {e}")
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DocumentTemplate':
        """Create a DocumentTemplate from a dictionary"""
        try:
            # Parse sections
            sections = []
            section_data_list = data.get('structure', {}).get('sections', [])
            
            for section_data in section_data_list:
                section = TemplateSection(
                    id=section_data['id'],
                    title=section_data['title'],
                    required=section_data.get('required', True),
                    order=section_data['order'],
                    prompt_template=section_data['prompt_template']
                )
                sections.append(section)
            
            # Parse usage stats
            usage_data = data.get('usage_stats', {})
            usage_stats = UsageStats(
                created_date=usage_data.get('created_date', ''),
                last_modified=usage_data.get('last_modified', ''),
                usage_count=usage_data.get('usage_count', 0),
                success_rate=usage_data.get('success_rate', 0.0)
            )
            
            # Create template
            template = cls(
                template_id=data['template_id'],
                name=data['name'],
                description=data['description'],
                version=data['version'],
                industry=IndustryType(data['industry']),
                category=data['category'],
                document_type=DocumentType(data['document_type']),
                company_sizes=[CompanySize(size) for size in data['company_sizes']],
                tone=ToneStyle(data['tone']),
                sections=sections,
                variants=data.get('variants', []),
                compliance_requirements=data.get('compliance_requirements', []),
                estimated_time_minutes=data.get('estimated_time_minutes', 30),
                complexity_level=ComplexityLevel(data.get('complexity_level', 'medium')),
                prerequisites=data.get('prerequisites', []),
                usage_stats=usage_stats
            )
            
            return template
            
        except KeyError as e:
            raise ValueError(f"Missing required field in template: {e}")
        except ValueError as e:
            raise ValueError(f"Invalid value in template: {e}")
        except Exception as e:
            raise ValueError(f"Error parsing template data: {e}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert template to dictionary format"""
        return {
            'template_id': self.template_id,
            'name': self.name,
            'description': self.description,
            'version': self.version,
            'industry': self.industry.value,
            'category': self.category,
            'document_type': self.document_type.value,
            'company_sizes': [size.value for size in self.company_sizes],
            'tone': self.tone.value,
            'structure': {
                'sections': [
                    {
                        'id': section.id,
                        'title': section.title,
                        'required': section.required,
                        'order': section.order,
                        'prompt_template': section.prompt_template
                    }
                    for section in sorted(self.sections, key=lambda s: s.order)
                ]
            },
            'variants': self.variants,
            'compliance_requirements': self.compliance_requirements,
            'estimated_time_minutes': self.estimated_time_minutes,
            'complexity_level': self.complexity_level.value,
            'prerequisites': self.prerequisites,
            'usage_stats': {
                'created_date': self.usage_stats.created_date,
                'last_modified': self.usage_stats.last_modified,
                'usage_count': self.usage_stats.usage_count,
                'success_rate': self.usage_stats.success_rate
            }
        }
    
    def get_sections_by_order(self) -> List[TemplateSection]:
        """Get sections sorted by order"""
        return sorted(self.sections, key=lambda s: s.order)
    
    def get_required_sections(self) -> List[TemplateSection]:
        """Get only required sections"""
        return [section for section in self.sections if section.required]
    
    def get_optional_sections(self) -> List[TemplateSection]:
        """Get only optional sections"""
        return [section for section in self.sections if not section.required]
    
    def is_suitable_for_company(self, company_size: CompanySize) -> bool:
        """Check if template is suitable for given company size"""
        return company_size in self.company_sizes
    
    def get_section_by_id(self, section_id: str) -> Optional[TemplateSection]:
        """Get section by ID"""
        for section in self.sections:
            if section.id == section_id:
                return section
        return None


class TemplateValidationError(Exception):
    """Exception raised when template validation fails"""
    pass


def validate_template_file(file_path: Path) -> List[str]:
    """Validate a template file and return list of issues"""
    issues = []
    
    try:
        template = DocumentTemplate.from_yaml_file(file_path)
        
        # Additional validation checks
        section_ids = [section.id for section in template.sections]
        if len(section_ids) != len(set(section_ids)):
            issues.append("Duplicate section IDs found")
        
        # Check for reasonable section count
        if len(template.sections) > 20:
            issues.append("Template has unusually high number of sections (>20)")
        
        # Check prompt template length
        for section in template.sections:
            if len(section.prompt_template.strip()) < 20:
                issues.append(f"Section '{section.id}' has very short prompt template")
        
    except Exception as e:
        issues.append(str(e))
    
    return issues


# Template loading utilities
def load_template_from_file(file_path: Path) -> DocumentTemplate:
    """Load and validate a template from file"""
    issues = validate_template_file(file_path)
    if issues:
        raise TemplateValidationError(f"Template validation failed for {file_path}: {'; '.join(issues)}")
    
    return DocumentTemplate.from_yaml_file(file_path)

# Quick test (remove after testing)
# if __name__ == "__main__":
#     from pathlib import Path
    
#     template_file = Path("templates/technology/software_development/project_proposal.yaml")
#     try:
#         template = DocumentTemplate.from_yaml_file(template_file)
#         print(f"✅ Successfully loaded template: {template.name}")
#         print(f"✅ Sections: {len(template.sections)}")
#         print(f"✅ Industry: {template.industry.value}")
#         print(f"✅ Template ID: {template.template_id}")
#     except Exception as e:
#         print(f"❌ Error: {e}")