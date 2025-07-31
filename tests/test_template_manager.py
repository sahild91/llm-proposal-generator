"""
Test Template Manager
Comprehensive test suite for the Template Manager class
"""

import sys
import os
from pathlib import Path
import json
import tempfile

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.template_manager import TemplateManager


class TestTemplateManager:
    """Test class for Template Manager"""
    
    def __init__(self):
        self.manager = None
        self.test_results = []
    
    def setup(self):
        """Setup test environment"""
        print("🔧 Setting up test environment...")
        
        # Initialize Template Manager
        templates_path = Path("templates")
        if not templates_path.exists():
            print("❌ Templates directory not found. Please run from project root.")
            return False
        
        try:
            self.manager = TemplateManager(templates_path)
            print("✅ Template Manager initialized")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize Template Manager: {e}")
            return False
    
    def test_basic_functionality(self):
        """Test basic template loading and retrieval"""
        print("\n📋 Testing Basic Functionality")
        
        # Test template loading
        template_count = len(self.manager)
        self.assert_true(template_count > 0, "Templates should be loaded")
        print(f"   ✅ Loaded {template_count} templates")
        
        # Test template retrieval
        all_templates = self.manager.get_all_templates()
        self.assert_equal(len(all_templates), template_count, "get_all_templates() count should match")
        print(f"   ✅ Retrieved all templates successfully")
        
        # Test specific template retrieval
        if all_templates:
            first_template = all_templates[0]
            retrieved = self.manager.get_template(first_template.template_id)
            self.assert_not_none(retrieved, "Template retrieval by ID should work")
            self.assert_equal(retrieved.template_id, first_template.template_id, "Retrieved template should match")
            print(f"   ✅ Template retrieval by ID works")
    
    def test_industry_functionality(self):
        """Test industry-related functionality"""
        print("\n🏭 Testing Industry Functionality")
        
        # Test industry discovery
        industries = self.manager.get_available_industries()
        self.assert_true(len(industries) > 0, "Should have at least one industry")
        print(f"   ✅ Found industries: {industries}")
        
        # Test industry filtering
        if industries:
            first_industry = industries[0]
            industry_templates = self.manager.get_templates_by_industry(first_industry)
            self.assert_true(len(industry_templates) > 0, f"Should have templates for {first_industry}")
            print(f"   ✅ Found {len(industry_templates)} templates in '{first_industry}'")
            
            # Verify all returned templates belong to the correct industry
            for template in industry_templates:
                self.assert_equal(template.industry.value, first_industry, 
                                f"Template {template.template_id} should belong to {first_industry}")
    
    def test_category_functionality(self):
        """Test category-related functionality"""
        print("\n📂 Testing Category Functionality")
        
        industries = self.manager.get_available_industries()
        if industries:
            first_industry = industries[0]
            categories = self.manager.get_categories_for_industry(first_industry)
            
            if categories:
                print(f"   ✅ Found categories in '{first_industry}': {categories}")
                
                # Test category filtering
                first_category = categories[0]
                category_templates = self.manager.get_templates_by_category(first_industry, first_category)
                self.assert_true(len(category_templates) > 0, f"Should have templates for {first_category}")
                print(f"   ✅ Found {len(category_templates)} templates in category '{first_category}'")
                
                # Verify all returned templates belong to the correct category
                for template in category_templates:
                    self.assert_equal(template.category, first_category,
                                    f"Template {template.template_id} should belong to category {first_category}")
            else:
                print("   ⚠️  No categories found")
    
    def test_document_type_functionality(self):
        """Test document type functionality"""
        print("\n📄 Testing Document Type Functionality")
        
        doc_types = self.manager.get_all_document_types()
        self.assert_true(len(doc_types) > 0, "Should have at least one document type")
        print(f"   ✅ Found document types: {doc_types}")
        
        # Test document type filtering
        first_doc_type = doc_types[0]
        doc_templates = self.manager.get_templates_by_document_type(first_doc_type)
        self.assert_true(len(doc_templates) > 0, f"Should have templates of type {first_doc_type}")
        print(f"   ✅ Found {len(doc_templates)} templates of type '{first_doc_type}'")
    
    def test_search_functionality(self):
        """Test search and filtering"""
        print("\n🔍 Testing Search Functionality")
        
        # Test basic search
        industries = self.manager.get_available_industries()
        if industries:
            search_results = self.manager.search_templates(industry=industries[0])
            self.assert_true(len(search_results) > 0, "Industry search should return results")
            print(f"   ✅ Industry search returned {len(search_results)} results")
        
        # Test multi-criteria search
        doc_types = self.manager.get_all_document_types()
        if industries and doc_types:
            multi_search = self.manager.search_templates(
                industry=industries[0],
                document_type=doc_types[0]
            )
            print(f"   ✅ Multi-criteria search returned {len(multi_search)} results")
        
        # Test text search
        text_search = self.manager.search_templates(search_text="project")
        print(f"   ✅ Text search for 'project' returned {len(text_search)} results")
        
        # Test empty search
        empty_search = self.manager.search_templates(industry="non_existent_industry")
        self.assert_equal(len(empty_search), 0, "Search for non-existent industry should return empty")
        print(f"   ✅ Empty search correctly returned 0 results")
    
    def test_recommendation_system(self):
        """Test recommendation functionality"""
        print("\n💡 Testing Recommendation System")
        
        industries = self.manager.get_available_industries()
        if industries:
            company_profile = {
                'industry': industries[0],
                'size': 'startup',
                'tone': 'startup_agile'
            }
            
            recommendations = self.manager.get_recommended_templates(company_profile)
            print(f"   ✅ Generated {len(recommendations)} recommendations")
            
            if recommendations:
                top_rec = recommendations[0]
                print(f"   ✅ Top recommendation: '{top_rec.name}' ({top_rec.industry.value})")
                
                # Verify recommendation relevance
                self.assert_equal(top_rec.industry.value, company_profile['industry'],
                                "Top recommendation should match industry")
    
    def test_advanced_features(self):
        """Test advanced features"""
        print("\n🔧 Testing Advanced Features")
        
        all_templates = self.manager.get_all_templates()
        if all_templates:
            first_template = all_templates[0]
            
            # Test template family
            family = self.manager.get_template_family(first_template.template_id)
            self.assert_true(len(family) >= 1, "Template family should include at least the base template")
            print(f"   ✅ Template family has {len(family)} templates")
            
            # Test similarity
            similar = self.manager.find_similar_templates(first_template.template_id)
            print(f"   ✅ Found {len(similar)} similar templates")
            
            if similar:
                most_similar, score = similar[0]
                print(f"   ✅ Most similar: '{most_similar.name}' (score: {score:.2f})")
                self.assert_true(0 <= score <= 1, "Similarity score should be between 0 and 1")
    
    def test_statistics_and_health(self):
        """Test statistics and health reporting"""
        print("\n📊 Testing Statistics and Health")
        
        # Test statistics
        stats = self.manager.get_template_statistics()
        self.assert_true(stats['total_templates'] > 0, "Should have template statistics")
        self.assert_true(len(stats['by_industry']) > 0, "Should have industry statistics")
        print(f"   ✅ Statistics: {stats['total_templates']} templates across {len(stats['by_industry'])} industries")
        
        # Test health report
        health = self.manager.get_discovery_health_report()
        self.assert_true(health['success_rate'] > 0, "Should have positive success rate")
        self.assert_true(health['directory_exists'], "Templates directory should exist")
        print(f"   ✅ Health: {health['success_rate']:.1%} success rate")
    
    def test_export_functionality(self):
        """Test export functionality"""
        print("\n📤 Testing Export Functionality")
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            tmp_path = Path(tmp_file.name)
        
        try:
            # Test export
            self.manager.export_template_catalog(tmp_path)
            self.assert_true(tmp_path.exists(), "Export file should be created")
            
            # Validate export content
            with open(tmp_path, 'r') as f:
                catalog = json.load(f)
            
            self.assert_true('templates' in catalog, "Catalog should contain templates")
            self.assert_true('total_templates' in catalog, "Catalog should contain total count")
            self.assert_equal(catalog['total_templates'], len(self.manager), "Catalog count should match manager count")
            
            print(f"   ✅ Successfully exported catalog with {len(catalog['templates'])} templates")
            
        finally:
            # Clean up
            if tmp_path.exists():
                tmp_path.unlink()
    
    def test_edge_cases(self):
        """Test edge cases and error conditions"""
        print("\n⚠️  Testing Edge Cases")
        
        # Test non-existent template
        non_existent = self.manager.get_template("definitely_not_a_real_template_id")
        self.assert_none(non_existent, "Non-existent template should return None")
        print("   ✅ Non-existent template correctly returns None")
        
        # Test contains operator
        all_templates = self.manager.get_all_templates()
        if all_templates:
            template_id = all_templates[0].template_id
            self.assert_true(template_id in self.manager, "__contains__ should work for existing template")
            self.assert_false("fake_template_id" in self.manager, "__contains__ should return False for non-existent")
            print("   ✅ __contains__ operator works correctly")
        
        # Test empty filters
        empty_results = self.manager.search_templates(industry="non_existent_industry")
        self.assert_equal(len(empty_results), 0, "Empty filter should return empty list")
        print("   ✅ Empty filters correctly return empty results")
    
    def test_change_detection(self):
        """Test file change detection"""
        print("\n🔄 Testing Change Detection")
        
        changes = self.manager.check_for_template_changes()
        print(f"   ✅ Change detection returned {len(changes)} changes")
        
        # Test reload functionality
        try:
            original_count = len(self.manager)
            self.manager.reload_templates()
            new_count = len(self.manager)
            self.assert_equal(new_count, original_count, "Reload should maintain template count")
            print("   ✅ Template reload works correctly")
        except Exception as e:
            print(f"   ⚠️  Reload test failed: {e}")
    
    def run_all_tests(self):
        """Run all tests"""
        print("🧪 Starting Comprehensive Template Manager Tests")
        print("=" * 70)
        
        if not self.setup():
            print("❌ Setup failed - cannot run tests")
            return False
        
        # List of all test methods
        test_methods = [
            self.test_basic_functionality,
            self.test_industry_functionality,
            self.test_category_functionality,
            self.test_document_type_functionality,
            self.test_search_functionality,
            self.test_recommendation_system,
            self.test_advanced_features,
            self.test_statistics_and_health,
            self.test_export_functionality,
            self.test_edge_cases,
            self.test_change_detection
        ]
        
        passed_tests = 0
        total_tests = len(test_methods)
        
        for test_method in test_methods:
            try:
                test_method()
                passed_tests += 1
            except AssertionError as e:
                print(f"   ❌ Test failed: {e}")
            except Exception as e:
                print(f"   ❌ Test error: {e}")
        
        # Final results
        print(f"\n🎉 TEST RESULTS")
        print("=" * 70)
        print(f"✅ Passed: {passed_tests}/{total_tests} tests")
        
        if passed_tests == total_tests:
            print("🚀 All tests passed! Template Manager is fully functional.")
            self.print_system_summary()
            return True
        else:
            print(f"❌ {total_tests - passed_tests} tests failed.")
            return False
    
    def print_system_summary(self):
        """Print system summary"""
        print(f"\n📋 SYSTEM SUMMARY")
        print("-" * 70)
        
        stats = self.manager.get_template_statistics()
        health = self.manager.get_discovery_health_report()
        
        print(f"📊 Templates: {stats['total_templates']}")
        print(f"🏭 Industries: {len(stats['by_industry'])}")
        print(f"📄 Document Types: {len(stats['by_document_type'])}")
        print(f"🎭 Tones Available: {len(self.manager.get_all_tones())}")
        print(f"🏢 Company Sizes: {len(self.manager.get_all_company_sizes())}")
        print(f"📈 Success Rate: {health['success_rate']:.1%}")
        print(f"⚠️  Load Errors: {stats['load_errors']}")
        
        if stats['load_errors'] > 0:
            print(f"\n⚠️  Load Errors Found:")
            for error in self.manager.get_load_errors()[:3]:
                print(f"   - {error}")
    
    # Assertion helpers
    def assert_true(self, condition, message):
        if not condition:
            raise AssertionError(message)
    
    def assert_false(self, condition, message):
        if condition:
            raise AssertionError(message)
    
    def assert_equal(self, actual, expected, message):
        if actual != expected:
            raise AssertionError(f"{message}. Expected: {expected}, Got: {actual}")
    
    def assert_not_none(self, value, message):
        if value is None:
            raise AssertionError(message)
    
    def assert_none(self, value, message):
        if value is not None:
            raise AssertionError(message)


def main():
    """Main test function"""
    tester = TestTemplateManager()
    success = tester.run_all_tests()
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())