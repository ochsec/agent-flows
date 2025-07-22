#!/usr/bin/env python3
"""
Research Manager Workflow - OpenRouter Implementation

This module implements the research manager workflow using OpenRouter
for multi-LLM access and task delegation.
"""

import os
import json
from datetime import datetime
from typing import Dict, Optional, List
from pathlib import Path

from pydantic import BaseModel, Field

# Import our OpenRouter client and web operations
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from workflows.openrouter_client import OpenRouterClient, WorkflowType, OpenRouterModels
tools_path = "/Users/chrisochsenreither/github/agent-flows/tools"
sys.path.append(tools_path)
from tools.web_operations import WebOperations


class ResearchContext(BaseModel):
    """Manages the research_context.md file for cumulative documentation"""
    
    file_path: Path = Field(default_factory=lambda: Path(os.getcwd()) / "research_context.md")
    sections: Dict[str, str] = Field(default_factory=dict)
    
    def set_working_directory(self, working_dir: str):
        """Set the working directory for the research context file"""
        self.file_path = Path(working_dir) / "research_context.md"
    
    def initialize(self, task_description: str) -> None:
        """Initialize research context file (starts fresh for new research task)"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Start fresh for each new research task
        content = f"""# Research Task: {task_description}
**Started:** {timestamp}

## Research Findings
_(This section will be populated by the Researcher mode)_

## Synthesis
_(This section will be populated by the Synthesizer mode)_

## Expert Analysis
_(This section will be populated by the Expert Consultant mode)_

## Verification
_(This section will be populated by the Fact-Checker mode)_

## Final Report
_(This section will be populated by the Writer mode)_

"""
        
        # Overwrite any existing file to start fresh
        with open(self.file_path, 'w') as f:
            f.write(content)
    
    def append_section(self, section_name: str, content: str) -> None:
        """Append content to a specific section"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        section_content = f"""
### {section_name} - {timestamp}

{content}

"""
        
        # Read current content
        with open(self.file_path, 'r') as f:
            current_content = f.read()
        
        # Find the section and append
        section_marker = f"## {section_name}"
        if section_marker in current_content:
            # Replace the section marker with marker + content
            updated_content = current_content.replace(
                f"{section_marker}\n_(This section will be populated by",
                f"{section_marker}\n{section_content}\n_(This section will be populated by"
            )
        else:
            # Append at the end
            updated_content = current_content + section_content
        
        with open(self.file_path, 'w') as f:
            f.write(updated_content)


class OpenRouterExecutor:
    """Handles execution of OpenRouter API calls with web search capabilities"""
    
    def __init__(self, model: Optional[str] = None, api_key: Optional[str] = None):
        self.client = OpenRouterClient(
            api_key=api_key,
            workflow_type=WorkflowType.RESEARCH
        )
        # Override model if specified
        if model:
            self.client.default_model.name = model
        
        # Initialize web operations for research
        self.web_ops = WebOperations()
        
        print(f"🔧 OpenRouter client initialized with model: {self.client.default_model.name}")
        print(f"🌐 Web search capabilities enabled")
    
    def execute_prompt(self, prompt: str, model: Optional[str] = None) -> str:
        """Execute a prompt using OpenRouter API"""
        print(f"🚀 Executing OpenRouter request...")
        
        result = self.client.execute_prompt(
            prompt=prompt,
            model=model,
            timeout=1800  # 30 minute timeout for comprehensive research
        )
        
        if not result.get("success", False):
            raise Exception(f"OpenRouter API error: {result.get('error', 'Unknown error')}")
        
        print(f"✅ Request completed in {result.get('execution_time', 0):.2f}s")
        print(f"📊 Usage: {result.get('usage', {}).get('total_tokens', 0)} tokens")
        
        return result["content"]


class SpecializedAgent:
    """Base class for specialized research agents"""
    
    def __init__(self, name: str, role_definition: str, instructions: str, executor: OpenRouterExecutor):
        self.name = name
        self.role_definition = role_definition
        self.instructions = instructions
        self.executor = executor
        self.context = ResearchContext()
    
    def create_system_prompt(self) -> str:
        """Create the agent's system prompt"""
        return f"""You are {self.name}.

{self.role_definition}

Instructions:
{self.instructions}

IMPORTANT: You must follow these instructions exactly and focus only on your specialized role."""
    
    def execute_task(self, task: str, model: Optional[str] = None) -> str:
        """Execute a research task using OpenRouter"""
        system_prompt = self.create_system_prompt()
        
        # Combine system prompt with task
        full_prompt = f"""{system_prompt}

Task: {task}

Please complete this task according to your role and instructions above."""
        
        return self.executor.execute_prompt(full_prompt, model)


