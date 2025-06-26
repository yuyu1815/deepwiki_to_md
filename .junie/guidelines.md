# Project Development Guidelines (Revised Edition)

**Important Note on Code Generation: When generating code based on the following guidelines, all comments and function
descriptions (such as JSDoc) must be written in Japanese. The code itself (including variable names and function names)
must be written in English.**

## Purpose and Role

These guidelines provide a comprehensive framework to support the development of highly maintainable software.

**Role of the AI Assistant:**

* Offer concrete suggestions for improvement during code reviews based on these guidelines
* Recommend appropriate design and implementation patterns during new development
* Detect guideline deviations and suggest alternatives
* Adjust priorities according to the project's maturity level

## Implementation Instructions (Important)

### 🔥 Highest Priority: Code Execution Procedure

**When modifying existing code:**
For modifications, updates, or refactoring of existing code, please execute the following command:

```
bash
gemini --prompt "Instruction content"
```

**Example:**

```
bash
gemini --prompt "Rename the function fetchData to a more descriptive name fetchUserProfile, and add JSDoc comments in Japanese."
```

**⚠️ Important Reminder:**
After executing the command, verify that the intended changes have been applied correctly.

**✅ Obligation:**  
If you are later instructed to use gemini, you must execute the gemini command.

## Core Principles \[Required]

Please refer to *GEMINI.md* within the same project.

**Examples of gemini command usage:**

```
bash
# Improve function naming
gemini --prompt "Rename the function fetchData to a more descriptive name fetchUserProfile, and add JSDoc comments in Japanese."

# Add error handling
gemini --prompt "Add comprehensive error handling to this API call section, including log output and user-friendly error messages."

# Address violation of the Single Responsibility Principle
gemini --prompt "This function currently has multiple responsibilities. Please split it appropriately in accordance with the Single Responsibility Principle."
```



