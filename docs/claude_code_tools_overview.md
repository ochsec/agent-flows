# List of Claude Code Built-In Tools

  File Operations:
  - Read - Read file contents
  - Edit - Make single edits to files
  - MultiEdit - Make multiple edits to a single file
  - Write - Write new files or overwrite existing ones
  - LS - List directory contents

  Search & Navigation:
  - Glob - Find files by pattern matching
  - Grep - Search file contents with regex
  - Task - Launch agents for complex searches

  Command Execution:
  - Bash - Execute shell commands with timeout

  Jupyter Notebooks:
  - NotebookRead - Read notebook cells
  - NotebookEdit - Edit notebook cells

  Web & Research:
  - WebFetch - Fetch and analyze web content
  - WebSearch - Search the web

  Planning & Organization:
  - TodoWrite - Create and manage task lists
  - exit_plan_mode - Exit planning mode when ready to code

## File Operation Constraints:

  Read:
  - Requires absolute paths (not relative)
  - Max 2000 lines by default
  - Lines >2000 chars get truncated
  - Must read file before editing it

  Edit/MultiEdit:
  - Must use Read first before any edits
  - old_string must be exact match (including whitespace)
  - old_string must be unique unless using replace_all
  - Preserve exact indentation from file
  - Don't include line number prefixes in strings

  Write:
  - Overwrites existing files completely
  - Must read existing files first
  - Absolute paths required
  - Prefer editing over creating new files

  LS:
  - Absolute paths only (no relative paths)
  - Can use glob patterns to ignore files

  General:
  - Always prefer editing existing files over creating new ones
  - Never create documentation files unless explicitly requested
  - Follow existing code conventions and style
  - No comments unless requested

## Task Tool - In-Depth:

  Purpose:
  Launches independent agents with their own toolset for complex searches and research tasks.

  When to Use:
  - Keyword searches ("find config files", "where is logging implemented")
  - Open-ended searches requiring multiple rounds of globbing/grepping
  - Questions like "which file does X?" or "how is Y implemented?"
  - Complex research that may need several search iterations

  When NOT to Use:
  - Reading specific known file paths (use Read instead)
  - Searching for specific class definitions (use Glob instead)
  - Searching within 2-3 known files (use Read instead)
  - Writing code or running commands (use other tools)
  - Non-search tasks

  Agent Capabilities:
  The launched agent has access to: Bash, Glob, Grep, LS, Read, Edit, MultiEdit, Write, NotebookRead, NotebookEdit, WebFetch, TodoWrite,
  WebSearch, exit_plan_mode

  Key Characteristics:
  - Stateless: Each agent invocation is independent
  - Single response: Agent returns one final message, no back-and-forth
  - Autonomous: Must provide complete task description upfront
  - Parallel execution: Launch multiple agents simultaneously for better performance
  - Trusted results: Agent outputs should generally be trusted

  Best Practices:
  - Provide highly detailed task descriptions
  - Specify exactly what information to return
  - Clearly indicate if it's research-only or includes code writing
  - Use multiple concurrent agents when possible
  - Include specific requirements for the final report format

##  Bash Permissions in Claude Code:

  Default Behavior:
  - Bash commands require explicit user approval by default
  - Each command must be manually approved before execution

  Security Controls:
  - Command blocklist - Blocks risky commands like curl and wget
  - Suspicious command detection - Flags potentially harmful commands even if previously allowed
  - Unmatched commands - Default to requiring manual approval
  - Permission-based architecture - Sensitive operations need explicit approval

  Granularity:
  - Permissions appear to be command-level, not blanket bash access
  - Previously approved commands may not require re-approval
  - System analyzes each command for risk factors

  User Control:
  - Users can review and approve/deny each suggested command
  - Recommended to use VMs for additional isolation
  - Users maintain control over what gets executed

## WebSearch vs WebFetch:

  WebSearch:
  - Searches the web and returns formatted search results
  - Provides up-to-date information beyond Claude's knowledge cutoff
  - Supports domain filtering (allow/block specific sites)
  - Only available in the US
  - Returns search result blocks, not raw content

  WebFetch:
  - Fetches content from specific URLs and processes it with AI
  - Converts HTML to markdown automatically
  - Takes a URL + prompt, returns AI analysis of the content
  - Has 15-minute cache for performance
  - Read-only operation (doesn't modify files)
  - Handles redirects and informs about host changes

  Safety Differences from curl/wget:

  WebFetch Safety Features:
  - AI-mediated processing - Content is analyzed by AI model, not directly executed
  - Structured output - Returns processed analysis, not raw executable content
  - Read-only - Cannot write files or execute downloaded content
  - Built-in validation - Handles redirects safely and validates URLs
  - Content conversion - HTML→markdown conversion reduces risk vectors

  curl/wget Risks:
  - Direct file download - Can download executable files to filesystem
  - Arbitrary execution - Downloaded content could be piped to shell
  - No validation - Raw network requests without safety checks
  - File system access - Direct write capabilities to local files

  Key Difference:
  WebFetch processes and analyzes web content through AI rather than downloading raw files that could be executed or contain malicious code.

##  TodoWrite Tool - In-Depth:

  Purpose:
  Creates and manages structured task lists for tracking progress during coding sessions.

  When to Use:
  - Complex multi-step tasks (3+ steps)
  - Non-trivial/complex tasks requiring planning
  - User explicitly requests todo list
  - Multiple tasks provided by user
  - After receiving new instructions
  - When starting work (mark as in_progress)
  - After completing tasks (mark as completed)

  When NOT to Use:
  - Single straightforward tasks
  - Trivial tasks completable in <3 steps
  - Purely conversational/informational requests
  - Tasks providing no organizational benefit

  Task States:
  - pending - Not yet started
  - in_progress - Currently working (limit to ONE at a time)
  - completed - Finished successfully

  Task Management Rules:
  - Real-time updates - Update status as you work
  - Immediate completion - Mark completed right after finishing
  - One in-progress - Only one task active at a time
  - Complete before starting - Finish current tasks before new ones
  - Remove irrelevant - Delete tasks no longer needed

  Completion Requirements:
  Only mark completed when FULLY accomplished:
  - ❌ Don't mark complete if tests failing
  - ❌ Don't mark complete if implementation partial
  - ❌ Don't mark complete if unresolved errors
  - ❌ Don't mark complete if missing files/dependencies

  Best Practices:
  - Create specific, actionable items
  - Break complex tasks into smaller steps
  - Use clear, descriptive task names
  - Be proactive - demonstrates attentiveness
  - Ensures all requirements completed successfully

## exit_plan_mode Tool:

  Purpose:
  Exits planning mode after presenting an implementation plan to the user.

  When to Use:
  - Only for tasks requiring code implementation planning
  - After finishing your implementation plan
  - When ready to get user approval before coding

  When NOT to Use:
  - Research tasks (searching, reading, understanding codebase)
  - Information gathering
  - File analysis or exploration
  - Any non-coding tasks

  Function:
  - Prompts user to exit plan mode
  - Allows user to approve/modify your plan before execution
  - Transitions from planning to implementation phase

  Key Point:
  Reserved specifically for coding implementation plans, not research or analysis tasks.