class ResearcherAgent(SpecializedAgent):
    """Specialized agent for information gathering with web search"""
    
    def __init__(self, executor: OpenRouterExecutor):
        role_definition = """You are in Researcher Mode, an expert information gatherer 
specialized in discovering, collecting, and analyzing information related to specific research topics."""
        
        instructions = """Your role is to gather and analyze comprehensive information on assigned research topics.
1. Read any existing research context from research_context.md
2. Carefully analyze the research prompt to identify ALL dimensions that need investigation
3. Conduct systematic web research that addresses every aspect mentioned or implied in the prompt:
   - Search for authoritative sources covering all requested dimensions
   - Adapt your search strategy based on the specific requirements
   - Go beyond surface-level information to find detailed insights
   - Ensure comprehensive coverage of the topic from multiple perspectives
4. For each search result, fetch and analyze the content
5. Evaluate sources for credibility, currency, and accuracy
6. Organize information systematically with proper citations
7. Note conflicting information and identify gaps
8. Format findings with clear headings organized by the dimensions identified
9. APPEND findings to research_context.md in the Research Findings section

IMPORTANT: Your research scope should be determined by the prompt requirements, not by predefined categories. Be thorough in addressing ALL aspects requested.

You have access to web search and web fetch capabilities. Use them extensively."""
        
        super().__init__("Researcher", role_definition, instructions, executor)
    
    def perform_research(self, topic: str) -> str:
        """Perform comprehensive web research on a topic"""
        print(f"🔍 Starting web research on: {topic}")
        
        # Define search queries for comprehensive coverage
        search_queries = [
            f"{topic} comparison benchmark 2024",
            f"{topic} best models evaluation",
            f"{topic} performance analysis",
            f"{topic} official documentation",
            f"{topic} expert review guide"
        ]
        
        research_results = []
        
        for query in search_queries:
            print(f"🔎 Searching: {query}")
            try:
                # Perform web search
                search_results = self.executor.web_ops.web_search(query)
                
                # Fetch and analyze top results
                for result in search_results[:2]:  # Top 2 results per query
                    try:
                        print(f"📄 Fetching: {result['title']}")
                        fetch_result = self.executor.web_ops.web_fetch(
                            result['url'], 
                            f"Extract key information about {topic} from this content. Focus on factual data, comparisons, and specific recommendations."
                        )
                        
                        research_results.append({
                            'query': query,
                            'source': result['title'],
                            'url': result['url'],
                            'content': fetch_result['content']
                        })
                        
                    except Exception as e:
                        print(f"⚠️ Failed to fetch {result['url']}: {e}")
                        continue
                        
            except Exception as e:
                print(f"⚠️ Search failed for '{query}': {e}")
                continue
        
        # Compile research findings
        compiled_research = self._compile_research_findings(topic, research_results)
        return compiled_research
    
    def _compile_research_findings(self, topic: str, results: List[Dict]) -> str:
        """Compile research results into organized findings"""
        compiled = f"# Research Findings: {topic}\n\n"
        
        compiled += f"## Research Overview\n"
        compiled += f"Conducted {len(results)} content analyses across multiple sources.\n\n"
        
        compiled += f"## Key Findings\n\n"
        
        for i, result in enumerate(results, 1):
            compiled += f"### Source {i}: {result['source']}\n"
            compiled += f"**URL:** {result['url']}\n"
            compiled += f"**Search Query:** {result['query']}\n\n"
            compiled += f"**Analysis:**\n{result['content']}\n\n"
            compiled += "---\n\n"
        
        compiled += f"## Sources Summary\n"
        for result in results:
            compiled += f"- [{result['source']}]({result['url']})\n"
        
        return compiled


class SynthesizerAgent(SpecializedAgent):
    """Specialized agent for knowledge integration"""
    
    def __init__(self, executor: OpenRouterExecutor):
        role_definition = """You are in Synthesizer Mode, an expert in knowledge integration 
specialized in identifying patterns, connections, and insights across diverse research findings."""
        
        instructions = """Your role is to integrate diverse research findings into cohesive knowledge structures:
1. Read research findings from research_context.md
2. Analyze findings to identify core themes, patterns, and relationships
3. Organize information into coherent conceptual frameworks
4. Identify and resolve contradictions between sources
5. Extract key insights addressing core research questions
6. Maintain clear references to original sources
7. Present synthesis in structured format
8. APPEND synthesis to research_context.md in the Synthesis section"""
        
        super().__init__("Synthesizer", role_definition, instructions, executor)


