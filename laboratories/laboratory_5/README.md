# Laboratory 5 - Architectural Verification
## 1. Objective

This lab aims to practically demonstrate the process of verifying the performance of a software system. It seeks to assess how the introduction of various architectural tactics related to performance and scalability can lead to improved results.

## 2. Part 1
Follow the instructions in the following [instructive](https://github.com/unal-lssa/lssa2025i/blob/main/laboratories/laboratory_5/part1.md) where you can find an example of how to modify and manage architectural tactics such as rate limiting and patterns such as load balancing.
## 3. Part 2
The following example presents an exercise in verifying the ERTMS system using a Python notebook in Google Collab:
[link](https://colab.research.google.com/drive/1d6B-539L2yjkjHsm6q8e7Zy5k-6bvVFl?ouid=115725317442376237948&usp=classroom_web&authuser=0)


### Conclusion

Adding some Performance & Scalability tactics leads to improved system performance. These tactics include:

* We introduced Load Balancing to distribute traffic.
* We reduced latency with Caching.
* We offloaded slow tasks with Asynchronous Processing.
* We introduced Limit Event Response.

Thanks to the simulator, you can verify that the system's performance is as agreed and even find possible areas for improvement.

