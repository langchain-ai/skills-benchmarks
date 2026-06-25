Skills are reusable agent capabilities that provide specialized workflows and domain knowledge. They use **progressive disclosure**: agents only load skill content when it's relevant to the task.

**How it works:**
1. **Match**: Agent sees skill descriptions in system prompt
2. **Read**: If relevant, agent reads full SKILL.md using read_file
3. **Execute**: Agent follows instructions and accesses supporting files