class ExpertConsultantAgent(SpecializedAgent):
    """Specialized agent for domain expertise analysis"""
    
    def __init__(self, executor: OpenRouterExecutor):
        role_definition = """You are in Expert Consultant Mode, a domain specialist who 
analyzes research findings through the lens of expert knowledge in specific fields."""
        
        instructions = """Your role is to provide expert domain perspective on research findings:
1. Read synthesis from research_context.md
2. Analyze findings through specific domain expertise
3. Identify domain-specific implications and specialized context
4. Suggest domain-appropriate research directions
5. Evaluate methodological approaches
6. Translate findings into practical applications
7. APPEND analysis to research_context.md in the Expert Analysis section"""
        
        super().__init__("Expert Consultant", role_definition, instructions, executor)


class FactCheckerAgent(SpecializedAgent):
    """Specialized agent for verification"""
    
    def __init__(self, executor: OpenRouterExecutor):
        role_definition = """You are in Fact-Checker Mode, a meticulous verification specialist 
focused on ensuring the accuracy and reliability of research findings."""
        
        instructions = """Your role is to verify the accuracy of research findings:
1. Read all content from research_context.md
2. Systematically verify each significant claim or data point
3. Evaluate sources using rigorous criteria
4. Flag information with verification status
5. Identify and correct common information errors
6. Verify citation accuracy
7. Document verification process clearly
8. APPEND verification results to research_context.md in the Verification section"""
        
        super().__init__("Fact-Checker", role_definition, instructions, executor)


class WriterAgent(SpecializedAgent):
    """Specialized agent for technical report generation"""
    
    def __init__(self, executor: OpenRouterExecutor):
        role_definition = """You are in Writer Mode, an expert communicator specialized in 
transforming research findings into clear, engaging, and well-structured technical reports."""
        
        instructions = """Your role is to transform research findings into polished, professional reports with MANDATORY TECHNICAL DEPTH:
1. Read all sections from research_context.md
2. Create comprehensive report structure with executive summary, methodology, detailed findings, analysis, and conclusions
3. Technical Depth Requirements:
   - EVERY key finding MUST have technical explanation
   - Include specific implementation details and code examples
   - Explain underlying mechanisms with technical terminology
   - Include performance metrics and scalability considerations
4. Apply principles of clear, technical writing
5. Integrate evidence and citations properly
6. APPEND finalized report to research_context.md
7. Save finalized report in specified folder"""
        
        super().__init__("Writer", role_definition, instructions, executor)


