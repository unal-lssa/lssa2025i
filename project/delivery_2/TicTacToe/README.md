**Large Scale Software Architecture, 2025i**

---

**Team Members:**

- Andrés Arenas
- Cristian Camilo Triana Garcia
- Daniel Estivenson Dorado Lame
- Daniel Santiago Mendoza Morales
- Juan Bernardo Benavides Rubio
- Santiago Suarez

[**Jupiter Notebook URL**](https://colab.research.google.com/drive/1TiGPb-jd51hIvklcM5pvJZgVI_Qw5uA6?usp=sharing)

<br/>

# Project Delivery 2 - Online Real-Time Tic-Tac-Toe Platform

---

# 1. Introduction

## 1.1 Objective

The objective of the second delivery of the project is to perform an iterative process to partially design and verify the architecture of a large-scale software system. This includes modeling, instantiation, visualization, simulation, and results analysis.

This document walks through each phase of the architectural modeling and evaluation process using a simplified metamodel and simulated workloads to represent architectural concerns.


## 1.2 System description
The proposed software system is a real-time, online multiplayer platform that allows users to play the classic game Tic-Tac-Toe or some variants from their web browsers or mobile devices. This platform operates in a concurrent environment, where multiple users can connect, interact, and play games simultaneously.

The system must handle multiple ongoing matches, real-time data synchronization between clients, and user sessions. To ensure a smooth user experience, it requires a robust server-side component that manages game state consistency, conflict resolution, and communication between users.

This system must be scalable to support a growing number of concurrent users, and resilient to handle failures gracefully (e.g., a user disconnects mid-game).

## 1.3 Architecture Verification Scenarios

In this study case, we present two architecture verification scenarios that aim to assess the system’s behavior under adverse conditions. These scenarios serve as testbeds to evaluate the effectiveness of applied architectural patterns and tactics for improving security and scalability in an online real-time multiplayer environment.

### 1.3.1 Security Scenario: Denial of Service (DoS) Attack

In real-time online platforms, such as the Tic-Tac-Toe system under study, high concurrency and open endpoints expose the system to potential Denial of Service (DoS) attacks. These attacks aim to overload system resources, degrade performance, or make services unavailable to legitimate users.

- **Architectural Tactic**: **Detect Service Demand**

  This tactic enables the system to monitor the rate of incoming requests and identify potentially harmful usage patterns that indicate service saturation or abuse.

- **Architectural Pattern**: **Rate Limiting**

  The system enforces thresholds on the number of requests accepted from a single source within a given time window. This protects backend services from becoming overwhelmed and ensures fair usage among clients.

**Expected Outcome**:
By applying this tactic and pattern, the system should detect and mitigate abusive traffic while preserving availability and responsiveness for legitimate users.

### 1.3.2 Scalability Scenario: High Load Conditions

Scalability becomes a critical concern when the system experiences a significant increase in the number of concurrent users or processing demands. This scenario simulates a workload spike to test the system’s ability to maintain acceptable performance and responsiveness.

- **Architectural Tactic**: **Induce Concurrency**
  This tactic enables the system to process multiple operations in parallel, often by leveraging additional instances or replicas of services to handle increased demand efficiently.

- **Architectural Pattern**: **Load Balancing**
  A load balancer distributes incoming requests across multiple service instances based on predefined strategies (e.g., round robin, weighted round robin). This helps prevent overloading any single instance and ensures better throughput.

**Expected Outcome**:
The system should demonstrate an improved ability to handle concurrent requests by distributing workload evenly, minimizing latency, and maintaining stability under load.
