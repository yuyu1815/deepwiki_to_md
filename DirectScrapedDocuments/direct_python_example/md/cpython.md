Overview
========

Relevant source files

The following files were used as context for generating this wiki page:

* [Doc/library/gc.rst](https://github.com/python/cpython/blob/ea23c897/Doc/library/gc.rst)
* [Doc/library/sys.rst](https://github.com/python/cpython/blob/ea23c897/Doc/library/sys.rst)
* [Include/cpython/code.h](https://github.com/python/cpython/blob/ea23c897/Include/cpython/code.h)
* [Include/cpython/object.h](https://github.com/python/cpython/blob/ea23c897/Include/cpython/object.h)
* [Include/cpython/pystate.h](https://github.com/python/cpython/blob/ea23c897/Include/cpython/pystate.h)
* [Include/internal/pycore\_ceval.h](https://github.com/python/cpython/blob/ea23c897/Include/internal/pycore_ceval.h)
* [Include/internal/pycore\_ceval\_state.h](https://github.com/python/cpython/blob/ea23c897/Include/internal/pycore_ceval_state.h)
* [Include/internal/pycore\_compile.h](https://github.com/python/cpython/blob/ea23c897/Include/internal/pycore_compile.h)
* [Include/internal/pycore\_dict.h](https://github.com/python/cpython/blob/ea23c897/Include/internal/pycore_dict.h)
* [Include/internal/pycore\_flowgraph.h](https://github.com/python/cpython/blob/ea23c897/Include/internal/pycore_flowgraph.h)
* [Include/internal/pycore\_gc.h](https://github.com/python/cpython/blob/ea23c897/Include/internal/pycore_gc.h)
* [Include/internal/pycore\_instruments.h](https://github.com/python/cpython/blob/ea23c897/Include/internal/pycore_instruments.h)
* [Include/internal/pycore\_interp.h](https://github.com/python/cpython/blob/ea23c897/Include/internal/pycore_interp.h)
* [Include/internal/pycore\_magic\_number.h](https://github.com/python/cpython/blob/ea23c897/Include/internal/pycore_magic_number.h)
* [Include/internal/pycore\_object.h](https://github.com/python/cpython/blob/ea23c897/Include/internal/pycore_object.h)
* [Include/internal/pycore\_opcode\_metadata.h](https://github.com/python/cpython/blob/ea23c897/Include/internal/pycore_opcode_metadata.h)
* [Include/internal/pycore\_optimizer.h](https://github.com/python/cpython/blob/ea23c897/Include/internal/pycore_optimizer.h)
* [Include/internal/pycore\_pystate.h](https://github.com/python/cpython/blob/ea23c897/Include/internal/pycore_pystate.h)
* [Include/internal/pycore\_runtime.h](https://github.com/python/cpython/blob/ea23c897/Include/internal/pycore_runtime.h)
* [Include/internal/pycore\_runtime\_init.h](https://github.com/python/cpython/blob/ea23c897/Include/internal/pycore_runtime_init.h)
* [Include/internal/pycore\_signal.h](https://github.com/python/cpython/blob/ea23c897/Include/internal/pycore_signal.h)
* [Include/internal/pycore\_symtable.h](https://github.com/python/cpython/blob/ea23c897/Include/internal/pycore_symtable.h)
* [Include/internal/pycore\_tstate.h](https://github.com/python/cpython/blob/ea23c897/Include/internal/pycore_tstate.h)
* [Include/internal/pycore\_typeobject.h](https://github.com/python/cpython/blob/ea23c897/Include/internal/pycore_typeobject.h)
* [Include/internal/pycore\_uop\_ids.h](https://github.com/python/cpython/blob/ea23c897/Include/internal/pycore_uop_ids.h)
* [Include/internal/pycore\_uop\_metadata.h](https://github.com/python/cpython/blob/ea23c897/Include/internal/pycore_uop_metadata.h)
* [Include/intrcheck.h](https://github.com/python/cpython/blob/ea23c897/Include/intrcheck.h)
* [Lib/test/test\_capi/test\_opt.py](https://github.com/python/cpython/blob/ea23c897/Lib/test/test_capi/test_opt.py)
* [Lib/test/test\_compile.py](https://github.com/python/cpython/blob/ea23c897/Lib/test/test_compile.py)
* [Lib/test/test\_dictcomps.py](https://github.com/python/cpython/blob/ea23c897/Lib/test/test_dictcomps.py)
* [Lib/test/test\_gc.py](https://github.com/python/cpython/blob/ea23c897/Lib/test/test_gc.py)
* [Lib/test/test\_generated\_cases.py](https://github.com/python/cpython/blob/ea23c897/Lib/test/test_generated_cases.py)
* [Lib/test/test\_iter.py](https://github.com/python/cpython/blob/ea23c897/Lib/test/test_iter.py)
* [Lib/test/test\_listcomps.py](https://github.com/python/cpython/blob/ea23c897/Lib/test/test_listcomps.py)
* [Lib/test/test\_monitoring.py](https://github.com/python/cpython/blob/ea23c897/Lib/test/test_monitoring.py)
* [Lib/test/test\_peepholer.py](https://github.com/python/cpython/blob/ea23c897/Lib/test/test_peepholer.py)
* [Lib/test/test\_setcomps.py](https://github.com/python/cpython/blob/ea23c897/Lib/test/test_setcomps.py)
* [Lib/test/test\_structseq.py](https://github.com/python/cpython/blob/ea23c897/Lib/test/test_structseq.py)
* [Lib/test/test\_sys.py](https://github.com/python/cpython/blob/ea23c897/Lib/test/test_sys.py)
* [Modules/clinic/gcmodule.c.h](https://github.com/python/cpython/blob/ea23c897/Modules/clinic/gcmodule.c.h)
* [Modules/gcmodule.c](https://github.com/python/cpython/blob/ea23c897/Modules/gcmodule.c)
* [Modules/signalmodule.c](https://github.com/python/cpython/blob/ea23c897/Modules/signalmodule.c)
* [Objects/dictobject.c](https://github.com/python/cpython/blob/ea23c897/Objects/dictobject.c)
* [Objects/object.c](https://github.com/python/cpython/blob/ea23c897/Objects/object.c)
* [Objects/structseq.c](https://github.com/python/cpython/blob/ea23c897/Objects/structseq.c)
* [Objects/typeobject.c](https://github.com/python/cpython/blob/ea23c897/Objects/typeobject.c)
* [Python/assemble.c](https://github.com/python/cpython/blob/ea23c897/Python/assemble.c)
* [Python/bytecodes.c](https://github.com/python/cpython/blob/ea23c897/Python/bytecodes.c)
* [Python/ceval.c](https://github.com/python/cpython/blob/ea23c897/Python/ceval.c)
* [Python/ceval\_gil.c](https://github.com/python/cpython/blob/ea23c897/Python/ceval_gil.c)
* [Python/ceval\_macros.h](https://github.com/python/cpython/blob/ea23c897/Python/ceval_macros.h)
* [Python/clinic/sysmodule.c.h](https://github.com/python/cpython/blob/ea23c897/Python/clinic/sysmodule.c.h)
* [Python/codegen.c](https://github.com/python/cpython/blob/ea23c897/Python/codegen.c)
* [Python/compile.c](https://github.com/python/cpython/blob/ea23c897/Python/compile.c)
* [Python/executor\_cases.c.h](https://github.com/python/cpython/blob/ea23c897/Python/executor_cases.c.h)
* [Python/flowgraph.c](https://github.com/python/cpython/blob/ea23c897/Python/flowgraph.c)
* [Python/gc.c](https://github.com/python/cpython/blob/ea23c897/Python/gc.c)
* [Python/gc\_free\_threading.c](https://github.com/python/cpython/blob/ea23c897/Python/gc_free_threading.c)
* [Python/generated\_cases.c.h](https://github.com/python/cpython/blob/ea23c897/Python/generated_cases.c.h)
* [Python/instrumentation.c](https://github.com/python/cpython/blob/ea23c897/Python/instrumentation.c)
* [Python/optimizer.c](https://github.com/python/cpython/blob/ea23c897/Python/optimizer.c)
* [Python/optimizer\_analysis.c](https://github.com/python/cpython/blob/ea23c897/Python/optimizer_analysis.c)
* [Python/optimizer\_bytecodes.c](https://github.com/python/cpython/blob/ea23c897/Python/optimizer_bytecodes.c)
* [Python/optimizer\_cases.c.h](https://github.com/python/cpython/blob/ea23c897/Python/optimizer_cases.c.h)
* [Python/optimizer\_symbols.c](https://github.com/python/cpython/blob/ea23c897/Python/optimizer_symbols.c)
* [Python/pylifecycle.c](https://github.com/python/cpython/blob/ea23c897/Python/pylifecycle.c)
* [Python/pystate.c](https://github.com/python/cpython/blob/ea23c897/Python/pystate.c)
* [Python/symtable.c](https://github.com/python/cpython/blob/ea23c897/Python/symtable.c)
* [Python/sysmodule.c](https://github.com/python/cpython/blob/ea23c897/Python/sysmodule.c)
* [Tools/cases\_generator/analyzer.py](https://github.com/python/cpython/blob/ea23c897/Tools/cases_generator/analyzer.py)
* [Tools/cases\_generator/generators\_common.py](https://github.com/python/cpython/blob/ea23c897/Tools/cases_generator/generators_common.py)
* [Tools/cases\_generator/optimizer\_generator.py](https://github.com/python/cpython/blob/ea23c897/Tools/cases_generator/optimizer_generator.py)
* [Tools/cases\_generator/stack.py](https://github.com/python/cpython/blob/ea23c897/Tools/cases_generator/stack.py)
* [Tools/cases\_generator/tier1\_generator.py](https://github.com/python/cpython/blob/ea23c897/Tools/cases_generator/tier1_generator.py)
* [Tools/cases\_generator/tier2\_generator.py](https://github.com/python/cpython/blob/ea23c897/Tools/cases_generator/tier2_generator.py)

This document provides a high-level overview of the CPython codebase, explaining its architecture, main components, and execution flow. CPython is the reference implementation of the Python programming language, written primarily in C. This overview helps developers understand how different parts of the interpreter work together to execute Python code.

CPython Architecture
--------------------

CPython is organized into several major subsystems that work together to parse, compile, and execute Python code. The following diagram illustrates the high-level architecture:

Sources: [Python/bytecodes.c1-33](https://github.com/python/cpython/blob/ea23c897/Python/bytecodes.c#L1-L33)(line numbers), [Python/ceval.c1-50](https://github.com/python/cpython/blob/ea23c897/Python/ceval.c#L1-L50) [Objects/object.c1-30](https://github.com/python/cpython/blob/ea23c897/Objects/object.c#L1-L30) [Python/pystate.c52-70](https://github.com/python/cpython/blob/ea23c897/Python/pystate.c#L52-L70) [Python/compile.c1-15](https://github.com/python/cpython/blob/ea23c897/Python/compile.c#L1-L15)

Execution Pipeline
------------------

Python code goes through several stages from source text to execution. Understanding this pipeline is fundamental to comprehending how Python works under the hood.

When you run a Python program, the code follows this path:

1. **Parsing**: Source code is parsed into an Abstract Syntax Tree (AST)
2. **Compilation**: The AST is analyzed to create symbol tables and then compiled into bytecode
3. **Execution**: The bytecode is executed by the interpreter, which has two tiers:
   * **Tier 1**: Direct bytecode interpretation with specialized variants
   * **Tier 2**: Trace-based optimizer that converts bytecode to micro-operations for faster execution

Sources: [Python/compile.c1-15](https://github.com/python/cpython/blob/ea23c897/Python/compile.c#L1-L15) [Python/flowgraph.c1-50](https://github.com/python/cpython/blob/ea23c897/Python/flowgraph.c#L1-L50) [Python/bytecodes.c145-200](https://github.com/python/cpython/blob/ea23c897/Python/bytecodes.c#L145-L200) [Python/generated\_cases.c.h1-30](https://github.com/python/cpython/blob/ea23c897/Python/generated_cases.c.h#L1-L30) [Python/optimizer.c103-155](https://github.com/python/cpython/blob/ea23c897/Python/optimizer.c#L103-L155) [Python/executor\_cases.c.h1-30](https://github.com/python/cpython/blob/ea23c897/Python/executor_cases.c.h#L1-L30)

Object System and Memory Management
-----------------------------------

Python's object system is the foundation of the language. Everything in Python is an object, managed by CPython's memory management system.

Key features of CPython's object system:

* **PyObject**: Common base structure for all Python objects with reference count and type information
* **Reference Counting**: Primary memory management mechanism (Py\_INCREF/Py\_DECREF)
* **Garbage Collection**: Handles cyclic references that reference counting can't clean up
* **Type System**: Defines behavior of objects, with PyTypeObject storing methods and attributes

Sources: [Objects/object.c42-100](https://github.com/python/cpython/blob/ea23c897/Objects/object.c#L42-L100) [Include/internal/pycore\_object.h20-100](https://github.com/python/cpython/blob/ea23c897/Include/internal/pycore_object.h#L20-L100) [Objects/typeobject.c1-50](https://github.com/python/cpython/blob/ea23c897/Objects/typeobject.c#L1-L50) [Python/gc\_free\_threading.c1-30](https://github.com/python/cpython/blob/ea23c897/Python/gc_free_threading.c#L1-L30)

Bytecode Execution and Interpretation
-------------------------------------

CPython executes Python code by interpreting bytecode instructions. The instruction execution loop is a core part of the interpreter.

CPython uses a two-tier execution system:

1. **Tier 1**: A direct bytecode interpreter that handles all Python bytecode instructions

   * Implements specialized versions of common operations for improved performance
   * Uses a dispatch loop to fetch, decode, and execute instructions
2. **Tier 2**: A trace-based optimizer that converts bytecode to micro-operations (UOps)

   * Activated for hot code paths to improve performance
   * Transforms bytecode sequences into optimized micro-operation sequences
   * Can specialize code based on observed types and patterns

Sources: [Python/ceval.c500-550](https://github.com/python/cpython/blob/ea23c897/Python/ceval.c#L500-L550) [Python/bytecodes.c145-300](https://github.com/python/cpython/blob/ea23c897/Python/bytecodes.c#L145-L300) [Python/generated\_cases.c.h20-100](https://github.com/python/cpython/blob/ea23c897/Python/generated_cases.c.h#L20-L100) [Python/optimizer.c103-155](https://github.com/python/cpython/blob/ea23c897/Python/optimizer.c#L103-L155) [Python/optimizer\_bytecodes.c1-50](https://github.com/python/cpython/blob/ea23c897/Python/optimizer_bytecodes.c#L1-L50)

Global Interpreter Lock (GIL)
-----------------------------

The Global Interpreter Lock (GIL) is a mutex that protects access to Python objects, preventing multiple threads from executing Python bytecode at the same time.

Key aspects of the GIL:

* Only one thread can execute Python bytecode at a time
* The GIL is released periodically during long-running operations
* I/O operations generally release the GIL
* CPython 3.13+ has an experimental "--disable-gil" mode for true parallelism

Sources: [Python/ceval.c350-450](https://github.com/python/cpython/blob/ea23c897/Python/ceval.c#L350-L450) [Python/pystate.c350-430](https://github.com/python/cpython/blob/ea23c897/Python/pystate.c#L350-L430)

Extension and C API
-------------------

CPython provides a C API that allows developers to extend Python with modules written in C and to embed Python in other applications.

The C API provides functions for:

* Creating and managing Python objects
* Defining new types and modules
* Converting between C and Python data types
* Calling Python functions from C
* Error handling and exceptions

Sources: [Include/internal/pycore\_object.h20-100](https://github.com/python/cpython/blob/ea23c897/Include/internal/pycore_object.h#L20-L100) [Objects/typeobject.c90-150](https://github.com/python/cpython/blob/ea23c897/Objects/typeobject.c#L90-L150) [Objects/object.c42-100](https://github.com/python/cpython/blob/ea23c897/Objects/object.c#L42-L100)

Compilation Process
-------------------

Python source code goes through multiple stages of compilation before execution.

The compilation process includes:

1. **Tokenizing**: Breaking the source code into tokens
2. **Parsing**: Converting tokens into an Abstract Syntax Tree (AST)
3. **Symbol Table**: Creating symbol tables for variable scope resolution
4. **Code Generation**: Converting the AST to bytecode
5. **Optimization**: Optimizing the bytecode for better performance

Sources: [Python/compile.c1-50](https://github.com/python/cpython/blob/ea23c897/Python/compile.c#L1-L50) [Python/symtable.c1-50](https://github.com/python/cpython/blob/ea23c897/Python/symtable.c#L1-L50) [Python/flowgraph.c1-50](https://github.com/python/cpython/blob/ea23c897/Python/flowgraph.c#L1-L50)

Runtime and Interpreter State
-----------------------------

CPython maintains various state structures to manage the execution environment.

The key state structures are:

* **\_PyRuntimeState**: Global state for the entire Python process
* **PyInterpreterState**: State for each Python interpreter instance
* **PyThreadState**: Thread-local state for each thread executing Python code
* **\_PyInterpreterFrame**: Execution frame for the current function call

Sources: [Python/pystate.c50-200](https://github.com/python/cpython/blob/ea23c897/Python/pystate.c#L50-L200) [Include/internal/pycore\_interp.h1-30](https://github.com/python/cpython/blob/ea23c897/Include/internal/pycore_interp.h#L1-L30) [Python/pylifecycle.c1-50](https://github.com/python/cpython/blob/ea23c897/Python/pylifecycle.c#L1-L50)

Standard Library Integration
----------------------------

The Python standard library is tightly integrated with the core interpreter, with some modules implemented in C for performance.

Key aspects of standard library integration:

* Core modules like `sys` provide access to interpreter internals
* Some modules have C implementations for performance
* The `importlib` module handles the import system
* Standard library functionality is exposed through well-defined APIs

Sources: [Python/sysmodule.c1-50](https://github.com/python/cpython/blob/ea23c897/Python/sysmodule.c#L1-L50) [Python/import.c1-50](https://github.com/python/cpython/blob/ea23c897/Python/import.c#L1-L50)

Conclusion
----------

CPython is a complex system with multiple components working together to provide the Python programming experience. The code execution pipeline transforms Python source code into bytecode, which is then executed by the interpreter. The object system and memory management ensure efficient handling of Python objects. The GIL manages thread synchronization, while the C API enables extension development.

Understanding these core components provides a solid foundation for diving deeper into specific parts of the CPython codebase and for contributing to its development.

For more detailed information about specific components, see:

* [Code Execution Pipeline](/python/cpython/2-code-execution-pipeline)
* [Object System and Memory Management](/python/cpython/3-object-system-and-memory-management)
* [Runtime and Thread Management](/python/cpython/4-runtime-and-thread-management)
* [Extension Development and C API](/python/cpython/5-extension-development-and-c-api)
* [Build System](/python/cpython/6-build-system)