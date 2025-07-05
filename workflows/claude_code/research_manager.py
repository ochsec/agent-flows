#!/usr/bin/env python3
"""
Research Manager Workflow - LangChain Implementation

This module implements the research manager workflow described in modes/research_manager.md
using LangChain for multi-agent orchestration and task delegation.
"""

import os
import subprocess
import json
from datetime import datetime
from typing import Dict, Optional, Union, List
from pathlib import Path

from pydantic import BaseModel, Field


class ResearchContext(BaseModel):
    """Manages the research_context.md file for cumulative documentation"""
    
    file_path: Path = Field(default_factory=lambda: Path("research_context.md"))
    sections: Dict[str, str] = Field(default_factory=dict)
    
    def initialize(self, task_description: str) -> None:
        """Initialize or update research context file"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if self.file_path.exists():
            # Preserve existing content
            with open(self.file_path, 'r') as f:
                existing_content = f.read()
        else:
            existing_content = ""
        
        # Create new section for this research task
        new_section = f"""
# Research Task: {task_description}
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

---

"""
        
        # Write updated content
        with open(self.file_path, 'w') as f:
            f.write(existing_content + new_section)
    
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


class ClaudeCodeExecutor:
    """Handles execution of Claude Code commands"""
    
    def __init__(self, model: str = "sonnet", perplexity_api_key: Optional[str] = None):
        self.model = model
        self.perplexity_api_key = perplexity_api_key
        self.base_command = ["claude", "-p", "--model", model, "--output-format", "json"]
    
    def execute_claude_command(self, prompt: str, mcp_config: Optional[str] = None) -> str:
        """Execute a Claude Code command and return the response"""
        command = self.base_command.copy()
        
        # Add MCP configuration if provided
        if mcp_config:
            command.extend(["--mcp-config", mcp_config])
        
        # Add the prompt
        command.append(prompt)
        
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode != 0:
                raise Exception(f"Claude command failed: {result.stderr}")
            
            # Parse JSON response
            try:
                response_data = json.loads(result.stdout)
                return response_data.get("content", result.stdout)
            except json.JSONDecodeError:
                # Fallback to raw text if JSON parsing fails
                return result.stdout
                
        except subprocess.TimeoutExpired:
            raise Exception("Claude command timed out")
        except Exception as e:
            raise Exception(f"Error executing Claude command: {e}")


class SpecializedAgent:
    """Base class for specialized research agents"""
    
    def __init__(self, name: str, role_definition: str, instructions: str, executor: ClaudeCodeExecutor):
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
    
    def execute_task(self, task: str, mcp_config: Optional[str] = None) -> str:
        """Execute a research task using Claude Code"""
        system_prompt = self.create_system_prompt()
        
        # Combine system prompt with task
        full_prompt = f"""{system_prompt}

Task: {task}

Please complete this task according to your role and instructions above."""
        
        return self.executor.execute_claude_command(full_prompt, mcp_config)


class ResearcherAgent(SpecializedAgent):
    """Specialized agent for information gathering"""
    
    def __init__(self, executor: ClaudeCodeExecutor):
        role_definition = """You are in Researcher Mode, an expert information gatherer 
specialized in discovering, collecting, and analyzing information related to specific research topics."""
        
        instructions = """Your role is to gather and analyze high-quality information on assigned research topics.
1. Read any existing research context from research_context.md
2. Use Perplexity AI tools to conduct comprehensive research with strategic search queries
3. Evaluate information sources for credibility, currency, objectivity, and accuracy
4. Collect and organize information systematically
5. Track all sources with complete citations
6. Note conflicting information and identify gaps
7. Format findings with clear headings
8. APPEND findings to research_context.md in the Research Findings section"""
        
        super().__init__("Researcher", role_definition, instructions, executor)
    
    def create_mcp_config(self) -> str:
        """Create MCP configuration for Perplexity access"""
        if not self.executor.perplexity_api_key:
            return ""
        
        mcp_config = {
            "mcpServers": {
                "perplexity": {
                    "command": "npx",
                    "args": ["@perplexity-ai/mcp-server"],
                    "env": {
                        "PERPLEXITY_API_KEY": self.executor.perplexity_api_key
                    }
                }
            }
        }
        return json.dumps(mcp_config)
    
    def execute_task(self, task: str) -> str:
        """Execute research task with Perplexity integration"""
        mcp_config = self.create_mcp_config() if self.executor.perplexity_api_key else None
        return super().execute_task(task, mcp_config)


class SynthesizerAgent(SpecializedAgent):
    """Specialized agent for knowledge integration"""
    
    def __init__(self, executor: ClaudeCodeExecutor):
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
    
    def __init__(self, executor: ClaudeCodeExecutor):
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
    
    def __init__(self, executor: ClaudeCodeExecutor):
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
    
    def __init__(self, executor: ClaudeCodeExecutor):
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
    """Main orchestrator for the research workflow"""
    
    def __init__(self, model: str = "sonnet", perplexity_api_key: Optional[str] = None):
        self.executor = ClaudeCodeExecutor(model=model, perplexity_api_key=perplexity_api_key)
        self.context = ResearchContext()
        
        # Initialize specialized agents
        self.researcher = ResearcherAgent(self.executor)
        self.synthesizer = SynthesizerAgent(self.executor)
        self.expert_consultant = ExpertConsultantAgent(self.executor)
        self.fact_checker = FactCheckerAgent(self.executor)
        self.writer = WriterAgent(self.executor)
        
        # Workflow state
        self.current_step = 0
        self.workflow_steps = [
            "initialize",
            "research",
            "synthesize", 
            "expert_analysis",
            "fact_check",
            "write_report"
        ]
    
    def execute_workflow(self, research_topic: str, output_folder: str = "reports") -> str:
        """Execute the complete research workflow"""
        
        print(f"🔬 Starting Research Workflow: {research_topic}")
        
        # Step 1: Initialize Research Context
        print("📝 Initializing research context...")
        self.context.initialize(research_topic)
        
        # Step 2: Delegate to Researcher
        print("🔍 Delegating to Researcher...")
        research_task = f"""Conduct comprehensive research on: {research_topic}
        
