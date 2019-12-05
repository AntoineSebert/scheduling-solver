# schedule_verifier_02229

**Requirement:** python3

**Assumptions:**
- Slices do not overlap in a core
- Slices are given in .xml in order of execution

**Use:** 
```
python3 verification_tool.py <path_to_testcase_folder>
```
Argument <path_to_testcase_folder> is a path to a folder of one testcase, containing a .cfg, .tsk & .xml file.

**Example:**
```
python3 verification_tool.py TestCases/CaseExample
```
