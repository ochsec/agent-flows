"""
Model recommendations for systems with 128GB unified memory (Apple Silicon).
You can run the absolute best models without any compromises.
"""

from typing import List
from clients.llm_client import WorkflowType, ModelConfig
from .modern_models_config import ModernLMStudioModels


class UnifiedMemoryModelRecommendations:
    """Best models to run with 128GB unified memory - no compromises needed."""
    
    @classmethod
    def get_top_tier_models(cls) -> List[ModelConfig]:
        """Get the absolute best models you should be running."""
        return [
            # Primary recommendation - best overall
            ModernLMStudioModels.QWEN_2_5_CODER_32B_FP16,  # Full precision for maximum quality
            
            # Alternatives for specific use cases
            ModernLMStudioModels.DEEPSEEK_CODER_V2_236B,   # If you want the biggest model
            ModernLMStudioModels.LLAMA_3_1_405B,           # Meta's flagship
            ModernLMStudioModels.MIXTRAL_8X22B,            # Fast MoE architecture
            ModernLMStudioModels.MISTRAL_LARGE_2,          # Great for general tasks
            ModernLMStudioModels.CODELLAMA_70B,            # Classic choice for code
            ModernLMStudioModels.COMMAND_R_PLUS,           # Huge context window (128K)
        ]
    
    @classmethod
    def get_recommended_setup(cls) -> dict:
        """Get the recommended model setup for 128GB unified memory."""
        return {
            "primary_model": "qwen2.5-coder:32b-instruct-fp16",
            "fast_model": "qwen2.5-coder:14b-instruct-q8_0",  # For quick iterations
            "massive_context": "command-r-plus:104b-q5_K_M",   # 128K context
            "experimental": "deepseek-coder-v2:236b-instruct-q4_K_M",  # Just because you can
            
            "quantization_notes": {
                "fp16": "Use for primary models - best quality",
                "q8_0": "Nearly lossless, good for secondary models",
                "q5_K_M": "Good balance for very large models",
                "q4_K_M": "Only for 200B+ models if needed"
            }
        }
    
    @classmethod
    def get_workflow_optimized(cls, workflow_type: WorkflowType) -> ModelConfig:
        """Get the best model for your workflow with no constraints."""
        if workflow_type == WorkflowType.JIRA_TASK or workflow_type == WorkflowType.CODE_REVIEW:
            return ModernLMStudioModels.QWEN_2_5_CODER_32B_FP16
        elif workflow_type == WorkflowType.RESEARCH:
            return ModernLMStudioModels.COMMAND_R_PLUS  # 128K context
        else:
            return ModernLMStudioModels.LLAMA_3_1_70B  # Great general purpose


# Quick access commands for 128GB unified memory
POWER_USER_COMMANDS = """
# For maximum quality code generation (use this as default)
python -m workflows.jira_task.task_executor_lmstudio \\
  "YOUR_TASK" \\
  --model "qwen2.5-coder:32b-instruct-fp16"

# For massive context tasks (128K tokens)
python -m workflows.jira_task.task_executor_lmstudio \\
  "YOUR_TASK" \\
  --model "command-r-plus:104b-q5_K_M"

# Just because you can - DeepSeek 236B
python -m workflows.jira_task.task_executor_lmstudio \\
  "YOUR_TASK" \\
  --model "deepseek-coder-v2:236b-instruct-q4_K_M"
"""