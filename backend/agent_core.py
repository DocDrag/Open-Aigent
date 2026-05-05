import re
import json
from llm_gateway import OllamaClient
from tools_fs import TOOLS
import datetime


SYSTEM_PROMPT = """You are an AI Software Engineer Agent.
You interact with the filesystem using Tags.

AVAILABLE TOOLS:
1. list_files(path="."): Lists files and directories.
2. read_file(path="file.py"): Reads file content.
3. write_file(path="file.py", content="..."): Creates or overwrites a file.
4. web_search(query="search term"): Searches the internet for information.
   - TIP: Use clean, simple keywords. Do NOT include trailing symbols like ">" or extra quotes.
   - TIP: If you are in a future year (like 2026), avoid adding the year to the search query unless looking for historical data, as it may not exist yet on the web.
5. read_url(url="https://..."): Reads the text content of a specific webpage.

IMPORTANT: You MUST use a `<call>` tag whenever you decide to take an action. Never just describe what you will do without calling a tool.




To take an action, use this format:
<thought>Your reasoning here</thought>
<call tool="tool_name">
  <arg name="path">value</arg>
  <content>Raw content here</content>
</call>

IMPORTANT RULES:
1. Output ONLY ONE <call> per response.
2. NEVER output <status>completed</status> in the same response as a <call>.
3. ARGUMENT VALUES: Put the raw value inside the tag. NEVER use quotes around the value. 
   - Correct: <arg name="path">file_name.py</arg>
   - Incorrect: <arg name="path">"file_name.py"</arg>
4. Wait for the tool result before proceeding.
5. When ALL tasks are finished, use: <thought>Summary</thought><status>completed</status>
"""

class Agent:
    def __init__(self, model="llama3", ollama_url=None):
        self.client = OllamaClient(model_name=model, base_url=ollama_url)

    def run_task_full_loop(self, task_description: str, history=None, objective: str = None):
        if history is None:
            history = []
        
        # If no objective provided, the current task is the objective
        main_objective = objective if objective else task_description
        current_history = list(history)
        max_steps = 20
        
        for step in range(max_steps):
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # Construct a clear prompt that preserves the main goal
            current_prompt = f"CURRENT DATE/TIME: {current_time}\n"
            current_prompt += f"MAIN OBJECTIVE: {main_objective}\n"

            
            if task_description and task_description != main_objective:
                current_prompt += f"LATEST USER INPUT: {task_description}\n"
            
            if current_history:
                current_prompt += "\nACTIONS HISTORY:\n" + "\n".join(current_history)
            
            current_prompt += "\n\nDecide the next action based on the MAIN OBJECTIVE."

            
            full_response = ""
            yield {"status": "thinking", "chunk": "", "step": step + 1}
            
            try:
                for chunk in self.client.chat_stream(current_prompt, system_prompt=SYSTEM_PROMPT):
                    full_response += chunk
                    yield {"status": "token", "chunk": chunk}

                thought = self._get_tag(full_response, "thought", "Processing...")
                
                # PRIORITY 1: Check for tool calls first
                tool_match = re.search(r'<call tool="(.*?)">', full_response)
                if tool_match:
                    tool_name = tool_match.group(1)
                    args = {}
                    for m in re.finditer(r'<arg name="(.*?)">(.*?)</arg>', full_response, re.DOTALL):
                        args[m.group(1)] = m.group(2).strip()
                    
                    content_match = re.search(r'<content>(.*?)</content>', full_response, re.DOTALL)
                    if content_match:
                        args["content"] = content_match.group(1).strip()

                    if tool_name == "write_file":
                        yield {
                            "status": "pending_approval",
                            "thought": thought,
                            "tool": tool_name,
                            "args": args
                        }
                        return

                    if tool_name in TOOLS:
                        yield {"status": "acting", "thought": thought, "tool": tool_name}
                        result = TOOLS[tool_name](**args)
                        current_history.append(f"Step {step+1}: {tool_name}({', '.join(f'{k}={v[:30]}' for k,v in args.items())})")
                        current_history.append(f"Observation: {result}")
                        yield {"status": "step_result", "tool": tool_name, "result": result}
                        continue # Look for more steps
                    else:
                        yield {"status": "error", "message": f"Unknown tool: {tool_name}"}
                        return

                # PRIORITY 2: Only then check for completion
                status_tag = self._get_tag(full_response, "status")
                if status_tag == "completed":
                    yield {"status": "completed", "thought": thought}
                    return
                
                # If no tool and no status, assume it's just chatting or finished
                yield {"status": "completed", "thought": thought}
                return

            except Exception as e:
                yield {"status": "error", "message": f"Agent Error: {str(e)}"}
                return

    def _get_tag(self, text, tag_name, default=""):
        match = re.search(f'<{tag_name}>(.*?)</{tag_name}>', text, re.DOTALL)
        return match.group(1).strip() if match else default
