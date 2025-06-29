import loguru
import json
import os
from openai import OpenAI
import time
from langchain_community.tools import ShellTool
from langchain_experimental.utilities import PythonREPL
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langchain.agents import AgentExecutor, create_react_agent, Tool
from langchain import hub
from dotenv import load_dotenv
import warnings
import subprocess
import shlex

load_dotenv()
warnings.filterwarnings("ignore")

# OpenRouter Configuration
OPENROUTER_API_KEY = os.getenv("OPENAI_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
MODEL_NAME = "openai/gpt-4o-mini-2024-07-18"

# OpenRouter headers as per official docs
OPENROUTER_HEADERS = {
    "HTTP-Referer": "http://localhost:3000",
    "X-Title": "Moktashif_AI"
}

class DiscoveryAgent:
    def __init__(self, initial_prompt):
        self.Agent = OpenAI(
            base_url=OPENROUTER_BASE_URL,
            api_key=OPENROUTER_API_KEY
        )
        self.system_prompt = initial_prompt

    def discover_website(self, user_msg):
        try:
            agent_result = self.Agent.chat.completions.create(
                extra_headers=OPENROUTER_HEADERS,
                model=MODEL_NAME,
                messages=[
                    {
                        "role": "system",
                        "content": f"{self.system_prompt}"
                    },
                    {
                        "role": "user",
                        "content": f"{user_msg}"
                    }
                ]
            )
            return agent_result.choices[0].message.content.replace("```json", "").replace("```", "")
        except Exception as e:
            print(f"Error in discover_website: {str(e)}")
            raise


class PlannerAgent:
    def __init__(self, initial_prompt):
        self.Agent = OpenAI(
            base_url=OPENROUTER_BASE_URL,
            api_key=OPENROUTER_API_KEY
        )
        self.system_prompt = initial_prompt

    def plan_decision_tree_for_website(self, user_msg):
        try:
            agent_result = self.Agent.chat.completions.create(
                extra_headers=OPENROUTER_HEADERS,
                model=MODEL_NAME,
                messages=[
                    {
                        "role": "system",
                        "content": f"{self.system_prompt}"
                    },
                    {
                        "role": "user",
                        "content": f"{user_msg}"
                    }
                ]
            )
            return agent_result.choices[0].message.content.replace("```json", "").replace("```", "")
        except Exception as e:
            print(f"Error in plan_decision_tree: {str(e)}")
            raise


class ImprovedShellTool:
    """Improved shell tool with better command handling and error checking"""
    
    def __init__(self):
        self.name = "terminal"
        self.description = "Execute shell commands with improved error handling"
    
    def _check_dependencies(self):
        """Check if required tools are installed"""
        required_tools = ['curl', 'jq', 'nc', 'nmap', 'sqlmap']
        missing_tools = []
        
        for tool in required_tools:
            try:
                subprocess.run(['which', tool], check=True, capture_output=True)
            except subprocess.CalledProcessError:
                missing_tools.append(tool)
        
        if missing_tools:
            install_cmd = f"sudo apt-get update && sudo apt-get install -y {' '.join(missing_tools)}"
            print(f"Missing tools detected: {missing_tools}")
            print(f"Run: {install_cmd}")
            return False
        return True
    
    def run(self, command):
        """Execute shell command with proper error handling"""
        try:
            # Check dependencies first
            if not self._check_dependencies():
                return "Error: Missing required tools. Please install them first."
            
            # Handle special cases for problematic commands
            if 'echo -e' in command and 'nc' in command:
                # Fix netcat HTTP request formatting
                command = command.replace('echo -e', 'printf')
                command = command.replace('\\r\\n', '\r\n')
            
            # Use shlex for proper command parsing
            if '|' in command:
                # Handle pipes specially
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
            else:
                # Use shlex for single commands
                args = shlex.split(command)
                result = subprocess.run(
                    args,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
            
            output = f"Command: {command}\n"
            if result.stdout:
                output += f"STDOUT:\n{result.stdout}\n"
            if result.stderr:
                output += f"STDERR:\n{result.stderr}\n"
            output += f"Return code: {result.returncode}"
            
            return output
            
        except subprocess.TimeoutExpired:
            return f"Command timed out: {command}"
        except Exception as e:
            return f"Error executing command '{command}': {str(e)}"


class DecisionTreeTracker:
    """Track progress through the decision tree"""
    
    def __init__(self):
        self.current_task_id = "1"
        self.completed_tasks = []
        self.decision_tree = {}
        self.task_results = {}
    
    def load_decision_tree(self, tree_json):
        """Load decision tree from JSON"""
        try:
            if isinstance(tree_json, str):
                self.decision_tree = json.loads(tree_json)
            else:
                self.decision_tree = tree_json
        except json.JSONDecodeError as e:
            print(f"Error parsing decision tree: {e}")
            return False
        return True
    
    def get_current_task(self):
        """Get the current task to execute"""
        if not self.decision_tree:
            return None
        
        tasks = self.decision_tree.get("target_functionality", {}).get("testing_plan", {}).get("tasks", [])
        for task in tasks:
            if task["id"] == self.current_task_id:
                return task
        return None
    
    def complete_task(self, task_id, result, success=True):
        """Mark task as completed and determine next task"""
        self.completed_tasks.append(task_id)
        self.task_results[task_id] = {"result": result, "success": success}
        
        # Find current task
        current_task = self.get_current_task()
        if not current_task:
            return None
        
        # Determine next task based on success/failure
        next_steps = current_task.get("next_steps", {})
        if success and "if_successful" in next_steps:
            next_tasks = next_steps["if_successful"]
        elif not success and "if_failed" in next_steps:
            next_tasks = next_steps["if_failed"]
        else:
            next_tasks = next_steps.get("if_inconclusive", [])
        
        if next_tasks:
            self.current_task_id = next_tasks[0]
            return self.current_task_id
        
        return None  # No more tasks
    
    def is_finished(self):
        """Check if all tasks are completed"""
        return self.get_current_task() is None


class ExploitAgent:
    def __init__(self, initial_prompt):
        self.Agent = ChatOpenAI(
            model=MODEL_NAME,
            temperature=0,
            openai_api_key=OPENROUTER_API_KEY,
            openai_api_base=OPENROUTER_BASE_URL,
            extra_headers=OPENROUTER_HEADERS
        )
        
        self.shell_tool = ImprovedShellTool()
        self.python_repl = PythonREPL()
        self.decision_tracker = DecisionTreeTracker()
        
        # Create tools list
        self.repl_tool = Tool(
            name="python_repl",
            description="A Python shell. Use this to execute python commands. Input should be a valid python command. If you want to see the output of a value, you should print it out with `print(...)`.",
            func=self.python_repl.run,
        )
        
        self.shell_tool_wrapped = Tool(
            name="terminal",
            description="Execute shell commands with improved error handling and dependency checking",
            func=self.shell_tool.run,
        )
        
        self.tools_list = [self.shell_tool_wrapped, self.repl_tool]
        
        # Create custom prompt for better decision tree following
        self.custom_prompt = f"""
{initial_prompt}

IMPORTANT DECISION TREE EXECUTION RULES:
1. You MUST follow the decision tree step by step
2. Execute only ONE task at a time
3. Evaluate the success/failure of each task
4. Move to the next task based on the decision tree logic
5. If a tool is missing, try alternative approaches or report the issue
6. Do NOT repeat the same task multiple times
7. Keep track of your progress through the decision tree

Current format:
Question: [decision tree JSON]
Thought: [analyze current situation and determine next step]
Action: [tool to use]
Action Input: [command to execute]
Observation: [result of the action]
... (continue until decision tree is complete)
Final Answer: [vulnerability report in the specified format]
"""
        
        self.prompt = hub.pull("hwchase17/react")
        self.prompt.template = self.custom_prompt
        
        self.shell_agent = create_react_agent(
            llm=self.Agent,
            tools=self.tools_list,
            prompt=self.prompt
        )
        
        self.agent_executor = AgentExecutor(
            agent=self.shell_agent,
            tools=self.tools_list,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=10,  # Limit iterations to prevent infinite loops
            early_stopping_method="force"  # Changed from "generate" to "force"
        )

    @tool
    def chatbot_response(self, input):
        """Use Chatbot to think how to evaluate what you have so far."""
        response = self.Agent.invoke(input)
        return response.content

    def exploit_agent_for_website(self, user_msg):
        """Execute the decision tree with improved tracking and error handling"""
        try:
            # Parse the decision tree from the user message
            if "Tree:" in user_msg:
                tree_part = user_msg.split("Tree:")[1].split("You need to")[0].strip()
                if self.decision_tracker.load_decision_tree(tree_part):
                    print(f"Decision tree loaded successfully")
                else:
                    return "Error: Could not parse decision tree"
            
            # Add decision tree context to the prompt
            enhanced_prompt = f"""
{user_msg}

DECISION TREE EXECUTION STATUS:
Current Task ID: {self.decision_tracker.current_task_id}
Completed Tasks: {self.decision_tracker.completed_tasks}

EXECUTION INSTRUCTIONS:
1. Follow the decision tree systematically
2. Execute the current task: {self.decision_tracker.current_task_id}
3. Evaluate success/failure based on the task criteria
4. Move to the next task according to the decision tree logic
5. If you encounter missing tools, try alternatives or report the issue
6. Generate the final vulnerability report when the decision tree is complete

Remember: Execute commands one at a time and evaluate results before proceeding.
"""
            
            # Run the agent with the enhanced prompt
            response = self.agent_executor.invoke({"input": enhanced_prompt})
            return response['output']
            
        except Exception as e:
            error_msg = f"Error in exploit agent execution: {str(e)}"
            print(error_msg)
            return error_msg
