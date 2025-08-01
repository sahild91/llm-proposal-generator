"""
TASK-008/009: Universal LLM Client - Optimized Version
Extends existing LLMClient for template-based document generation
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from llm_client import LLMClient
from template_system import DocumentTemplate, TemplateSection


class UniversalLLMClient(LLMClient):
    """Universal LLM Client for template-based document generation"""
    
    def __init__(self, config: Dict[str, Any], company_config: Dict[str, Any] = None, template_manager=None):
        super().__init__(config, company_config)
        self.template_manager = template_manager
    
    # =============================================================================
    # CORE GENERATION METHODS
    # =============================================================================
    
    def generate_from_template(self, template_id: str, project_data: Dict[str, Any], 
                             selected_sections: Optional[List[str]] = None,
                             generation_options: Optional[Dict[str, Any]] = None) -> str:
        """Generate document using specific template"""
        template = self._get_template(template_id)
        sections = self._determine_sections(template, selected_sections)
        prompt = self._create_universal_prompt(template, project_data, sections, generation_options)
        content = self.provider.generate_completion(prompt)
        return self._post_process_content(content, template, project_data)
    
    def generate_document_by_type(self, document_type: str, industry: str, 
                                project_data: Dict[str, Any], **filters) -> str:
        """Auto-select best template and generate document"""
        template = self._find_best_template(document_type, industry, **filters)
        return self.generate_from_template(template.template_id, project_data)
    
    def generate_section_by_section(self, template_id: str, project_data: Dict[str, Any],
                                   progress_callback: Optional[callable] = None) -> Dict[str, str]:
        """Generate document section by section with progress tracking"""
        template = self._get_template(template_id)
        sections = template.get_required_sections()
        section_content = {}
        
        for i, section in enumerate(sections):
            if progress_callback:
                progress_callback(f"Generating: {section.title}", i, len(sections))
            
            prompt = self._create_section_prompt(template, section, project_data)
            section_content[section.id] = self.provider.generate_completion(prompt)
        
        return section_content
    
    # =============================================================================
    # TEMPLATE ANALYSIS & PREVIEW
    # =============================================================================
    
    def get_template_preview(self, template_id: str) -> Dict[str, Any]:
        """Get template preview information"""
        template = self._get_template(template_id)
        return {
            'template_id': template.template_id,
            'name': template.name,
            'description': template.description,
            'industry': template.industry.value,
            'document_type': template.document_type.value,
            'estimated_time_minutes': template.estimated_time_minutes,
            'complexity_level': template.complexity_level.value,
            'sections': [
                {
                    'id': s.id, 'title': s.title, 'required': s.required, 'order': s.order,
                    'description': s.prompt_template[:100] + "..." if len(s.prompt_template) > 100 else s.prompt_template
                }
                for s in template.get_sections_by_order()
            ],
            'prerequisites': template.prerequisites,
            'compliance_requirements': template.compliance_requirements
        }
    
    def validate_template_compatibility(self, template_id: str, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate template compatibility with project"""
        template = self._get_template(template_id)
        score, issues = self._calculate_compatibility(template, project_data)
        
        return {
            'compatible': score >= 50,
            'score': max(0, score),
            'issues': issues,
            'template_name': template.name,
            'recommendations': self._generate_recommendations(issues, template, project_data)
        }
    
    def get_generation_estimate(self, template_id: str, include_sections: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get generation time and complexity estimates"""
        template = self._get_template(template_id)
        sections = self._determine_sections(template, include_sections)
        
        time_per_section = {'low': 30, 'medium': 60, 'high': 120}
        section_time = time_per_section[template.complexity_level.value]
        total_time = len(sections) * section_time
        
        return {
            'template_name': template.name,
            'complexity_level': template.complexity_level.value,
            'sections_to_generate': len(sections),
            'estimated_generation_time_seconds': total_time,
            'estimated_generation_time_formatted': f"{total_time // 60}m {total_time % 60}s",
            'estimated_tokens': len(sections) * 500
        }
    
    # =============================================================================
    # PROMPT GENERATION
    # =============================================================================
    
    def _create_universal_prompt(self, template: DocumentTemplate, project_data: Dict[str, Any],
                               sections: List[TemplateSection], options: Optional[Dict[str, Any]] = None) -> str:
        """Create comprehensive prompt for document generation"""
        options = options or {}
        
        # Build prompt components
        company_context = self._get_company_context()
        industry_context = self._get_industry_context(template.industry.value)
        tone_guidance = self._get_tone_guidance(template.tone.value, options.get('tone_override'))
        project_context = self._build_project_context(project_data)
        section_prompts = self._build_section_prompts(sections, project_data, template)
        
        return f"""
{company_context}

{industry_context}

{tone_guidance}

{project_context}

Generate a professional {template.document_type.value} document:

{section_prompts}

GUIDELINES:
- Use markdown formatting for structure
- Make content specific to {project_data.get('project_name', 'the project')}
- Target audience: {template.company_sizes[0].value.title()} company in {template.industry.value}
- Follow {template.tone.value} communication style
- Include specific details, not generic placeholders
""".strip()
    
    def _create_section_prompt(self, template: DocumentTemplate, section: TemplateSection, project_data: Dict[str, Any]) -> str:
        """Create prompt for single section generation"""
        return f"""
{self._get_company_context()}
{self._get_industry_context(template.industry.value)}
{self._get_tone_guidance(template.tone.value)}

Generate ONLY this section for a {template.document_type.value}:

## {section.title}
{section.prompt_template}

Make content specific to: {project_data.get('project_name', 'the project')}
Use markdown formatting and professional language.
"""
    
    # =============================================================================
    # HELPER METHODS
    # =============================================================================
    
    def _get_template(self, template_id: str) -> DocumentTemplate:
        """Get template with error handling"""
        if not self.template_manager:
            raise ValueError("Template manager not provided")
        template = self.template_manager.get_template(template_id)
        if not template:
            raise ValueError(f"Template not found: {template_id}")
        return template
    
    def _find_best_template(self, document_type: str, industry: str, **filters) -> DocumentTemplate:
        """Find best matching template"""
        search_filters = {'document_type': document_type, 'industry': industry, **filters}
        templates = self.template_manager.get_available_templates(search_filters)
        
        if not templates:
            # Fallback to document type only
            templates = self.template_manager.get_available_templates({'document_type': document_type})
        
        if not templates:
            raise ValueError(f"No suitable template found for {document_type} in {industry}")
        
        return templates[0]  # Return first match (could be enhanced with scoring)
    
    def _determine_sections(self, template: DocumentTemplate, selected_sections: Optional[List[str]] = None) -> List[TemplateSection]:
        """Determine which sections to generate"""
        if selected_sections:
            sections = [template.get_section_by_id(sid) for sid in selected_sections if template.get_section_by_id(sid)]
            return sorted(sections, key=lambda s: s.order)
        return template.get_required_sections()
    
    def _calculate_compatibility(self, template: DocumentTemplate, project_data: Dict[str, Any]) -> tuple[int, List[str]]:
        """Calculate compatibility score and issues"""
        score = 100
        issues = []
        
        # Industry check
        project_industry = project_data.get('industry', '').lower()
        if project_industry and project_industry != template.industry.value:
            issues.append(f"Industry mismatch: template is for {template.industry.value}, project is {project_industry}")
            score -= 30
        
        # Company size check
        company_size = project_data.get('company_size', '').lower()
        if company_size:
            try:
                from template_system import CompanySize
                size_enum = CompanySize(company_size)
                if size_enum not in template.company_sizes:
                    issues.append(f"Company size mismatch")
                    score -= 20
            except ValueError:
                issues.append(f"Invalid company size: {company_size}")
                score -= 10
        
        # Required fields check
        required_fields = ['project_name', 'client_name']
        missing = [f for f in required_fields if not project_data.get(f)]
        if missing:
            issues.append(f"Missing fields: {', '.join(missing)}")
            score -= len(missing) * 10
        
        return score, issues
    
    def _generate_recommendations(self, issues: List[str], template: DocumentTemplate, project_data: Dict[str, Any]) -> List[str]:
        """Generate compatibility recommendations"""
        recommendations = []
        for issue in issues:
            if "Industry mismatch" in issue:
                recommendations.append(f"Consider templates from {project_data.get('industry', 'your')} industry")
            elif "size mismatch" in issue:
                recommendations.append("Look for templates supporting your company size")
            elif "Missing fields" in issue:
                recommendations.append("Provide complete project information")
        return recommendations or ["Template appears suitable for your project"]
    
    def _build_project_context(self, project_data: Dict[str, Any]) -> str:
        """Build project context for prompts"""
        context_parts = []
        key_fields = ['project_name', 'client_name', 'project_type', 'expected_duration', 'requirements']
        
        for field in key_fields:
            if project_data.get(field):
                context_parts.append(f"{field.replace('_', ' ').title()}: {project_data[field]}")
        
        return "PROJECT CONTEXT:\n" + "\n".join(context_parts) if context_parts else "PROJECT CONTEXT: General business project"
    
    def _build_section_prompts(self, sections: List[TemplateSection], project_data: Dict[str, Any], template: DocumentTemplate) -> str:
        """Build section-specific prompts"""
        prompts = []
        for section in sorted(sections, key=lambda s: s.order):
            prompts.append(f"""
## {section.title}
{section.prompt_template}
- Make specific to: {project_data.get('project_name', 'the project')}
- Follow {template.industry.value} industry standards
""")
        return "\n".join(prompts)
    
    def _post_process_content(self, content: str, template: DocumentTemplate, project_data: Dict[str, Any]) -> str:
        """Post-process generated content"""
        if not content.startswith('#'):
            title = project_data.get('project_name', f"{template.document_type.value.title()} Document")
            content = f"# {title}\n\n{content}"
        
        # Add metadata comment
        metadata = f"""<!-- Generated using {template.name} on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -->\n\n"""
        return metadata + content
    
    # =============================================================================
    # CONTEXT GENERATION (Industry & Tone)
    # =============================================================================
    
    def _get_industry_context(self, industry: str) -> str:
        """Get industry-specific context"""
        contexts = {
            'technology': "Focus on innovation, scalability, technical feasibility, and digital transformation.",
            'manufacturing': "Focus on production efficiency, quality control, supply chain optimization, and regulatory compliance.",
            'healthcare': "Focus on patient care, regulatory compliance, data privacy, and clinical excellence.",
            'education': "Focus on learning outcomes, curriculum development, student engagement, and educational standards.",
            'services': "Focus on client satisfaction, service delivery excellence, and professional expertise.",
            'retail': "Focus on customer experience, inventory management, sales optimization, and market trends.",
            'logistics': "Focus on supply chain optimization, transportation efficiency, and safety compliance.",
            'finance': "Focus on regulatory compliance, risk management, financial analysis, and fiduciary responsibility."
        }
        return f"INDUSTRY CONTEXT: {contexts.get(industry, 'Professional business standards and best practices.')}"
    
    def _get_tone_guidance(self, tone: str, override: Optional[str] = None) -> str:
        """Get tone guidance for document generation"""
        active_tone = override or tone
        
        guidance = {
            'formal_corporate': "Use professional, detailed language with comprehensive coverage and executive-level communication.",
            'startup_agile': "Use direct, energetic language focused on innovation, rapid execution, and competitive advantages.",
            'government_compliance': "Use formal, precise language with emphasis on compliance, documentation, and regulatory requirements.",
            'academic_research': "Use scholarly, analytical language with emphasis on methodology, evidence, and research-backed recommendations.",
            'consulting_professional': "Use expert, advisory language focused on strategic value, actionable insights, and business outcomes."
        }
        
        return f"TONE GUIDANCE: {guidance.get(active_tone, 'Use clear, professional business language.')}"