class ResearchManagerWorkflow:
    """Main orchestrator for the research workflow using OpenRouter"""
    
    def __init__(self, model: Optional[str] = None, api_key: Optional[str] = None):
        self.executor = OpenRouterExecutor(model=model, api_key=api_key)
        self.context = ResearchContext()
        
        # Initialize specialized agents
        self.researcher = ResearcherAgent(self.executor)
        self.synthesizer = SynthesizerAgent(self.executor)
        self.expert_consultant = ExpertConsultantAgent(self.executor)
        self.fact_checker = FactCheckerAgent(self.executor)
        self.writer = WriterAgent(self.executor)
        
        # Workflow state tracking (manager's persistent context)
        self.current_step = 0
        self.workflow_steps = [
            "initialize",
            "research",
            "synthesize", 
            "expert_analysis",
            "fact_check",
            "write_report"
        ]
        
        # Manager's context preservation
        self.research_topic = ""
        self.workflow_progress = {}
        self.step_summaries = {}
        self.identified_issues = []
        self.quality_checks = {}
    
    def update_progress(self, step: str, summary: str, issues: Optional[List[str]] = None):
        """Update the manager's context with step progress"""
        self.current_step += 1
        self.workflow_progress[step] = {
            "completed": True,
            "timestamp": datetime.now().isoformat(),
            "summary": summary
        }
        self.step_summaries[step] = summary
        if issues:
            self.identified_issues.extend(issues)
    
    def create_contextual_prompt(self, agent_task: str, step: str) -> str:
        """Create a prompt with manager's context for better coordination"""
        context_summary = ""
        
        if self.step_summaries:
            context_summary = "\n\nMANAGER'S CONTEXT FROM PREVIOUS STEPS:\n"
            for completed_step, summary in self.step_summaries.items():
                context_summary += f"- {completed_step}: {summary}\n"
        
        if self.identified_issues:
            context_summary += "\nIDENTIFIED ISSUES TO ADDRESS:\n"
            for issue in self.identified_issues[-3:]:  # Last 3 issues
                context_summary += f"- {issue}\n"
        
        return f"""RESEARCH TOPIC: {self.research_topic}
CURRENT WORKFLOW STEP: {step}
PROGRESS: Step {self.current_step + 1} of {len(self.workflow_steps)}

{context_summary}

TASK FOR THIS STEP:
{agent_task}

IMPORTANT: You must read from research_context.md to access all previous work, but use the manager's context above to understand the workflow progress and any issues that need attention."""
    
    def execute_workflow(self, research_topic: str, output_folder: Optional[str] = None) -> str:
        """Execute the complete research workflow"""
        
        print(f"🔬 Starting OpenRouter Research Workflow: {research_topic}")
        print(f"🗂️  Current working directory: {os.getcwd()}")
        print(f"🗂️  Script directory: {Path(__file__).parent}")
        print(f"🗂️  Output folder: {output_folder}")
        print(f"🤖 Using model: {self.executor.client.default_model.name}")
        
        self.research_topic = research_topic
        
        # Step 1: Initialize Research Context
        print("📝 Initializing research context...")
        if output_folder:
            self.context.set_working_directory(str(output_folder))
        self.context.initialize(research_topic)
        self.update_progress("initialize", f"Initialized research context for: {research_topic}")
        
        # Step 2: Delegate to Researcher with web search
        print("🔍 Delegating to Researcher with web search capabilities...")
        
        # Use the new research method that includes web search
        researcher_result = self.researcher.perform_research(research_topic)
        self.context.append_section("Research Findings", researcher_result)
        
        # Extract summary for manager's context
        research_summary = f"Completed comprehensive research gathering on {research_topic}"
        self.update_progress("research", research_summary)
        
        # Step 3: Delegate to Synthesizer
        print("🧠 Delegating to Synthesizer...")
        synthesis_task = """Analyze the research findings in research_context.md.
        
Please identify core themes, patterns, and relationships across the research findings.
Organize the information into coherent frameworks and extract key insights that address
the research question. Resolve any contradictions found in the sources.

Append your synthesis to research_context.md in the Synthesis section."""
        
        contextual_prompt = self.create_contextual_prompt(synthesis_task, "synthesize")
        synthesizer_result = self.synthesizer.execute_task(contextual_prompt)
        self.context.append_section("Synthesis", synthesizer_result)
        
        synthesis_summary = "Completed synthesis of research findings, identified key patterns and insights"
        self.update_progress("synthesize", synthesis_summary)
        
        # Step 4: Delegate to Expert Consultant
        print("👨‍🔬 Delegating to Expert Consultant...")
        expert_task = f"""Provide expert analysis of the synthesis in research_context.md for: {research_topic}
        
Please analyze the findings through domain expertise, identify practical implications,
suggest future research directions, and translate findings into actionable insights.
Consider methodological approaches and real-world applications.

Append your expert analysis to research_context.md in the Expert Analysis section."""
        
        expert_result = self.expert_consultant.execute_task(expert_task)
        self.context.append_section("Expert Analysis", expert_result)
        
        # Step 5: Delegate to Fact-Checker
        print("✅ Delegating to Fact-Checker...")
        fact_check_task = f"""Verify the accuracy of all content in research_context.md for: {research_topic}
        
Please systematically verify claims, evaluate source credibility, check citation accuracy,
and flag any information that needs correction. Document your verification process clearly.

Append your verification results to research_context.md in the Verification section."""
        
        fact_check_result = self.fact_checker.execute_task(fact_check_task)
        self.context.append_section("Verification", fact_check_result)
        
        # Step 6: Delegate to Writer
        print("✍️ Delegating to Writer...")
        
        # Use current working directory if no output folder specified
        if output_folder is None:
            output_path = Path.cwd()
        else:
            output_path = Path(output_folder)
        
        # Create output folder if it doesn't exist
        output_path.mkdir(exist_ok=True)
        
        write_task = f"""Create a comprehensive technical report in MARKDOWN FORMAT using all sections from research_context.md for: {research_topic}

CRITICAL: The entire report must be in proper Markdown format with:
- Proper header hierarchy (# ## ### ####)
- Code blocks with syntax highlighting (```language)
- Tables for comparisons and data
- Bullet points and numbered lists
- Bold (**text**) and italic (*text*) formatting
- Proper link formatting [text](url)

REQUIRED CONTENT:
- Executive summary that addresses ALL dimensions covered in the research
- Detailed methodology section explaining research approach
- Comprehensive findings organized by the dimensions that were researched:
  * Each dimension should have appropriate depth and detail
  * Include data, metrics, and evidence where applicable
  * Use tables, lists, and formatting for clarity
  * Provide balanced coverage of different perspectives
- In-depth analysis that synthesizes findings across all dimensions
- Implications and recommendations based on the complete picture
- Comprehensive references with proper markdown links

IMPORTANT: The report structure and emphasis should reflect the actual research conducted and the dimensions that were investigated. Do not force a technical-only perspective if the research covered broader aspects.

The output must be publication-ready markdown that renders beautifully in any markdown viewer.
Do NOT save the report yourself - just return the complete markdown content."""
        
        writer_result = self.writer.execute_task(write_task)
        self.context.append_section("Final Report", writer_result)
        
        # Save final report to specified folder
        # Clean the research topic to create a valid filename
        import re
        clean_topic = re.sub(r'[^\w\s-]', '', research_topic)  # Remove special chars
        clean_topic = re.sub(r'[-\s]+', '_', clean_topic)  # Replace spaces/hyphens with underscores
        clean_topic = clean_topic.strip('_').lower()  # Remove leading/trailing underscores
        
        # Limit filename length to avoid filesystem issues
        max_length = 100
        if len(clean_topic) > max_length:
            clean_topic = clean_topic[:max_length].rstrip('_')
        
        report_filename = f"{clean_topic}_research_report_openrouter.md"
        report_path = output_path / report_filename
        
        with open(report_path, 'w') as f:
            f.write(f"# Research Report: {research_topic}\n\n")
            f.write(writer_result)
        
        # Clean up research_context.md after report generation
        try:
            research_context_path = self.context.file_path
            if research_context_path.exists():
                research_context_path.unlink()
                print(f"🧹 Cleaned up research context file: {research_context_path}")
            else:
                print(f"ℹ️  Research context file not found for cleanup: {research_context_path}")
        except Exception as e:
            print(f"⚠️  Warning: Could not delete research_context.md: {e}")
            print(f"   File path: {self.context.file_path}")
            print("   Please manually delete this file to prevent bloat")
        
        print("✅ OpenRouter research workflow completed!")
        print(f"📄 Final report saved to: {report_path}")
        
        return str(report_path)


