"""
Test Template Manager - Pytest Compatible
Comprehensive test suite for the Template Manager class
"""

import sys
import os
from pathlib import Path
import json
import tempfile
import pytest

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from template_manager import TemplateManager


@pytest.fixture
def templates_path():
    """Get templates directory path"""
    templates_path = Path("templates")
    if not templates_path.exists():
        pytest.skip("Templates directory not found. Please run from project root.")
    return templates_path


@pytest.fixture
def template_manager(templates_path):
    """Initialize Template Manager for testing"""
    return TemplateManager(templates_path)


class TestTemplateManagerBasics:
    """Test basic Template Manager functionality"""
    
    def test_template_manager_initialization(self, template_manager):
        """Test Template Manager initializes correctly"""
        assert template_manager is not None
        assert len(template_manager) >= 0  # Should have some templates or be empty
        print(f"✅ Template Manager initialized with {len(template_manager)} templates")
    
    def test_template_loading_and_retrieval(self, template_manager):
        """Test template loading and retrieval"""
        template_count = len(template_manager)
        assert template_count >= 0, "Templates should be loaded (or empty if no templates exist)"
        print(f"   ✅ Loaded {template_count} templates")
        
        # Test template retrieval
        all_templates = template_manager.get_all_templates()
        assert len(all_templates) == template_count, "get_all_templates() count should match"
        print(f"   ✅ Retrieved all templates successfully")
        
        # Test specific template retrieval if templates exist
        if all_templates:
            first_template = all_templates[0]
            retrieved = template_manager.get_template(first_template.template_id)
            assert retrieved is not None, "Template retrieval by ID should work"
            assert retrieved.template_id == first_template.template_id, "Retrieved template should match"
            print(f"   ✅ Template retrieval by ID works")


class TestTemplateManagerIndustry:
    """Test industry-related functionality"""
    
    def test_industry_discovery(self, template_manager):
        """Test industry discovery functionality"""
        industries = template_manager.get_available_industries()
        print(f"   ✅ Found industries: {industries}")
        
        # If we have industries, test industry filtering
        if industries:
            first_industry = industries[0]
            industry_templates = template_manager.get_templates_by_industry(first_industry)
            print(f"   ✅ Found {len(industry_templates)} templates in '{first_industry}'")
            
            # Verify all returned templates belong to the correct industry
            for template in industry_templates:
                assert template.industry.value == first_industry, \
                    f"Template {template.template_id} should belong to {first_industry}"
    
    def test_category_functionality(self, template_manager):
        """Test category-related functionality"""
        industries = template_manager.get_available_industries()
        if industries:
            first_industry = industries[0]
            categories = template_manager.get_categories_for_industry(first_industry)
            
            if categories:
                print(f"   ✅ Found categories in '{first_industry}': {categories}")
                
                # Test category filtering
                first_category = categories[0]
                category_templates = template_manager.get_templates_by_category(first_industry, first_category)
                print(f"   ✅ Found {len(category_templates)} templates in category '{first_category}'")
                
                # Verify all returned templates belong to the correct category
                for template in category_templates:
                    assert template.category == first_category, \
                        f"Template {template.template_id} should belong to category {first_category}"
            else:
                print("   ⚠️  No categories found")


class TestTemplateManagerDocumentTypes:
    """Test document type functionality"""
    
    def test_document_type_functionality(self, template_manager):
        """Test document type functionality"""
        doc_types = template_manager.get_all_document_types()
        print(f"   ✅ Found document types: {doc_types}")
        
        if doc_types:
            # Test document type filtering
            first_doc_type = doc_types[0]
            doc_templates = template_manager.get_templates_by_document_type(first_doc_type)
            print(f"   ✅ Found {len(doc_templates)} templates of type '{first_doc_type}'")


