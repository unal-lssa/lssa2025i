**Large-Scale Software Architecture, 2025i**<br>
Jeisson Andrés Vergara Vargas

# Project - Delivery 2

## 1. Objective

The objective of the second (final) delivery of the project is to perform an iterative process to partially design and verify the architecture of a large-scale software system, applying an execution process (for verification) that includes modeling, instantiation, graphing, simulation, and results analysis.

## 2. Activities

* Perform four architectural verification iterations for the software system designed in **Delivery 1**.
* Iteration 1 must be based on the architectural model created in the **Delivery 1** and must focus on the **security** quality attribute (scenario).
* Iteration 2 must be based on a new architectural model that includes at least one architectural tactic and an architectural pattern that allows responding to the scenario posed in iteration 1.
* Iteration 3 must be based on the architectural model created in the iteration 3 and must focus on the **scalability** quality attribute (scenario).
* Iteration 4 must be based on a new architectural model that includes at least one architectural tactic and an architectural pattern that allows responding to the scenario posed in iteration 3.
* Execute each iteration through a process that includes: modeling, instantiation, graphing (C&C architectural view and deployment architectural view (if applicable)), simulation (of the quality attribute scenarios), and analysis of results. Refer to Lab 5. Use a general-purpose programming language for this activity (preferably Python) and develop the process using a Jupyter Notebook in Google Colab.

## 3. Considerations

* For new models to be created, the original metamodel (delivery 1) must be adjusted in order to allow the modeling of security and scalability elements.
* The second and fourth iterations should emphasize the redesign of the system architecture, including at least one architectural tactic and one architectural pattern that enable compliance with each one of the quality attributes (responses to the scenarios): security -> iteration 2, scalability -> iteration 4.
* Graphing (visualization of architectures) can be done manually, by creating architectural views using diagrams, or automatically, by using a graph creation library.

## 4. Delivery

### 4.1. Deliverable

* Link (URL) to a Jupyter Notebook, created and stored in Google Colab, named lssa_2025i_d2_x.ipynb (where X = the name of the system), which must contain:
 - Full names of team members.
 - System name.
 - System description.
 - Executable code for each execution (Note: execution must be possible directly in the Jupyter Notebook).
 - Descriptions associated with each phase of each execution: modeling, instantiation, graphing, simulation, and results analysis.

### 4.2. Submission Format

* The deliverable must be submitted via GitHub ([lssa2025i](https://github.com/unal-lssa/lssa2025i) repository).
* Steps:
  - Use the branch corresponding to your team (team1, team2, ...).
  - In the folder [project/delivery_2](), create an **X** folder (where X = the name of the system), which must include the **deliverable**:
    + README.md with the full names of the team members.
    + Jupyter Notebook URL.

### 4.3. Delivery Deadline

Thursday, May 15, 2025, before 23h59.