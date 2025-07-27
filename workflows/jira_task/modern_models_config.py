"""
Modern high-parameter models configuration for LM Studio.
These are the state-of-the-art models that actually perform well for code generation.
"""

from typing import List, Dict, Any
from dataclasses import dataclass
from clients.llm_client import WorkflowType, ModelConfig


@dataclass
class ModernLMStudioModels:
    """Modern high-parameter models for serious code generation work."""
    
    # Qwen 2.5 Series - State of the art code models
    QWEN_2_5_CODER_32B = ModelConfig(
        name="qwen2.5-coder:32b-instruct-q4_K_M",
        max_tokens=8192,
        context_window=32768,
        cost_per_1k_tokens=0.0,
        best_for=[WorkflowType.CODE_REVIEW, WorkflowType.JIRA_TASK, WorkflowType.GENERAL],
        description="Qwen 2.5 Coder 32B - State-of-the-art code generation, rivals GPT-4"
    )
    
    QWEN_2_5_CODER_32B_FP16 = ModelConfig(
        name="qwen2.5-coder:32b-instruct-fp16",
        max_tokens=8192,
        context_window=32768,
        cost_per_1k_tokens=0.0,
        best_for=[WorkflowType.CODE_REVIEW, WorkflowType.JIRA_TASK, WorkflowType.GENERAL],
        description="Qwen 2.5 Coder 32B FP16 - Maximum quality, requires 64GB+ VRAM"
    )
    
    QWEN_2_5_CODER_14B = ModelConfig(
        name="qwen2.5-coder:14b-instruct-q4_K_M",
        max_tokens=8192,
        context_window=32768,
        cost_per_1k_tokens=0.0,
        best_for=[WorkflowType.CODE_REVIEW, WorkflowType.JIRA_TASK],
        description="Qwen 2.5 Coder 14B - Excellent balance of performance and quality"
    )
    
    # DeepSeek Coder V2 Series
    DEEPSEEK_CODER_V2_236B = ModelConfig(
        name="deepseek-coder-v2:236b-instruct-q4_K_M",
        max_tokens=8192,
        context_window=128000,
        cost_per_1k_tokens=0.0,
        best_for=[WorkflowType.CODE_REVIEW, WorkflowType.JIRA_TASK],
        description="DeepSeek Coder V2 236B - Massive model with incredible context length"
    )
    
    DEEPSEEK_CODER_V2_16B = ModelConfig(
        name="deepseek-coder-v2:16b-lite-instruct-q8_0",
        max_tokens=8192,
        context_window=32768,
        cost_per_1k_tokens=0.0,
        best_for=[WorkflowType.CODE_REVIEW, WorkflowType.JIRA_TASK],
        description="DeepSeek Coder V2 Lite 16B - Efficient variant with good performance"
    )
    
    # CodeLlama Series (70B variants)
    CODELLAMA_70B = ModelConfig(
        name="codellama:70b-instruct-q4_K_M",
        max_tokens=4096,
        context_window=16384,
        cost_per_1k_tokens=0.0,
        best_for=[WorkflowType.CODE_REVIEW, WorkflowType.JIRA_TASK],
        description="Code Llama 70B - Meta's largest code model"
    )
    
    # Llama 3.1 Series
    LLAMA_3_1_70B = ModelConfig(
        name="llama3.1:70b-instruct-q4_K_M",
        max_tokens=8192,
        context_window=131072,
        cost_per_1k_tokens=0.0,
        best_for=[WorkflowType.GENERAL, WorkflowType.RESEARCH, WorkflowType.CODE_REVIEW],
        description="Llama 3.1 70B - Excellent general purpose with huge context"
    )
    
    LLAMA_3_1_405B = ModelConfig(
        name="llama3.1:405b-instruct-q4_K_M",
        max_tokens=8192,
        context_window=131072,
        cost_per_1k_tokens=0.0,
        best_for=[WorkflowType.GENERAL, WorkflowType.RESEARCH, WorkflowType.CODE_REVIEW],
        description="Llama 3.1 405B - Meta's flagship model, requires massive resources"
    )
    
    # Mixtral/Mistral Large Series
    MIXTRAL_8X22B = ModelConfig(
        name="mixtral:8x22b-instruct-v0.1-q4_K_M",
        max_tokens=8192,
        context_window=65536,
        cost_per_1k_tokens=0.0,
        best_for=[WorkflowType.GENERAL, WorkflowType.RESEARCH, WorkflowType.CODE_REVIEW],
        description="Mixtral 8x22B - Mixture of experts, 141B parameters"
    )
    
    MISTRAL_LARGE_2 = ModelConfig(
        name="mistral-large:123b-instruct-2407-q4_K_M",
        max_tokens=8192,
        context_window=131072,
        cost_per_1k_tokens=0.0,
        best_for=[WorkflowType.GENERAL, WorkflowType.RESEARCH, WorkflowType.CODE_REVIEW],
        description="Mistral Large 2 123B - Latest from Mistral AI"
    )
    
    # Starcoder 2 Series
    STARCODER2_15B = ModelConfig(
        name="starcoder2:15b-instruct-v0.1",
        max_tokens=8192,
        context_window=16384,
        cost_per_1k_tokens=0.0,
        best_for=[WorkflowType.CODE_REVIEW, WorkflowType.JIRA_TASK],
        description="StarCoder 2 15B - Specialized for code completion"
    )
    
    # Command R Series
    COMMAND_R_PLUS = ModelConfig(
        name="command-r-plus:104b-q4_K_M",
        max_tokens=8192,
        context_window=131072,
        cost_per_1k_tokens=0.0,
        best_for=[WorkflowType.RESEARCH, WorkflowType.GENERAL],
        description="Command R+ 104B - Cohere's flagship with huge context"
    )
    
    # Yi Coder Series
    YI_CODER_9B = ModelConfig(
        name="yi-coder:9b-instruct",
        max_tokens=8192,
        context_window=128000,
        cost_per_1k_tokens=0.0,
        best_for=[WorkflowType.CODE_REVIEW, WorkflowType.JIRA_TASK],
        description="Yi Coder 9B - Efficient code model with huge context"
    )
    
    @classmethod
    def get_recommended_for_coding(cls) -> List[ModelConfig]:
        """Get the best models for coding tasks, ordered by preference."""
        return [
            cls.QWEN_2_5_CODER_32B,        # Best overall for code
            cls.DEEPSEEK_CODER_V2_16B,     # Great alternative
            cls.QWEN_2_5_CODER_14B,        # Faster option
            cls.CODELLAMA_70B,             # Classic choice
            cls.YI_CODER_9B,               # Efficient with huge context
        ]
    
    @classmethod
    def get_recommended_by_vram(cls, vram_gb: int) -> List[ModelConfig]:
        """Get recommended models based on available VRAM."""
        if vram_gb >= 80:  # A100 80GB or better
            return [
                cls.QWEN_2_5_CODER_32B_FP16,
                cls.DEEPSEEK_CODER_V2_236B,
                cls.LLAMA_3_1_405B,
                cls.MIXTRAL_8X22B,
            ]
        elif vram_gb >= 48:  # RTX 4090/A6000
            return [
                cls.QWEN_2_5_CODER_32B,
                cls.CODELLAMA_70B,
                cls.LLAMA_3_1_70B,
                cls.MISTRAL_LARGE_2,
            ]
        elif vram_gb >= 24:  # RTX 3090/4090
            return [
                cls.QWEN_2_5_CODER_14B,
                cls.DEEPSEEK_CODER_V2_16B,
                cls.STARCODER2_15B,
                cls.YI_CODER_9B,
            ]
        else:  # Less than 24GB
            return [
                cls.YI_CODER_9B,
                cls.STARCODER2_15B,
                # You might need to use smaller quantization
            ]
    
    @classmethod
    def get_model_requirements(cls, model: ModelConfig) -> Dict[str, Any]:
        """Get hardware requirements for a model."""
        requirements = {
            cls.QWEN_2_5_CODER_32B.name: {"min_vram_gb": 24, "recommended_vram_gb": 48, "min_ram_gb": 64},
            cls.QWEN_2_5_CODER_32B_FP16.name: {"min_vram_gb": 64, "recommended_vram_gb": 80, "min_ram_gb": 128},
            cls.QWEN_2_5_CODER_14B.name: {"min_vram_gb": 16, "recommended_vram_gb": 24, "min_ram_gb": 32},
            cls.DEEPSEEK_CODER_V2_236B.name: {"min_vram_gb": 80, "recommended_vram_gb": 160, "min_ram_gb": 256},
            cls.DEEPSEEK_CODER_V2_16B.name: {"min_vram_gb": 16, "recommended_vram_gb": 24, "min_ram_gb": 32},
            cls.CODELLAMA_70B.name: {"min_vram_gb": 40, "recommended_vram_gb": 48, "min_ram_gb": 64},
            cls.LLAMA_3_1_70B.name: {"min_vram_gb": 40, "recommended_vram_gb": 48, "min_ram_gb": 64},
            cls.LLAMA_3_1_405B.name: {"min_vram_gb": 160, "recommended_vram_gb": 320, "min_ram_gb": 512},
            cls.MIXTRAL_8X22B.name: {"min_vram_gb": 80, "recommended_vram_gb": 96, "min_ram_gb": 128},
            cls.MISTRAL_LARGE_2.name: {"min_vram_gb": 64, "recommended_vram_gb": 80, "min_ram_gb": 128},
            cls.STARCODER2_15B.name: {"min_vram_gb": 16, "recommended_vram_gb": 24, "min_ram_gb": 32},
            cls.COMMAND_R_PLUS.name: {"min_vram_gb": 64, "recommended_vram_gb": 80, "min_ram_gb": 128},
            cls.YI_CODER_9B.name: {"min_vram_gb": 12, "recommended_vram_gb": 16, "min_ram_gb": 24},
        }
        return requirements.get(model.name, {"min_vram_gb": 16, "recommended_vram_gb": 24, "min_ram_gb": 32})