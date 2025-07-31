import hashlib
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
import logging
from datetime import datetime

from .template_system import (
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