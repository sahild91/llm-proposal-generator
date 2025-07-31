"""
LLM Client for handling different LLM providers
Supports OpenAI, Anthropic, and local LLMs
"""

import json
import requests
from typing import Dict, Any, Optional, List
import time
from abc import ABC, abstractmethod

class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    def generate_completion(self, prompt: str, **kwargs) -> str:
        pass

class OpenAIProvider(LLMProvider):
    """OpenAI API provider"""
    
    def __init__(self, config: Dict[str, Any]):
        self.api_key = config.get('api_key', '')
        self.model = config.get('model', 'gpt-4')
        self.endpoint = config.get('endpoint', 'https://api.openai.com/v1/chat/completions')
        self.max_tokens = config.get('max_tokens', 4000)
        self.temperature = config.get('temperature', 0.7)
    
    def generate_completion(self, prompt: str, **kwargs) -> str:
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': self.model,
            'messages': [
                {'role': 'system', 'content': 'You are a professional technical writer specializing in project proposals and feasibility analysis.'},
                {'role': 'user', 'content': prompt}
            ],
            'max_tokens': kwargs.get('max_tokens', self.max_tokens),
            'temperature': kwargs.get('temperature', self.temperature)
        }
        
        try:
            response = requests.post(self.endpoint, headers=headers, json=data, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            return result['choices'][0]['message']['content']
        except requests.exceptions.RequestException as e:
            raise Exception(f"OpenAI API error: {e}")
        except KeyError as e:
            raise Exception(f"Unexpected API response format: {e}")

class AnthropicProvider(LLMProvider):
    """Anthropic Claude API provider"""
    
    def __init__(self, config: Dict[str, Any]):
        self.api_key = config.get('api_key', '')
        self.model = config.get('model', 'claude-3-sonnet-20240229')
        self.endpoint = config.get('endpoint', 'https://api.anthropic.com/v1/messages')
        self.max_tokens = config.get('max_tokens', 4000)
        self.temperature = config.get('temperature', 0.7)
    
    def generate_completion(self, prompt: str, **kwargs) -> str:
        headers = {
            'x-api-key': self.api_key,
            'Content-Type': 'application/json',
            'anthropic-version': '2023-06-01'
        }
        
        data = {
            'model': self.model,
            'max_tokens': kwargs.get('max_tokens', self.max_tokens),
            'temperature': kwargs.get('temperature', self.temperature),
            'messages': [
                {'role': 'user', 'content': prompt}
            ]
        }
        
        try:
            response = requests.post(self.endpoint, headers=headers, json=data, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            return result['content'][0]['text']
        except requests.exceptions.RequestException as e:
            raise Exception(f"Anthropic API error: {e}")
        except KeyError as e:
            raise Exception(f"Unexpected API response format: {e}")

class LocalLLMProvider(LLMProvider):
    """Local LLM provider (placeholder for llama-cpp integration)"""
    
    def __init__(self, config: Dict[str, Any]):
        self.model_path = config.get('model_path', '')
        self.endpoint = config.get('endpoint', 'http://localhost:8080/completion')
        self.max_tokens = config.get('max_tokens', 4000)
        self.temperature = config.get('temperature', 0.7)
    
    def generate_completion(self, prompt: str, **kwargs) -> str:
        # This is a placeholder implementation for local LLM
        # In a real implementation, you would integrate with llama-cpp-python
        data = {
            'prompt': prompt,
            'max_tokens': kwargs.get('max_tokens', self.max_tokens),
            'temperature': kwargs.get('temperature', self.temperature),
            'stop': ['Human:', 'Assistant:']
        }
        
        try:
            response = requests.post(self.endpoint, json=data, timeout=120)
            response.raise_for_status()
            
            result = response.json()
            return result.get('content', 'Error: No content returned from local LLM')
        except requests.exceptions.RequestException as e:
            raise Exception(f"Local LLM error: {e}")

class LLMClient:
    """Main LLM client that manages different providers"""
    
    def __init__(self, config: Dict[str, Any], company_config: Dict[str, Any] = None):
        self.config = config
        self.company_config = company_config or {}
        self.provider = self._create_provider()
    
    def _create_provider(self) -> LLMProvider:
        """Create the appropriate LLM provider based on configuration"""
        provider_name = self.config.get('provider', 'openai').lower()
        
        if provider_name == 'openai':
            return OpenAIProvider(self.config)
        elif provider_name == 'anthropic':
            return AnthropicProvider(self.config)
        elif provider_name == 'local':
            return LocalLLMProvider(self.config)
        else:
            raise ValueError(f"Unsupported LLM provider: {provider_name}")
    
    def generate_proposal(self, project_data: Dict[str, Any]) -> str:
        """Generate a project proposal based on project data"""
        prompt = self._create_proposal_prompt(project_data)
        return self.provider.generate_completion(prompt)
    
    def generate_feasibility(self, project_data: Dict[str, Any]) -> str:
        """Generate a feasibility analysis based on project data"""
        prompt = self._create_feasibility_prompt(project_data)
        return self.provider.generate_completion(prompt)
    
    def refine_document(self, document_content: str, refinement_request: str) -> str:
        """Refine existing document based on user request"""
        prompt = f"""
        Please refine the following document based on this request: {refinement_request}
        
        Current document:
        {document_content}
        
        Please provide the refined version in markdown format.
        """
        return self.provider.generate_completion(prompt)
    
    def _create_proposal_prompt(self, project_data: Dict[str, Any]) -> str:
        """Create a structured prompt for proposal generation"""
        
        # Company context
        company_context = self._get_company_context()
        
        return f"""
        {company_context}
        
        Create a professional project proposal in markdown format based on the following information:

        Project Name: {project_data.get('project_name', 'N/A')}
        Client Name: {project_data.get('client_name', 'N/A')}
        Project Type: {project_data.get('project_type', 'N/A')}
        Expected Duration: {project_data.get('expected_duration', 'N/A')}
        
        Requirements:
        {project_data.get('requirements', 'N/A')}
        
        Hardware Components: {', '.join(project_data.get('hardware_components', []))}
        Software Modules: {', '.join(project_data.get('software_modules', []))}
        
        Please structure the proposal with the following sections:
        1. Executive Summary
        2. Project Overview
        3. Technical Approach
        4. Deliverables
        5. Timeline & Milestones
        6. Resource Requirements
        7. Budget Estimation
        8. Risk Assessment
        9. Terms & Conditions
        
        Make it professional, detailed, and tailored to the specific project requirements.
        Highlight our company's expertise in {', '.join(self.company_config.get('specializations', ['technology solutions']))}.
        """
    
    def _create_feasibility_prompt(self, project_data: Dict[str, Any]) -> str:
        """Create a structured prompt for feasibility analysis"""
        
        # Company context
        company_context = self._get_company_context()
        
        return f"""
        {company_context}
        
        Create a comprehensive feasibility analysis in markdown format for the following project:

        Project Name: {project_data.get('project_name', 'N/A')}
        Client Name: {project_data.get('client_name', 'N/A')}
        Project Type: {project_data.get('project_type', 'N/A')}
        Expected Duration: {project_data.get('expected_duration', 'N/A')}
        
        Requirements:
        {project_data.get('requirements', 'N/A')}
        
        Hardware Components: {', '.join(project_data.get('hardware_components', []))}
        Software Modules: {', '.join(project_data.get('software_modules', []))}
        
        Please analyze the following aspects:
        
        ## Technical Feasibility
        - Technology stack assessment
        - Technical challenges and solutions
        - Integration complexity
        - Scalability considerations
        
        ## Operational Feasibility
        - Resource availability
        - Team capability requirements
        - Infrastructure needs
        - Workflow integration
        
        ## Economic Feasibility
        - Cost-benefit analysis
        - ROI projections
        - Budget requirements
        - Financial risks
        
        ## Legal & Compliance Feasibility
        - Regulatory requirements
        - Compliance considerations
        - Intellectual property concerns
        - Legal risks
        
        ## Schedule Feasibility
        - Timeline assessment
        - Critical path analysis
        - Resource scheduling
        - Delivery milestones
        
        ## Risk Analysis
        - Technical risks
        - Business risks
        - Mitigation strategies
        - Contingency plans
        
        ## Recommendations
        - Go/No-go recommendation
        - Alternative approaches
        - Success criteria
        - Next steps
        
        Consider our company's expertise in {', '.join(self.company_config.get('specializations', ['technology solutions']))} 
        and experience in the {self.company_config.get('industry', 'technology')} industry.
        
        Provide detailed analysis with specific recommendations and actionable insights.
        """
    
    def _get_company_context(self) -> str:
        """Get company context for prompts"""
        if not self.company_config:
            return "You are a professional technical writer specializing in project proposals and feasibility analysis."
        
        company_name = self.company_config.get('name', 'Our Company')
        industry = self.company_config.get('industry', 'technology')
        specializations = ', '.join(self.company_config.get('specializations', ['technology solutions']))
        
        return f"""
        You are a professional technical writer working for {company_name}, a leading {industry} company.
        Our company specializes in: {specializations}.
        
        Write all proposals and analyses from the perspective of {company_name}, highlighting our expertise 
        and capabilities in the relevant areas. Make sure to position our company as the ideal partner 
        for this project based on our industry experience and specializations.
        """
    
    def test_connection(self) -> bool:
        """Test if the LLM provider is accessible"""
        try:
            test_prompt = "Please respond with 'Connection successful' if you can read this message."
            response = self.provider.generate_completion(test_prompt, max_tokens=50)
            return "successful" in response.lower() or len(response.strip()) > 0
        except Exception as e:
            print(f"LLM connection test failed: {e}")
            return False