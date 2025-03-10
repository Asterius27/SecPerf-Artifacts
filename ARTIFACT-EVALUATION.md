# Artifact Appendix

Paper title: **Stochastic Models for Remote Timing Attacks**

Artifacts HotCRP Id: **#5**

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
https://github.com/Asterius27/SecPerf-Artifacts/tree/09ba50b0fb7bb2c5482848c5f6c3c9a90de40523

### Set up the environment (Only for Functional and Reproduced badges)
Please refer to the README.md for a complete list of dependencies and installation instructions. Open the HTML file from Chrome if you want to collect data, all other scripts can be run simply by invoking python (python \<script\>.py).

### Testing the Environment (Only for Functional and Reproduced badges)
The scripts should run without any errors.

## Artifact Evaluation (Only for Functional and Reproduced badges)

### Main Results and Claims

#### Main Result 1: Experiments in a Controlled Setting
Our attack outperforms the box test on key performance metrics (true positive rate, true negative rate and abstention rate) using the response times collected in a controlled setting (HotCRP and WordPress) in a direct timing attack scenario. Section 6.2, specifically Table 2.
To generate the results presented in the table use the launch_model_direct.py script.

#### Main Result 2: Experiments in the Wild
Our attack outperforms BakingTimer on key performance metrics (true positive rate, true negative rate and abstention rate) using the response times collected in real-world websites in a cross-site timing attack scenario. Section 6.3, specifically Table 3.
To generate the results presented in the table use the launch_model_cross_site.py script.

#### Main Result 3: Number of Requests
Our attack outperforms the box test and BakingTimer on key performance metrics (true positive rate, true negative rate and abstention rate) using the same number of requests required by our attack to reach a conclusion. This experiment reuses the same data collected for the previous two experiments and the same scripts, with the only difference being that the arrays passed to the box test and BakingTimer are sliced. Section 6.4, specifically Tables 4 and 5.
To generate the results presented in the tables use a modified version of the launch_model_direct.py and launch_model_cross_site.py scripts.

#### Main Result 4: Robustness Analysis
Our attack is robust against RTT variations and different web application architectures. This experiment reuses the same data collected for the experiments in a controlled setting and the same script used for the experiments in a controlled setting, with the only difference being random noise added to the measurements (when testing robustness against RTT variations) and the dataset (when testing robustness against load balancing). Section 6.5, specifically Tables 6 and 7.
To generate the results presented in the tables use a modified version of the launch_model_direct.py script.

### Experiments 

#### Experiment 1: Experiments in a Controlled Setting
Simply launch the launch_model_direct.py script (```python launch_model_direct.py```) and adjust the ```SITE``` variable to compute results for HotCRP and WordPress in a direct timing scenario. By doing so you should be able to recompute the results presented in Table 2. It will take 3-4 hours (depending also on how powerful the CPU is) and just a couple of megabytes of space. This script uses the response times collected in our controlled setting with varying loads and computes the results for both our model and the box test. The results are saved in a csv file.

#### Experiment 2: Experiments in the Wild
Simply launch the launch_model_cross_site.py script (```python launch_model_cross_site.py```) to compute results for real-world websites in a cross-site timing scenario. By doing so you should be able to recompute the results presented in Table 3. It will take 3-4 hours (depending also on how powerful the CPU is) and just a couple of megabytes of space. This script uses the response times collected in the wild on Tranco's top 20 analyzed websites, and computes the results for both our model and BakingTimer. The results are saved in a csv file.

#### Experiment 3: Number of Requests
Simply launch the launch_model_direct_n_requests.py and launch_model_cross_site_n_requests.py scripts (```python launch_model_direct_n_requests.py``` and ```python launch_model_cross_site_n_requests.py```). For the launch_model_direct_n_requests.py script adjust the ```SITE``` variable to compute results for HotCRP and WordPress in a direct timing scenario. By doing so you should be able to recompute the results presented in Tables 4 and 5. It will take 3-4 hours (depending also on how powerful the CPU is) for each execution and just a couple of megabytes of space. Use the same datasets as before as this is only a study on the performance degradation of BakingTimer and the box test compared to the previous two experiments. The results are saved in a csv file.

#### Experiment 4: Robustness Analysis
When testing for robustness against RTT variations launch the launch_model_direct_rtt_noise.py script (```python launch_model_direct_rtt_noise.py```) and adjust the ```NOISE_DISTRIBUTION``` and ```STD_DEV``` variables to compute results for the different distributions and standard variations that are presented in the paper. The results in Table 6 cannot be reproduced exactly, as the noise added to the measurements is randomly sampled from a distribution each time the script is executed. It will take 3-4 hours (depending also on how powerful the CPU is) for each execution and just a couple of megabytes of space. Here we are only testing for performance degradation based on RTT variability in a controlled setting and this was done on the HotCRP dataset. The results are saved in a csv file.

When testing for robustness against load balancing, use the launch_model_direct_load_balancing.py script (```python launch_model_direct_load_balancing.py```). The only difference between this script and the launch_model_direct.py script is that this script loads the response times measured for our HotCRP installation with a load balancer ("Direct_Timing_Load_Balancer_Data" folder). By doing so you should be able to recompute the results presented in Table 7. It will take 3-4 hours (depending also on how powerful the CPU is) and just a couple of megabytes of space. Here we are only testing for performance degradation based on the presence of a load balancer in a controlled setting. The results are saved in a csv file.

## Limitations (Only for Functional and Reproduced badges)
The results in Table 6 cannot be reproduced exactly, as the noise added to the measurements is randomly sampled from a distribution each time the script is executed.

## Notes on Reusability (Only for Functional and Reproduced badges)
The MATLAB scripts that correspond to the model can be reused to implement any kind of remote timing attack, the required inputs are described throughout the paper and in the comments of the python scripts. The other scripts are just general scripts that collect response time data and process it before feeding it to the model, as well as processing the model's output in order to compute the presented results.