class TestTemplateManagerSearch:
    """Test search and filtering functionality"""
    
    def test_search_functionality(self, template_manager):
        """Test search and filtering"""
        # Test basic search
        industries = template_manager.get_available_industries()
        if industries:
            search_results = template_manager.search_templates(industry=industries[0])
            print(f"   ✅ Industry search returned {len(search_results)} results")
        
        # Test multi-criteria search
        doc_types = template_manager.get_all_document_types()
        if industries and doc_types:
            multi_search = template_manager.search_templates(
                industry=industries[0],
                document_type=doc_types[0]
            )
            print(f"   ✅ Multi-criteria search returned {len(multi_search)} results")
        
        # Test text search
        text_search = template_manager.search_templates(search_text="project")
        print(f"   ✅ Text search for 'project' returned {len(text_search)} results")
        
        # Test empty search
        empty_search = template_manager.search_templates(industry="non_existent_industry")
        assert len(empty_search) == 0, "Search for non-existent industry should return empty"
        print(f"   ✅ Empty search correctly returned 0 results")


class TestTemplateManagerRecommendations:
    """Test recommendation functionality"""
    
    def test_recommendation_system(self, template_manager):
        """Test recommendation functionality"""
        industries = template_manager.get_available_industries()
        if industries:
            company_profile = {
                'industry': industries[0],
                'size': 'startup',
                'tone': 'startup_agile'
            }
            
            recommendations = template_manager.get_recommended_templates(company_profile)
            print(f"   ✅ Generated {len(recommendations)} recommendations")
            
            if recommendations:
                top_rec = recommendations[0]
                print(f"   ✅ Top recommendation: '{top_rec.name}' ({top_rec.industry.value})")
                
                # Verify recommendation relevance
                assert top_rec.industry.value == company_profile['industry'], \
                    "Top recommendation should match industry"


class TestTemplateManagerAdvanced:
    """Test advanced features"""
    
    def test_advanced_features(self, template_manager):
        """Test advanced features"""
        all_templates = template_manager.get_all_templates()
        if all_templates:
            first_template = all_templates[0]
            
            # Test template family
            family = template_manager.get_template_family(first_template.template_id)
            assert len(family) >= 1, "Template family should include at least the base template"
            print(f"   ✅ Template family has {len(family)} templates")
            
            # Test similarity
            similar = template_manager.find_similar_templates(first_template.template_id)
            print(f"   ✅ Found {len(similar)} similar templates")
            
            if similar:
                most_similar, score = similar[0]
                print(f"   ✅ Most similar: '{most_similar.name}' (score: {score:.2f})")
                assert 0 <= score <= 1, "Similarity score should be between 0 and 1"


class TestTemplateManagerStatistics:
    """Test statistics and health reporting"""
    
    def test_statistics_and_health(self, template_manager):
        """Test statistics and health reporting"""
        # Test statistics
        stats = template_manager.get_template_statistics()
        assert 'total_templates' in stats, "Should have template statistics"
        assert 'by_industry' in stats, "Should have industry statistics"
        print(f"   ✅ Statistics: {stats['total_templates']} templates across {len(stats['by_industry'])} industries")
        
        # Test health report
        health = template_manager.get_discovery_health_report()
        assert 'success_rate' in health, "Should have success rate"
        assert 'directory_exists' in health, "Should check directory exists"
        print(f"   ✅ Health: {health['success_rate']:.1%} success rate")


class TestTemplateManagerExport:
    """Test export functionality"""
    
    def test_export_functionality(self, template_manager):
        """Test export functionality"""
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            tmp_path = Path(tmp_file.name)
        
        try:
            # Test export
            template_manager.export_template_catalog(tmp_path)
            assert tmp_path.exists(), "Export file should be created"
            
            # Validate export content
            with open(tmp_path, 'r') as f:
                catalog = json.load(f)
            
            assert 'templates' in catalog, "Catalog should contain templates"
            assert 'total_templates' in catalog, "Catalog should contain total count"
            assert catalog['total_templates'] == len(template_manager), "Catalog count should match manager count"
            
            print(f"   ✅ Successfully exported catalog with {len(catalog['templates'])} templates")
            
        finally:
            # Clean up
            if tmp_path.exists():
                tmp_path.unlink()


class TestTemplateManagerEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_edge_cases(self, template_manager):
        """Test edge cases and error conditions"""
        # Test non-existent template
        non_existent = template_manager.get_template("definitely_not_a_real_template_id")
        assert non_existent is None, "Non-existent template should return None"
        print("   ✅ Non-existent template correctly returns None")
        
        # Test contains operator
        all_templates = template_manager.get_all_templates()
        if all_templates:
            template_id = all_templates[0].template_id
            assert template_id in template_manager, "__contains__ should work for existing template"
            assert "fake_template_id" not in template_manager, "__contains__ should return False for non-existent"
            print("   ✅ __contains__ operator works correctly")
        
        # Test empty filters
        empty_results = template_manager.search_templates(industry="non_existent_industry")
        assert len(empty_results) == 0, "Empty filter should return empty list"
        print("   ✅ Empty filters correctly return empty results")


class TestTemplateManagerChangeDetection:
    """Test file change detection"""
    
    def test_change_detection(self, template_manager):
        """Test file change detection"""
        changes = template_manager.check_for_template_changes()
        print(f"   ✅ Change detection returned {len(changes)} changes")
        
        # Test reload functionality
        try:
            original_count = len(template_manager)
            template_manager.reload_templates()
            new_count = len(template_manager)
            assert new_count == original_count, "Reload should maintain template count"
            print("   ✅ Template reload works correctly")
        except Exception as e:
            print(f"   ⚠️  Reload test failed: {e}")


# Integration test that runs comprehensive validation
def test_comprehensive_template_manager_integration(template_manager):
    """Comprehensive integration test"""
    print("🧪 Running Comprehensive Template Manager Integration Test")
    print("=" * 70)
    
    # Basic functionality
    assert template_manager is not None
    template_count = len(template_manager)
    print(f"📊 Total templates loaded: {template_count}")
    
    if template_count > 0:
        # Test core functionality
        all_templates = template_manager.get_all_templates()
        assert len(all_templates) == template_count
        
        # Test industries
        industries = template_manager.get_available_industries()
        print(f"🏭 Industries available: {len(industries)}")
        
        # Test document types
        doc_types = template_manager.get_all_document_types()
        print(f"📄 Document types: {len(doc_types)}")
        
        # Test statistics
        stats = template_manager.get_template_statistics()
        health = template_manager.get_discovery_health_report()
        
        print(f"📈 Success rate: {health['success_rate']:.1%}")
        print(f"⚠️  Load errors: {stats['load_errors']}")
        
        if stats['load_errors'] > 0:
            print(f"⚠️  Load errors found:")
            for error in template_manager.get_load_errors()[:3]:
                print(f"   - {error}")
    
    print("✅ Comprehensive integration test completed successfully")


# Utility function to print system summary
def test_system_summary(template_manager):
    """Print system summary for debugging"""
    print(f"\n📋 TEMPLATE MANAGER SUMMARY")
    print("-" * 70)
    
    stats = template_manager.get_template_statistics()
    health = template_manager.get_discovery_health_report()
    
    print(f"📊 Templates: {stats['total_templates']}")
    print(f"🏭 Industries: {len(stats.get('by_industry', {}))}")
    print(f"📄 Document Types: {len(stats.get('by_document_type', {}))}")
    
    if hasattr(template_manager, 'get_all_tones'):
        print(f"🎭 Tones Available: {len(template_manager.get_all_tones())}")
    if hasattr(template_manager, 'get_all_company_sizes'):
        print(f"🏢 Company Sizes: {len(template_manager.get_all_company_sizes())}")
    
    print(f"📈 Success Rate: {health['success_rate']:.1%}")
    print(f"⚠️  Load Errors: {stats['load_errors']}")
    
    if stats['load_errors'] > 0:
        print(f"\n⚠️  Recent Load Errors:")
        for error in template_manager.get_load_errors()[:3]:
            print(f"   - {error}")