def main():
    """Main entry point for the research manager workflow"""
    import argparse
    from dotenv import load_dotenv
    
    # Get the original working directory from the wrapper script
    original_cwd = os.environ.get('ORIGINAL_PWD', os.getcwd())
    
    # Change to the original working directory for the duration of the script
    if original_cwd != os.getcwd():
        print(f"🔄 Changing working directory from {os.getcwd()} to {original_cwd}")
        os.chdir(original_cwd)
    
    load_dotenv()
    
    parser = argparse.ArgumentParser(description="Research Manager Workflow - OpenRouter Integration")
    parser.add_argument("topic", help="Research topic to investigate")
    parser.add_argument("--output", "-o", default=None, help="Output folder for reports (default: current directory)")
    parser.add_argument("--model", help="OpenRouter model to use (e.g., anthropic/claude-3.5-sonnet)")
    parser.add_argument("--api-key", help="OpenRouter API key (or set OPENROUTER_API_KEY env var)")
    parser.add_argument("--list-models", action="store_true", help="List recommended models for research workflow")
    
    args = parser.parse_args()
    
    # List models if requested
    if args.list_models:
        print("Recommended OpenRouter Models for Research Workflow:")
        print("=" * 60)
        models = OpenRouterModels.get_recommended_models(WorkflowType.RESEARCH)
        for model in models:
            print(f"• {model.name}")
            print(f"  {model.description}")
            print(f"  Cost: ${model.cost_per_1k_tokens:.4f}/1K tokens")
            print(f"  Context: {model.context_window:,} tokens")
            print()
        return
    
    # Get OpenRouter API key from args or environment
    api_key = args.api_key or os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ Error: OpenRouter API key required.")
        print("   Set OPENROUTER_API_KEY environment variable or use --api-key")
        return 1
    
    # Initialize and run workflow
    workflow = ResearchManagerWorkflow(model=args.model, api_key=api_key)
    
    try:
        # Now that we're in the correct working directory, use args.output directly
        report_path = workflow.execute_workflow(args.topic, args.output)
        print("\n🎉 Research completed successfully!")
        print(f"📊 Report available at: {report_path}")
        
    except Exception as e:
        print(f"❌ Error during research workflow: {e}")
        raise


if __name__ == "__main__":
    main()