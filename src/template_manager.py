import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
import logging
from datetime import datetime

from template_system import (
    DocumentTemplate, IndustryType, CompanySize, ToneStyle, 
    DocumentType, ComplexityLevel, TemplateValidationError,
    load_template_from_file
)


class TemplateManager:
    """Manages template discovery, loading, and caching for desktop application"""
    
    def __init__(self, templates_dir: Path):
        """Initialize the template manager"""
        self.templates_dir = Path(templates_dir)
        self.templates_cache: Dict[str, DocumentTemplate] = {}
        self.load_errors: List[str] = []
        self.relationship_errors: List[str] = []
        
        # File tracking for change detection
        self.file_mtimes: Dict[str, float] = {}
        self.file_hashes: Dict[str, str] = {}
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Initialize all indexes
        self._init_indexes()
        
        # Load templates
        self._load_all_templates()
    
    def _init_indexes(self) -> None:
        """Initialize all template indexes"""
        self.industry_index: Dict[str, List[DocumentTemplate]] = {}
        self.category_index: Dict[str, List[DocumentTemplate]] = {}
        self.document_type_index: Dict[str, List[DocumentTemplate]] = {}
        self.tone_index: Dict[str, List[DocumentTemplate]] = {}
        self.complexity_index: Dict[str, List[DocumentTemplate]] = {}
        self.company_size_index: Dict[str, List[DocumentTemplate]] = {}
    
    # =============================================================================
    # TEMPLATE LOADING & DISCOVERY
    # =============================================================================
    
    def _load_all_templates(self) -> None:
        """Load all templates with enhanced discovery"""
        self.logger.info(f"Loading templates from: {self.templates_dir}")
        
        if not self.templates_dir.exists():
            self.logger.warning(f"Templates directory does not exist: {self.templates_dir}")
            return
        
        # Clear all data
        self._clear_all_data()
        
        # Find and load templates
        template_files = list(self.templates_dir.rglob("*.yaml"))
        self.logger.info(f"Found {len(template_files)} template files")
        
        for template_file in template_files:
            self._load_template_file(template_file)
        
        # Validate and log results
        self._validate_template_relationships()
        self._log_results()
    
    def _clear_all_data(self) -> None:
        """Clear all cached data"""
        self.templates_cache.clear()
        self.load_errors.clear()
        self.relationship_errors.clear()
        self.file_mtimes.clear()
        self.file_hashes.clear()
        
        for index in [self.industry_index, self.category_index, self.document_type_index,
                     self.tone_index, self.complexity_index, self.company_size_index]:
            index.clear()
    
    def _load_template_file(self, file_path: Path) -> None:
        """Load and index a single template file"""
        try:
            if self._should_skip_file(file_path):
                return
            
            # Track file metadata
            self._track_file_metadata(file_path)
            
            # Load template
            template = load_template_from_file(file_path)
            
            # Check for duplicates
            if template.template_id in self.templates_cache:
                self.load_errors.append(f"Duplicate template ID '{template.template_id}' in {file_path}")
                return
            
            # Add to cache and indexes
            self.templates_cache[template.template_id] = template
            self._add_to_all_indexes(template)
            
            self.logger.debug(f"Loaded template: {template.template_id}")
            
        except Exception as e:
            error_msg = f"Error loading {file_path}: {str(e)}"
            self.load_errors.append(error_msg)
            self.logger.error(error_msg)
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped"""
        skip_patterns = ['TEMPLATE_SCHEMA', 'README', '.example', '.template', 'test_', '_test']
        filename = file_path.name.upper()
        return any(pattern.upper() in filename for pattern in skip_patterns)
    
    def _track_file_metadata(self, file_path: Path) -> None:
        """Track file metadata for change detection"""
        stat = file_path.stat()
        self.file_mtimes[str(file_path)] = stat.st_mtime
        
        with open(file_path, 'rb') as f:
            self.file_hashes[str(file_path)] = hashlib.md5(f.read()).hexdigest()
    
    def _add_to_all_indexes(self, template: DocumentTemplate) -> None:
        """Add template to all relevant indexes"""
        # Industry index
        self._add_to_index(self.industry_index, template.industry.value, template)
        
        # Category index
        category_key = f"{template.industry.value}:{template.category}"
        self._add_to_index(self.category_index, category_key, template)
        
        # Document type index
        self._add_to_index(self.document_type_index, template.document_type.value, template)
        
        # Tone index
        self._add_to_index(self.tone_index, template.tone.value, template)
        
        # Complexity index
        self._add_to_index(self.complexity_index, template.complexity_level.value, template)
        
        # Company size index
        for size in template.company_sizes:
            self._add_to_index(self.company_size_index, size.value, template)
    
    def _add_to_index(self, index: Dict[str, List[DocumentTemplate]], key: str, template: DocumentTemplate) -> None:
        """Helper to add template to an index"""
        if key not in index:
            index[key] = []
        index[key].append(template)
    
    # =============================================================================
    # TEMPLATE RETRIEVAL
    # =============================================================================
    
    def get_template(self, template_id: str) -> Optional[DocumentTemplate]:
        """Get template by ID"""
        return self.templates_cache.get(template_id)
    
    def get_all_templates(self) -> List[DocumentTemplate]:
        """Get all templates"""
        return list(self.templates_cache.values())
    
    def get_templates_by_industry(self, industry: str) -> List[DocumentTemplate]:
        """Get templates by industry"""
        return self.industry_index.get(industry, [])
    
    def get_templates_by_category(self, industry: str, category: str) -> List[DocumentTemplate]:
        """Get templates by industry and category"""
        return self.category_index.get(f"{industry}:{category}", [])
    
    def get_templates_by_document_type(self, document_type: str) -> List[DocumentTemplate]:
        """Get templates by document type"""
        return self.document_type_index.get(document_type, [])
    
    def get_templates_by_tone(self, tone: str) -> List[DocumentTemplate]:
        """Get templates by tone"""
        return self.tone_index.get(tone, [])
    
    def get_templates_by_complexity(self, complexity: str) -> List[DocumentTemplate]:
        """Get templates by complexity"""
        return self.complexity_index.get(complexity, [])
    
    def get_templates_by_company_size(self, company_size: str) -> List[DocumentTemplate]:
        """Get templates by company size"""
        return self.company_size_index.get(company_size, [])
    
    # =============================================================================
    # METADATA & DISCOVERY
    # =============================================================================
    
    def get_available_industries(self) -> List[str]:
        """Get all available industries"""
        return sorted(self.industry_index.keys())
    
    def get_categories_for_industry(self, industry: str) -> List[str]:
        """Get categories for industry"""
        categories = {t.category for t in self.get_templates_by_industry(industry)}
        return sorted(categories)
    
    def get_all_document_types(self) -> List[str]:
        """Get all document types"""
        return sorted(self.document_type_index.keys())
    
    def get_all_tones(self) -> List[str]:
        """Get all tones"""
        return sorted(self.tone_index.keys())
    
    def get_all_complexity_levels(self) -> List[str]:
        """Get all complexity levels"""
        return sorted(self.complexity_index.keys())
    
    def get_all_company_sizes(self) -> List[str]:
        """Get all company sizes"""
        return sorted(self.company_size_index.keys())
    
    # =============================================================================
    # SEARCH & RECOMMENDATIONS
    # =============================================================================
    
    def search_templates(self, **filters) -> List[DocumentTemplate]:
        """Search templates with multiple filters"""
        results = list(self.templates_cache.values())
        
        # Apply each filter
        filter_map = {
            'industry': lambda t, v: t.industry.value == v,
            'category': lambda t, v: t.category == v,
            'document_type': lambda t, v: t.document_type.value == v,
            'tone': lambda t, v: t.tone.value == v,
            'complexity': lambda t, v: t.complexity_level.value == v,
            'company_size': lambda t, v: CompanySize(v) in t.company_sizes,
            'search_text': lambda t, v: v.lower() in t.name.lower() or v.lower() in t.description.lower()
        }
        
        for key, value in filters.items():
            if value and key in filter_map:
                results = [t for t in results if filter_map[key](t, value)]
        
        return results
    
    def get_recommended_templates(self, company_profile: Dict[str, str], 
                                project_context: Optional[Dict[str, str]] = None) -> List[DocumentTemplate]:
        """Get recommended templates"""
        scored_templates = []
        
        for template in self.templates_cache.values():
            score = self._calculate_recommendation_score(template, company_profile, project_context)
            if score > 0:
                scored_templates.append((template, score))
        
        scored_templates.sort(key=lambda x: x[1], reverse=True)
        return [template for template, score in scored_templates[:10]]
    
    def _calculate_recommendation_score(self, template: DocumentTemplate, 
                                      company_profile: Dict[str, str],
                                      project_context: Optional[Dict[str, str]] = None) -> float:
        """Calculate recommendation score"""
        score = 0.0
        
        # Industry match (highest priority)
        if template.industry.value == company_profile.get('industry'):
            score += 3.0
        
        # Company size match
        if company_profile.get('size'):
            try:
                size_enum = CompanySize(company_profile['size'])
                if size_enum in template.company_sizes:
                    score += 2.0
            except ValueError:
                pass
        
        # Tone match
        if template.tone.value == company_profile.get('tone'):
            score += 1.5
        
        # Usage stats boost
        if template.usage_stats.usage_count > 0:
            score += min(template.usage_stats.usage_count * 0.1, 1.0)
        
        return score
    
    # =============================================================================
    # ADVANCED FEATURES
    # =============================================================================
    
    def find_similar_templates(self, template_id: str, limit: int = 5) -> List[Tuple[DocumentTemplate, float]]:
        """Find similar templates"""
        reference = self.get_template(template_id)
        if not reference:
            return []
        
        similar = []
        for other_id, other in self.templates_cache.items():
            if other_id == template_id:
                continue
                
            similarity = self._calculate_similarity(reference, other)
            if similarity > 0.3:
                similar.append((other, similarity))
        
        similar.sort(key=lambda x: x[1], reverse=True)
        return similar[:limit]
    
    def _calculate_similarity(self, t1: DocumentTemplate, t2: DocumentTemplate) -> float:
        """Calculate similarity between templates"""
        score = 0.0
        if t1.industry == t2.industry: score += 0.3
        if t1.document_type == t2.document_type: score += 0.3
        if t1.tone == t2.tone: score += 0.2
        if set(t1.company_sizes) & set(t2.company_sizes): score += 0.2
        return min(score, 1.0)
    
    def get_template_family(self, template_id: str) -> List[DocumentTemplate]:
        """Get template and its variants"""
        base = self.get_template(template_id)
        if not base:
            return []
        
        family = [base]
        for variant_id in base.variants:
            variant = self.get_template(variant_id)
            if variant:
                family.append(variant)
        
        return family
    
    # =============================================================================
    # VALIDATION & MAINTENANCE
    # =============================================================================
    
    def _validate_template_relationships(self) -> None:
        """Validate template relationships"""
        self.relationship_errors.clear()
        
        for template_id, template in self.templates_cache.items():
            for variant_id in template.variants:
                if variant_id not in self.templates_cache:
                    self.relationship_errors.append(
                        f"Template '{template_id}' references non-existent variant '{variant_id}'"
                    )
    
    def check_for_template_changes(self) -> List[str]:
        """Check for changed template files"""
        if not hasattr(self, 'file_mtimes'):
            return []
        
        changed = []
        for file_path_str, last_mtime in self.file_mtimes.items():
            file_path = Path(file_path_str)
            
            if not file_path.exists():
                changed.append(f"DELETED: {file_path.name}")
                continue
            
            if file_path.stat().st_mtime > last_mtime:
                try:
                    template = load_template_from_file(file_path)
                    changed.append(template.template_id)
                except:
                    changed.append(f"MODIFIED: {file_path.name}")
        
        return changed
    
    def reload_templates(self) -> None:
        """Reload all templates"""
        self.logger.info("Reloading templates from disk")
        self._load_all_templates()
    
    # =============================================================================
    # STATISTICS & REPORTING
    # =============================================================================
    
    def get_template_statistics(self) -> Dict[str, any]:
        """Get template statistics"""
        if not self.templates_cache:
            return {
                'total_templates': 0,
                'by_industry': {},
                'by_document_type': {},
                'by_complexity': {},
                'load_errors': len(self.load_errors)
            }
        
        return {
            'total_templates': len(self.templates_cache),
            'by_industry': {k: len(v) for k, v in self.industry_index.items()},
            'by_document_type': {k: len(v) for k, v in self.document_type_index.items()},
            'by_complexity': {k: len(v) for k, v in self.complexity_index.items()},
            'load_errors': len(self.load_errors)
        }
    
    def get_discovery_health_report(self) -> Dict[str, any]:
        """Get system health report"""
        total_files = len(list(self.templates_dir.rglob("*.yaml"))) if self.templates_dir.exists() else 0
        
        return {
            'timestamp': datetime.now().isoformat(),
            'templates_directory': str(self.templates_dir),
            'directory_exists': self.templates_dir.exists(),
            'total_yaml_files': total_files,
            'successfully_loaded': len(self.templates_cache),
            'load_errors': len(self.load_errors),
            'relationship_errors': len(self.relationship_errors),
            'success_rate': len(self.templates_cache) / max(total_files, 1),
            'indexes_built': {
                'industry': len(self.industry_index),
                'category': len(self.category_index),
                'document_type': len(self.document_type_index),
                'tone': len(self.tone_index),
                'complexity': len(self.complexity_index),
                'company_size': len(self.company_size_index)
            }
        }
    
    def export_template_catalog(self, output_path: Path) -> None:
        """Export template catalog to JSON"""
        catalog = {
            'generated_at': datetime.now().isoformat(),
            'total_templates': len(self.templates_cache),
            'statistics': self.get_template_statistics(),
            'templates': [
                {
                    'template_id': t.template_id,
                    'name': t.name,
                    'description': t.description,
                    'industry': t.industry.value,
                    'category': t.category,
                    'document_type': t.document_type.value,
                    'company_sizes': [s.value for s in t.company_sizes],
                    'tone': t.tone.value,
                    'complexity': t.complexity_level.value,
                    'estimated_time': t.estimated_time_minutes,
                    'section_count': len(t.sections)
                }
                for t in self.templates_cache.values()
            ]
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(catalog, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Template catalog exported to: {output_path}")
    
    def _log_results(self) -> None:
        """Log loading results"""
        total = len(self.templates_cache)
        self.logger.info(f"Template loading completed:")
        self.logger.info(f"  - Total loaded: {total}")
        self.logger.info(f"  - Industries: {len(self.industry_index)}")
        self.logger.info(f"  - Document types: {len(self.document_type_index)}")
        
        if self.load_errors:
            self.logger.warning(f"  - Load errors: {len(self.load_errors)}")
        if self.relationship_errors:
            self.logger.warning(f"  - Relationship errors: {len(self.relationship_errors)}")
    
    # =============================================================================
    # UTILITY METHODS
    # =============================================================================
    
    def get_load_errors(self) -> List[str]:
        """Get load errors"""
        return self.load_errors.copy()
    
    def __len__(self) -> int:
        """Return number of templates"""
        return len(self.templates_cache)
    
    def __contains__(self, template_id: str) -> bool:
        """Check if template exists"""
        return template_id in self.templates_cache

    def get_available_templates(self, filters: Optional[Dict[str, Any]] = None) -> List[DocumentTemplate]:
        """
        Get available templates with optional filtering
        
        Args:
            filters: Optional dictionary with filter criteria:
                - industry: str - Filter by industry
                - category: str - Filter by category  
                - document_type: str - Filter by document type
                - company_size: str - Filter by company size
                - tone: str - Filter by tone
                - complexity: str - Filter by complexity level
        
        Returns:
            List of DocumentTemplate objects matching filters
        """
        if not filters:
            return list(self.templates_cache.values())
        
        results = list(self.templates_cache.values())
        
        # Apply industry filter
        if filters.get('industry'):
            results = [t for t in results if t.industry.value == filters['industry']]
        
        # Apply category filter
        if filters.get('category'):
            results = [t for t in results if t.category == filters['category']]
        
        # Apply document type filter
        if filters.get('document_type'):
            results = [t for t in results if t.document_type.value == filters['document_type']]
        
        # Apply company size filter
        if filters.get('company_size'):
            try:
                size_enum = CompanySize(filters['company_size'])
                results = [t for t in results if size_enum in t.company_sizes]
            except ValueError:
                # Invalid company size, return empty results
                return []
        
        # Apply tone filter
        if filters.get('tone'):
            results = [t for t in results if t.tone.value == filters['tone']]
        
        # Apply complexity filter
        if filters.get('complexity'):
            results = [t for t in results if t.complexity_level.value == filters['complexity']]
        
        return results

    def get_template(self, template_id: str) -> Optional[DocumentTemplate]:
        """
        Get a specific template by ID
        
        Args:
            template_id: The unique identifier for the template
            
        Returns:
            DocumentTemplate if found, None otherwise
        """
        return self.templates_cache.get(template_id)

    def get_templates_by_filter(self, filter_type: str, filter_value: str) -> List[DocumentTemplate]:
        """
        Get templates by a specific filter type and value
        
        Args:
            filter_type: Type of filter ('industry', 'category', 'document_type', etc.)
            filter_value: Value to filter by
            
        Returns:
            List of matching templates
        """
        filter_map = {
            'industry': self.get_templates_by_industry,
            'document_type': self.get_templates_by_document_type,
            'tone': self.get_templates_by_tone,
            'complexity': self.get_templates_by_complexity,
            'company_size': self.get_templates_by_company_size
        }
        
        if filter_type == 'category':
            # Category requires industry context, so we need to search differently
            return [t for t in self.templates_cache.values() if t.category == filter_value]
        
        filter_func = filter_map.get(filter_type)
        if filter_func:
            return filter_func(filter_value)
        else:
            return []

    def get_template_metadata(self, template_id: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a specific template without loading full content
        
        Args:
            template_id: The template identifier
            
        Returns:
            Dictionary with template metadata or None if not found
        """
        template = self.get_template(template_id)
        if not template:
            return None
        
        return {
            'template_id': template.template_id,
            'name': template.name,
            'description': template.description,
            'industry': template.industry.value,
            'category': template.category,
            'document_type': template.document_type.value,
            'company_sizes': [size.value for size in template.company_sizes],
            'tone': template.tone.value,
            'complexity_level': template.complexity_level.value,
            'estimated_time_minutes': template.estimated_time_minutes,
            'section_count': len(template.sections),
            'required_sections': len([s for s in template.sections if s.required]),
            'optional_sections': len([s for s in template.sections if not s.required]),
            'prerequisites': template.prerequisites,
            'compliance_requirements': template.compliance_requirements,
            'variants': template.variants
        }

    def get_templates_by_criteria(self, **criteria) -> List[DocumentTemplate]:
        """
        Advanced template filtering with multiple criteria
        
        Args:
            **criteria: Keyword arguments for filtering:
                - industries: List[str] - Multiple industries
                - document_types: List[str] - Multiple document types  
                - company_sizes: List[str] - Multiple company sizes
                - max_complexity: str - Maximum complexity level
                - max_time_minutes: int - Maximum estimated time
                - has_variants: bool - Templates with variants
                - required_sections_only: bool - Only required sections
        
        Returns:
            List of templates matching all criteria
        """
        results = list(self.templates_cache.values())
        
        # Filter by multiple industries
        if criteria.get('industries'):
            industries = criteria['industries']
            results = [t for t in results if t.industry.value in industries]
        
        # Filter by multiple document types
        if criteria.get('document_types'):
            doc_types = criteria['document_types']
            results = [t for t in results if t.document_type.value in doc_types]
        
        # Filter by multiple company sizes
        if criteria.get('company_sizes'):
            company_sizes = criteria['company_sizes']
            try:
                size_enums = [CompanySize(size) for size in company_sizes]
                results = [t for t in results if any(size in t.company_sizes for size in size_enums)]
            except ValueError:
                return []
        
        # Filter by maximum complexity
        if criteria.get('max_complexity'):
            complexity_order = {'low': 1, 'medium': 2, 'high': 3}
            max_level = complexity_order.get(criteria['max_complexity'], 3)
            results = [t for t in results if complexity_order.get(t.complexity_level.value, 3) <= max_level]
        
        # Filter by maximum time
        if criteria.get('max_time_minutes'):
            max_time = criteria['max_time_minutes']
            results = [t for t in results if t.estimated_time_minutes <= max_time]
        
        # Filter by templates with variants
        if criteria.get('has_variants'):
            if criteria['has_variants']:
                results = [t for t in results if t.variants]
            else:
                results = [t for t in results if not t.variants]
        
        # Filter by templates with only required sections
        if criteria.get('required_sections_only'):
            if criteria['required_sections_only']:
                results = [t for t in results if all(s.required for s in t.sections)]
        
        return results

    def get_template_suggestions(self, partial_name: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get template suggestions based on partial name matching
        
        Args:
            partial_name: Partial template name to search for
            limit: Maximum number of suggestions to return
            
        Returns:
            List of template suggestions with relevance scores
        """
        suggestions = []
        partial_lower = partial_name.lower()
        
        for template in self.templates_cache.values():
            name_lower = template.name.lower()
            desc_lower = template.description.lower()
            
            # Calculate relevance score
            score = 0
            if partial_lower in name_lower:
                score += 10  # Higher score for name matches
                if name_lower.startswith(partial_lower):
                    score += 5  # Even higher for prefix matches
            
            if partial_lower in desc_lower:
                score += 3  # Lower score for description matches
            
            if score > 0:
                suggestions.append({
                    'template': template,
                    'score': score,
                    'match_type': 'name' if partial_lower in name_lower else 'description'
                })
        
        # Sort by score (descending) and limit results
        suggestions.sort(key=lambda x: x['score'], reverse=True)
        return suggestions[:limit]

    def template_exists(self, template_id: str) -> bool:
        """
        Check if a template exists
        
        Args:
            template_id: The template identifier to check
            
        Returns:
            True if template exists, False otherwise
        """
        return template_id in self.templates_cache

    def get_template_count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Get count of templates matching optional filters
        
        Args:
            filters: Optional filter criteria (same as get_available_templates)
            
        Returns:
            Number of templates matching filters
        """
        return len(self.get_available_templates(filters))

    def get_filter_options(self) -> Dict[str, List[str]]:
        """
        Get all available filter options
        
        Returns:
            Dictionary with all possible filter values for each filter type
        """
        return {
            'industries': self.get_available_industries(),
            'document_types': self.get_all_document_types(),
            'tones': self.get_all_tones(),
            'complexity_levels': self.get_all_complexity_levels(),
            'company_sizes': self.get_all_company_sizes(),
            'categories': self._get_all_categories()
        }

    def _get_all_categories(self) -> List[str]:
        """Get all unique categories across all templates"""
        categories = set()
        for template in self.templates_cache.values():
            categories.add(template.category)
        return sorted(list(categories))

    # Enhanced __contains__ method for better template checking
    def __contains__(self, template_id: str) -> bool:
        """
        Check if template exists using 'in' operator
        
        Args:
            template_id: Template ID to check
            
        Returns:
            True if template exists
        """
        return template_id in self.templates_cache