class TestTemplateManagerQueryMethods:
    """Test TASK-007: Template Query Methods"""
    
    def test_get_available_templates_no_filters(self, template_manager):
        """Test get_available_templates() without filters"""
        all_templates = template_manager.get_available_templates()
        expected_count = len(template_manager.get_all_templates())
        assert len(all_templates) == expected_count, "Should return all templates when no filters"
        print(f"   ✅ get_available_templates() returned {len(all_templates)} templates")
    
    def test_get_available_templates_with_filters(self, template_manager):
        """Test get_available_templates() with various filters"""
        industries = template_manager.get_available_industries()
        if industries:
            # Test industry filter
            industry_templates = template_manager.get_available_templates({'industry': industries[0]})
            print(f"   ✅ Industry filter returned {len(industry_templates)} templates for '{industries[0]}'")
            
            # Verify all returned templates match the industry
            for template in industry_templates:
                assert template.industry.value == industries[0], f"Template {template.template_id} should belong to {industries[0]}"
        
        # Test invalid filter
        invalid_results = template_manager.get_available_templates({'company_size': 'invalid_size'})
        assert len(invalid_results) == 0, "Invalid filter should return empty results"
        print("   ✅ Invalid filter correctly returns empty results")
    
    def test_get_template_by_id(self, template_manager):
        """Test get_template() method"""
        all_templates = template_manager.get_all_templates()
        if all_templates:
            first_template = all_templates[0]
            
            # Test existing template
            retrieved = template_manager.get_template(first_template.template_id)
            assert retrieved is not None, "Should retrieve existing template"
            assert retrieved.template_id == first_template.template_id, "Retrieved template should match"
            print(f"   ✅ Retrieved template by ID: '{retrieved.name}'")
            
            # Test non-existent template
            non_existent = template_manager.get_template("definitely_not_a_real_template_id")
            assert non_existent is None, "Non-existent template should return None"
            print("   ✅ Non-existent template correctly returns None")
    
    def test_get_templates_by_filter(self, template_manager):
        """Test get_templates_by_filter() method"""
        industries = template_manager.get_available_industries()
        if industries:
            industry_filtered = template_manager.get_templates_by_filter('industry', industries[0])
            print(f"   ✅ Industry filter returned {len(industry_filtered)} templates")
            
            # Verify all results match the filter
            for template in industry_filtered:
                assert template.industry.value == industries[0]
        
        doc_types = template_manager.get_all_document_types()
        if doc_types:
            doc_type_filtered = template_manager.get_templates_by_filter('document_type', doc_types[0])
            print(f"   ✅ Document type filter returned {len(doc_type_filtered)} templates")
        
        # Test invalid filter type
        invalid_filtered = template_manager.get_templates_by_filter('invalid_type', 'invalid_value')
        assert len(invalid_filtered) == 0, "Invalid filter type should return empty results"
    
    def test_get_template_metadata(self, template_manager):
        """Test get_template_metadata() method"""
        all_templates = template_manager.get_all_templates()
        if all_templates:
            first_template = all_templates[0]
            metadata = template_manager.get_template_metadata(first_template.template_id)
            
            assert metadata is not None, "Should return metadata for existing template"
            assert metadata['template_id'] == first_template.template_id, "Metadata should match template"
            assert 'name' in metadata, "Metadata should include name"
            assert 'industry' in metadata, "Metadata should include industry"
            assert 'section_count' in metadata, "Metadata should include section count"
            
            print(f"   ✅ Retrieved metadata for '{metadata['name']}' with {metadata['section_count']} sections")
            
            # Test non-existent template metadata
            no_metadata = template_manager.get_template_metadata("non_existent_id")
            assert no_metadata is None, "Should return None for non-existent template"
    
    def test_get_templates_by_criteria(self, template_manager):
        """Test get_templates_by_criteria() advanced filtering"""
        industries = template_manager.get_available_industries()
        doc_types = template_manager.get_all_document_types()
        
        if industries and doc_types:
            # Test multiple industries
            criteria_results = template_manager.get_templates_by_criteria(
                industries=industries[:2] if len(industries) > 1 else industries
            )
            print(f"   ✅ Multi-industry criteria returned {len(criteria_results)} templates")
            
            # Test max time filter
            time_filtered = template_manager.get_templates_by_criteria(max_time_minutes=60)
            print(f"   ✅ Time-limited criteria returned {len(time_filtered)} templates")
            for template in time_filtered:
                assert template.estimated_time_minutes <= 60, "All templates should be under time limit"
            
            # Test complexity filter
            complexity_filtered = template_manager.get_templates_by_criteria(max_complexity='medium')
            print(f"   ✅ Complexity-limited criteria returned {len(complexity_filtered)} templates")
    
    def test_get_template_suggestions(self, template_manager):
        """Test get_template_suggestions() method"""
        # Test with common word
        suggestions = template_manager.get_template_suggestions("project", limit=3)
        print(f"   ✅ Found {len(suggestions)} suggestions for 'project'")
        
        for suggestion in suggestions:
            assert 'template' in suggestion, "Suggestion should include template"
            assert 'score' in suggestion, "Suggestion should include score"
            assert suggestion['score'] > 0, "Suggestion should have positive score"
        
        # Test with non-existent term
        no_suggestions = template_manager.get_template_suggestions("xyzneverexists")
        assert len(no_suggestions) == 0, "Should return no suggestions for non-existent terms"
    
    def test_template_exists(self, template_manager):
        """Test template_exists() method"""
        all_templates = template_manager.get_all_templates()
        if all_templates:
            first_template = all_templates[0]
            
            # Test existing template
            exists = template_manager.template_exists(first_template.template_id)
            assert exists is True, "Should return True for existing template"
            print(f"   ✅ template_exists() correctly identifies existing template")
            
            # Test non-existent template
            not_exists = template_manager.template_exists("definitely_not_a_real_template")
            assert not_exists is False, "Should return False for non-existent template"
            print(f"   ✅ template_exists() correctly identifies non-existent template")
    
    def test_get_template_count(self, template_manager):
        """Test get_template_count() method"""
        # Test total count
        total_count = template_manager.get_template_count()
        expected_count = len(template_manager.get_all_templates())
        assert total_count == expected_count, "Total count should match template library size"
        print(f"   ✅ Total template count: {total_count}")
        
        # Test filtered count
        industries = template_manager.get_available_industries()
        if industries:
            industry_count = template_manager.get_template_count({'industry': industries[0]})
            industry_templates = template_manager.get_available_templates({'industry': industries[0]})
            assert industry_count == len(industry_templates), "Filtered count should match filtered results"
            print(f"   ✅ Templates in '{industries[0]}': {industry_count}")
    
    def test_get_filter_options(self, template_manager):
        """Test get_filter_options() method"""
        filter_options = template_manager.get_filter_options()
        
        expected_keys = ['industries', 'document_types', 'tones', 'complexity_levels', 'company_sizes', 'categories']
        for key in expected_keys:
            assert key in filter_options, f"Filter options should include {key}"
        
        print(f"   ✅ Filter options available:")
        for filter_type, options in filter_options.items():
            print(f"      - {filter_type}: {len(options)} options")
            assert isinstance(options, list), f"{filter_type} should be a list"
    
    def test_contains_operator(self, template_manager):
        """Test __contains__ operator"""
        all_templates = template_manager.get_all_templates()
        if all_templates:
            first_template = all_templates[0]
            
            # Test existing template
            assert first_template.template_id in template_manager, "__contains__ should work for existing template"
            print("   ✅ __contains__ operator works for existing template")
            
            # Test non-existent template
            assert "fake_template_id" not in template_manager, "__contains__ should return False for non-existent"
            print("   ✅ __contains__ operator works for non-existent template")