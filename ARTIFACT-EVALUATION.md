# Artifact Appendix

Paper title: **Stochastic Models for Remote Timing Attacks**

Artifacts HotCRP Id: **#5** (not your paper Id, but the artifacts id)

Requested Badge: **Available**, **Functional**, and **Reproduced**

## Description
This artifact contains all the measurements that were collected for the paper, along with the scripts for data collection, processing, and result computation. Together, these resources enable the full reproduction of the paper's results.

### Security/Privacy Issues and Ethical Concerns (All badges)
None

## Basic Requirements (Only for Functional and Reproduced badges)
There are no specific hardware requirements. For software, the necessary tools are:

- Data Collection: Chrome (latest version), Python, Grafana k6, HotCRP, and WordPress.
- Data Processing: Python and MATLAB.

The data collection phase has no strict time constraints, though the recommended duration is predefined in the current version of the scripts. Processing the provided datasets to generate the paper's results takes approximately 5 hours on a modern CPU. Storage requirements are minimal, only a few megabytes. For a complete list of dependencies and installation instructions, please refer to the README.md.

### Hardware Requirements
None

### Software Requirements
Please refer to the README.md for a complete list of dependencies and installation instructions. In addition to the required software, collecting response time data from real-world websites requires creating an account on those websites. Alternatively, the provided datasets can be used instead.

### Estimated Time and Storage Consumption
Processing the provided datasets to generate the paper's results takes approximately 5 hours on a modern CPU. Storage requirements are minimal, only a few megabytes.

## Environment
Please refer to the README.md for a complete list of dependencies, installation, and execution instructions.

### Accessibility (All badges)
https://github.com/Asterius27/SecPerf-Artifacts/tree/9901cc56236ddd2e96fb8b560734dd65b5127384/

### Set up the environment (Only for Functional and Reproduced badges)
Please refer to the README.md for a complete list of dependencies and installation instructions. Open the HTML file from Chrome if you want to collect data, all other scripts can be run simply by invoking python (python \<script\>.py).

### Testing the Environment (Only for Functional and Reproduced badges)
None

## Artifact Evaluation (Only for Functional and Reproduced badges)
This section includes all the steps required to evaluate your artifact's functionality and validate your paper's key results and claims.
Therefore, highlight your paper's main results and claims in the first subsection. And describe the experiments that support your claims in the subsection after that.

### Main Results and Claims
List all your paper's results and claims that are supported by your submitted artifacts.

#### Main Result 1: Name
Describe the results in 1 to 3 sentences.
Refer to the related sections in your paper and reference the experiments that support this result/claim.

#### Main Result 2: Name
...

### Experiments 
List each experiment the reviewer has to execute. Describe:
 - How to execute it in detailed steps.
 - What the expected result is.
 - How long it takes and how much space it consumes on disk. (approximately)
 - Which claim and results does it support, and how.

#### Experiment 1: Name
Provide a short explanation of the experiment and expected results.
Describe thoroughly the steps to perform the experiment and to collect and organize the results as expected from your paper.
Use code segments to support the reviewers, e.g.,
```bash
python experiment_1.py
```
#### Experiment 2: Name
...

#### Experiment 3: Name 
...

## Limitations (Only for Functional and Reproduced badges)
Describe which tables and results are included or are not reproducible with the provided artifact.
Provide an argument why this is not included/possible.

## Notes on Reusability (Only for Functional and Reproduced badges)
First, this section might not apply to your artifacts.
Use it to share information on how your artifact can be used beyond your research paper, e.g., as a general framework.
The overall goal of artifact evaluation is not only to reproduce and verify your research but also to help other researchers to re-use and improve on your artifacts.
Please describe how your artifacts can be adapted to other settings, e.g., more input dimensions, other datasets, and other behavior, through replacing individual modules and functionality or running more iterations of a specific part.