Please gather high-quality information from multiple sources, evaluate credibility,
and organize findings systematically. Focus on collecting factual data, expert opinions,
current developments, and identifying any conflicting information or gaps.

After completing your research, append your findings to research_context.md in the 
Research Findings section."""
        
        researcher_result = self.researcher.execute_task(research_task)
        self.context.append_section("Research Findings", researcher_result)
        
        # Step 3: Delegate to Synthesizer
        print("🧠 Delegating to Synthesizer...")
        synthesis_task = f"""Analyze the research findings in research_context.md for: {research_topic}
        
Please identify core themes, patterns, and relationships across the research findings.
Organize the information into coherent frameworks and extract key insights that address
the research question. Resolve any contradictions found in the sources.

Append your synthesis to research_context.md in the Synthesis section."""
        
        synthesizer_result = self.synthesizer.execute_task(synthesis_task)
        self.context.append_section("Synthesis", synthesizer_result)
        
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
        
        # Create output folder if it doesn't exist
        Path(output_folder).mkdir(exist_ok=True)
        
        write_task = f"""Create a comprehensive technical report using all sections from research_context.md for: {research_topic}
        
Please create a polished, professional report with MANDATORY TECHNICAL DEPTH including:
- Executive summary with technical overview
- Detailed methodology section
- Findings with granular technical explanations, code snippets, architectural details
- In-depth analysis with performance metrics and scalability considerations
- Technical implications and future research directions
- Comprehensive references

Save the report in the {output_folder} folder and append it to research_context.md."""
        
        writer_result = self.writer.execute_task(write_task)
        self.context.append_section("Final Report", writer_result)
        
        # Save final report to specified folder
        report_filename = f"{research_topic.replace(' ', '_').lower()}_research_report.md"
        report_path = Path(output_folder) / report_filename
        
        with open(report_path, 'w') as f:
            f.write(f"# Research Report: {research_topic}\n\n")
            f.write(writer_result)
        
        print("✅ Research workflow completed!")
        print(f"📄 Final report saved to: {report_path}")
        print(f"📁 Full research context available in: {self.context.file_path}")
        
        return str(report_path)


def main():
    """Main entry point for the research manager workflow"""
    import argparse
    from dotenv import load_dotenv
    
    load_dotenv()
    
    parser = argparse.ArgumentParser(description="Research Manager Workflow - Claude Code Integration")
    parser.add_argument("topic", help="Research topic to investigate")
    parser.add_argument("--output", "-o", default="reports", help="Output folder for reports")
    parser.add_argument("--model", default="sonnet", help="Claude model to use (sonnet, opus, haiku)")
    parser.add_argument("--perplexity-api-key", help="Perplexity API key (or set PERPLEXITY_API_KEY env var)")
    
    args = parser.parse_args()
    
    # Get Perplexity API key from args or environment
    perplexity_api_key = args.perplexity_api_key or os.getenv("PERPLEXITY_API_KEY")
    if not perplexity_api_key:
        print("⚠️  Warning: No Perplexity API key provided. Research will be limited to Claude's knowledge.")
        print("   Set PERPLEXITY_API_KEY environment variable or use --perplexity-api-key for enhanced research.")
    
    # Initialize and run workflow
    workflow = ResearchManagerWorkflow(model=args.model, perplexity_api_key=perplexity_api_key)
    
    try:
        report_path = workflow.execute_workflow(args.topic, args.output)
        print("\n🎉 Research completed successfully!")
        print(f"📊 Report available at: {report_path}")
        
    except Exception as e:
        print(f"❌ Error during research workflow: {e}")
        raise


if __name__ == "__main__":
    main()