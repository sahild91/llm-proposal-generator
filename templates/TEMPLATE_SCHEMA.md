# Template Schema Documentation

This document defines the structure that all template files must follow.

## Template File Structure (.yaml format)

### Required Fields

```yaml
# Basic template metadata (REQUIRED)
template_id: "unique_identifier"     # Must be unique across all templates
name: "Human-Readable Name"          # Display name in UI
description: "Brief description"     # What this template generates
version: "1.0"                      # Template version

# Classification (REQUIRED)
industry: "technology"              # See INDUSTRIES list below
category: "software_development"    # Subcategory within industry
document_type: "proposal"          # proposal, report, manual, plan, specification

# Target audience (REQUIRED)
company_sizes:                      # Array of applicable company sizes
  - "startup"
  - "small"
tone: "startup_agile"              # See TONES list below

# Template structure (REQUIRED)
structure:
  sections:                        # Array of document sections
    - id: "section_id"            # Unique section identifier
      title: "Section Title"      # Display title
      required: true              # true/false
      order: 1                    # Display order (1, 2, 3...)
      prompt_template: |          # LLM instruction for this section
        Detailed instruction for what to generate in this section.
        Can be multiple lines with specific guidance.
```

### Optional Fields

```yaml
# Template variants (OPTIONAL)
variants:                          # Array of related template IDs
  - "template_enterprise_version"
  - "template_consulting_version"

# Industry requirements (OPTIONAL)
compliance_requirements:           # Array of compliance needs
  - "GDPR compliance"
  - "ISO 27001 considerations"

# Generation settings (OPTIONAL)
estimated_time_minutes: 30        # Time to complete
complexity_level: "medium"        # low, medium, high
prerequisites:                    # Array of prerequisites
  - "Project requirements defined"
  - "Technology stack selected"

# Usage metadata (AUTO-POPULATED by system)
usage_stats:
  created_date: "2024-01-01"
  last_modified: "2024-01-01"
  usage_count: 0
  success_rate: 0.0
```

## Controlled Vocabularies

### INDUSTRIES
- `technology`
- `manufacturing`
- `services`
- `business`
- `healthcare`
- `education`
- `retail`
- `logistics`
- `finance`
- `legal`

### COMPANY_SIZES
- `startup` (1-10 employees)
- `small` (11-50 employees)
- `medium` (51-250 employees)
- `large` (251-1000 employees)
- `enterprise` (1000+ employees)

### TONES
- `formal_corporate` - Professional, detailed, third-person
- `startup_agile` - Direct, energetic, action-oriented
- `government_compliance` - Formal, regulatory, precise
- `academic_research` - Scholarly, analytical, evidence-based
- `consulting_professional` - Expert, advisory, client-focused

### DOCUMENT_TYPES
- `proposal` - Business proposals and project proposals
- `report` - Analysis reports and status reports
- `manual` - User manuals and procedure manuals
- `plan` - Strategic plans and implementation plans
- `specification` - Technical specifications and requirements
- `policy` - Company policies and procedures
- `agreement` - Contracts and service agreements

### COMPLEXITY_LEVELS
- `low` - Simple templates, 15-30 minutes to complete
- `medium` - Standard templates, 30-60 minutes to complete
- `high` - Complex templates, 60+ minutes to complete

## Section Structure Rules

### Required Section Fields
- `id` - Must be unique within the template
- `title` - Human-readable section name
- `required` - Boolean (true/false)
- `order` - Integer for section ordering
- `prompt_template` - Multi-line instruction for LLM

### Section ID Naming Convention
Use lowercase with underscores: `executive_summary`, `technical_approach`, `risk_assessment`

### Prompt Template Guidelines
- Be specific about what content to include
- Provide context about the section's purpose
- Include formatting guidance when needed
- Reference other sections when relevant
- Keep instructions clear and actionable

## Validation Rules

### Template ID Rules
- Must be unique across all templates
- Use lowercase with underscores
- Include industry/category hint: `tech_proposal_startup`
- No spaces or special characters

### Section Order Rules
- Must start with 1 and be consecutive
- No gaps in numbering (1, 2, 3, not 1, 3, 5)
- Order determines display sequence in UI

### Required Fields Validation
- At least one section must be required: true
- Industry must match controlled vocabulary
- Company_sizes must be array with valid values
- Tone must match controlled vocabulary

## Example Template Structure

```yaml
template_id: "software_project_proposal"
name: "Software Project Proposal"
description: "Comprehensive project proposal for software development projects"
version: "1.0"

industry: "technology"
category: "software_development"
document_type: "proposal"

company_sizes: 
  - "startup"
  - "small"
tone: "startup_agile"

structure:
  sections:
    - id: "executive_summary"
      title: "Executive Summary"
      required: true
      order: 1
      prompt_template: |
        Create a compelling executive summary that captures the project's value proposition.
        Include the client's key challenges, our proposed solution, and expected business impact.
        Keep it concise but comprehensive - this is what executives will read first.

    - id: "project_overview"
      title: "Project Overview"
      required: true
      order: 2
      prompt_template: |
        Provide a detailed project overview including:
        - Project objectives and scope
        - Target audience and users
        - Key functionality and features
        - Success criteria and measurable outcomes

variants:
  - "software_project_proposal_enterprise"

compliance_requirements:
  - "Data protection and privacy compliance"

estimated_time_minutes: 45
complexity_level: "high"
prerequisites:
  - "Project requirements clearly defined"
  - "Client information available"
```

## File Naming Convention

Templates should be saved as: `{template_id}.yaml`

Example: `software_project_proposal.yaml`

## Directory Structure

```
templates/
├── TEMPLATE_SCHEMA.md (this file)
├── technology/
│   ├── software_development/
│   │   ├── software_project_proposal.yaml
│   │   ├── technical_specification.yaml
│   │   └── api_documentation.yaml
│   └── hardware_development/
├── manufacturing/
└── services/
```

## Schema Version

Current Schema Version: 1.0
Last Updated: 2024-01-01

When schema changes are made, all existing templates must be validated against the new schema.