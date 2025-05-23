# Stochastic Models for Remote Timing Attacks Artifacts

This artifact contains all the measurements that were collected for the paper, along with the scripts for data collection, processing, and result computation. Together, these resources enable the full reproduction of the paper's results.

## Dependencies/Installation instructions

### Model

1. Install MATLAB (version 24.2.0.2712019 (R2024b)) with Simulink (select it when prompted in the installation wizard)
2. Add MATLAB to the PATH environmnet variable (to test if you have successfully added MATLAB to path, you should be able to launch matlab by using the `matlab` command from any directory)
3. Install the symbolic math toolbox add-on (version 24.2). (From MATLAB: Apps -> Get More Apps -> Search for 'symbolic math toolbox' -> Install)
4. Check that the add-ons where successfully installed:
```
matlab -nodisplay -nosplash -r "ver; exit"
```
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;In the output you should see the following lines:
```
...
MATLAB                                                Version 24.2        (R2024b)
Simulink                                              Version 24.2        (R2024b)
Symbolic Math Toolbox                                 Version 24.2        (R2024b)
...
```

### Python

1. Install Python (version 3.13.2)
2. Install numpy (version 1.26.4), pandas (version 2.2.2), scipy (version 1.14.1) and playwright (version 1.45.1)
3. Install playwright browsers: `playwright install` (in the terminal)

### [OPTIONAL] Load Simulator

1. Install k6 (https://grafana.com/docs/k6/latest/set-up/install-k6/) (version k6 v1.0.0-rc1)
2. To check if you have successfully installed grafana k6, the `k6` command in the terminal should print the help output (the list of parameters)

### [OPTIONAL] WordPress and HotCRP

1. Install WordPress (version 6.7.0) and HotCRP (version 3.0.0)
2. Create two accounts in your local WordPress and HotCRP installations with the following credentials:
   - email: alice@gmail.com -- pass: password
   - email: bob@gmail.com -- pass: password

### [OPTIONAL] Browsers and Accounts

1. Install Chrome (version 131, it should also work with later versions, though they have not been tested)
2. Create two accounts (with any credentials) for all of the following websites:
   - https://www.microsoft.com/
   - https://it-it.facebook.com/
	- https://www.twitter.com/
	- https://www.office.com/it/
	- https://www.linkedin.it/
	- https://live.com/
	- https://wikipedia.org/
	- https://www.bing.it/
	- https://pinterest.com/
	- https://adobe.com/
	- https://www.spotify.com/
	- https://www.vimeo.com/
	- https://www.skype.com/

## References to the paper's pseudo-code and Execution instructions

Because we had to run our tests using previously collected data, due to reasons such as reproducibility and testing, we split the two algorithms that are presented in the paper. The process involves two main phases: data collection and data processing. 

There is no strict order in which the scripts must be executed. All data collection scripts are optional, as the required datasets are already provided. Note, however, that generating new datasets will not allow for exact reproduction of the paper’s results, since the datasets include response times measured from real-world websites. If you choose not to use the provided datasets, make sure to run all data collection scripts before executing any data processing scripts. **It is recommended to use the provided datasets.**

Here's how these steps are organized:

### [OPTIONAL] 1. Data Collection  
We first collect response time data for **cross-site timing** and **direct timing attacks** using the following scripts:  
- **Cross-site timing attacks:** `payload.html` (and `payload.js`)  
- **Direct timing attacks:** `measure_direct_timings_response_times.py` (and `measure_direct_timings_aux.py`)  

These scripts execute both the exploration and exploitation phases but only collect raw response time data without processing. For this step, you need to configure:

- The number of samples per batch for the exploration phase
- The number of batches for the exploration phase
- The endtime for the exploration phase
- The number of samples for the exploitation phase

#### [OPTIONAL] 1a. Data Collection for Direct Timing Attacks

**Note that you should have WordPress and HotCRP installed on a physically separate machine to the one where you are executing the data collection scripts in order to take accurate measurements, though the process will also work with everything installed on the same machine**

1. Update the script `load_simulator.js` with the correct URLs and parameters:
   - `baseURL` (line 8) is the web application's URL (e.g. localhost:3000)
   - `path` (line 11 and line 38) is the list of paths the load simulator will send requests to. Uncomment according to whether you are using wordpress (paths begin with wp-) or hotcrp (paths do not begin with wp-)
   - `target` (line 49 and 50) inside the `options` object is the number of virtual users the load simulator will use. This has to be set according to your machine
   - **DO NOT ADD OR REMOVE LINES FROM THIS FILE**
2. Launch the `measure_direct_timings_response_times.py` script (it will take around 8 hours to complete, depending on how many different load scenarios it has to simulate and collect measurements for) with the following arguments:
   - `url` is the URL of the login page of the local wordpress or hotcrp installation (e.g. http://localhost:9006/signin or http://localhost:9006/wp-login)
   - `site` is the name of the site to analyze (either wordpress or hotcrp)
   - `nusers` is the number of users set in the `load_simulator.js` script (the `target` field of the `options` object)
   - `skip` is the number of users that will be subtracted at every cycle, in order to change the simulated load. (E.g. if number_of_users is 800 and skip is 200, then the script will measure reponse times at 4 different loads, in the following order: 800 users, 600 users, 400 users, 200 users. The number of users determines the load of the system.) So an example command would be the following:
```
python3 measure_direct_timings_response_times.py --url http://localhost:9006/signin --site hotcrp --nusers 700 --skip 200
```
3. Repeat all steps and relaunch the `measure_direct_timings_response_times.py` script to collect data for the other web application (either WordPress or HotCRP depending on which one you did first)
4. Results will be inside the `Direct_Timing_Data_New/` folder
5. If you want to use these new measurements to run the analysis, then rename the `Direct_Timing_Data/` folder to `Direct_Timing_Data_Old/` and rename the `Direct_Timing_Data_New/` folder to `Direct_Timing_Data/`

#### [OPTIONAL] 1b. Data Collection for Cross-Site Timing Attacks

**Note that you should use two physically separate machines to collect accurate measurements, one where you the two instances used to collect data for the Exploration phase (by clicking on the 'Exploration Phase (knowing you are logged in)' and 'Exploration Phase (knowing you are NOT logged in)' buttons) and one where you have the two instances used to collect data for the Exploitation phase (by clicking on the 'Exploitation Phase (knowing you are logged in)' and 'Exploitation Phase (knowing you are NOT logged in)' buttons). However, the process will also work by doing everything on the same machine**

1. Open 4 different instances of Chrome with 4 different clean profiles, in order to have 4 simultaneous instances of chrome that are all clean and indipendent of each other
2. In one of these instances log in with one of the two accounts that were created for all websites in all websites, do the same in another instance with the other account for all websites
3. Load the `payload.html` file in all 4 instances
4. In the two instances were you logged in to all websites launch the Exploration and Exploitation phases for a logged in user by clicking on the 'Exploration Phase (knowing you are logged in)' button in one instance and on the 'Exploitation Phase (knowing you are logged in)' button in the other instance
5. In the other two instances launch the Exploration and Exploitation phases for a non logged in user by clicking on the 'Exploration Phase (knowing you are NOT logged in)' button in one instance and on the 'Exploitation Phase (knowing you are NOT logged in)' button in the other instance
6. You may see errors in the browser console — this is normal, and you can safely ignore them
7. You might have to allow 'multiple file downloads' in Chrome
8. The data collection will run indefinitely, though once each batch of measurements has finished it will download a .json file. You can decide when to stop collecting measurements, though it is recommended to collect data for at least 7-8 hours.
9. If you want to use these new measurements to run the analysis:
   - Rename the `Cross_Site_Exploitation_Phase_Data/` folder to `Cross_Site_Exploitation_Phase_Data_Old/`
   - Rename the `Cross_Site_Exploration_Phase_Data/` folder to `Cross_Site_Exploration_Phase_Data_Old/`
   - Create a new `Cross_Site_Exploitation_Phase_Data/` folder and place inside it all .json files downloaded from the two instances where you clicked on the 'Exploitation Phase' button (both logged and not logged)
   - Create a new `Cross_Site_Exploration_Phase_Data/` folder and place inside it all .json files downloaded from the two instances where you clicked on the 'Exploration Phase' button (both logged and not logged)

---

### 2. Data Processing  
After collecting the data, we process it using the following scripts:  
- **Cross-site timing attacks:** `launch_model_cross_site.py`
- **Cross-site timing attacks with limit on number of requests:** `launch_model_cross_site_n_requests.py`
- **Direct timing attacks:** `launch_model_direct.py`
- **Direct timing attacks with limit on number of requests:** `launch_model_direct_n_requests.py`
- **Direct timing attacks with load balancing:** `launch_model_direct_load_balancing.py`
- **Direct timing attacks with simulated RTT noise:** `launch_model_direct_rtt_noise.py`

All scripts handle processing for the exploration and exploitation phases. The general workflow is as follows:

#### Exploration Phase:
1. **Load and preprocess data:**  
   - Load the exploration phase data and remove round-trip times (RTT) from measurements.  
   - Compute the minimum response times to derive the `X^0` and `X^1` arrays (via the `load_expl_phase` function).  

2. **Determine the load factor array (`X^R`):**  
   - Identify the batch of requests closest in time to the attack.  
   - Remove RTT from the measurements in this array.  

This completes the exploration phase, producing the `X^0`, `X^1`, and `X^R` arrays.

#### Exploitation Phase:
1. **Model building:**  
   - Build the model using the `X^0`, `X^1`, and `X^R` arrays that were computed earlier.  

2. **Process exploitation data:**  
   - Load the exploitation phase data and iterate through the requests, simulating the pseudo-code’s `while` loop.  

3. **Probability estimation:**  
   - For each measurement in the exploitation array, execute the MATLAB script (corresponding to the `EstimateProba` sub-procedure) to calculate probabilities.  

4. **Stopping criteria:**  
   - Stop processing when either:  
     - A probability exceeds the threshold (`alpha`)  
     - The end of the array is reached  

#### 2a. Compute Direct Timing Attacks Results

Execute `launch_model_direct.py` (it will take around 4 hours on a decently fast machine), with the following arguments:
   - `site` is the name of the site to analyze (either `wordpress` or `hotcrp`)
   - `th` is the threshold value used by the MATLAB script (5 for `wordpress` and 15 for `hotcrp`)

So the commands needed to reproduce the paper's results are:
```
python3 launch_model_direct.py --site hotcrp --th 15
python3 launch_model_direct.py --site wordpress --th 5
```
The overall results are saved in .txt and .csv files inside the 'Direct_Timing_Results/<web_application_name>/' folder.

#### 2b. Compute Cross-Site Timing Attacks Results

Execute `launch_model_cross_site.py`, no arguments needed (it will take around 4 hours on a decently fast machine). The overall results are saved in .txt and .csv files inside the 'Cross_Site_Results/' folder.

#### 2c. Compute Direct Timing Attacks With Limit on Number of Requests Results

Execute `launch_model_direct_n_requests.py` (it will take around 4 hours on a decently fast machine), with the following arguments:
   - `site` is the name of the site to analyze (either `wordpress` or `hotcrp`)
   - `th` is the threshold value used by the MATLAB script (5 for `wordpress` and 15 for `hotcrp`)

So the commands needed to reproduce the paper's results are:
```
python3 launch_model_direct_n_requests.py --site hotcrp --th 15
python3 launch_model_direct_n_requests.py --site wordpress --th 5
```
The overall results are saved in .txt and .csv files inside the 'Direct_Timing_Number_of_Requests_Results/<web_application_name>/' folder.

#### 2d. Compute Cross-Site Timing Attacks With Limit on Number of Requests Results

Execute `launch_model_cross_site_n_requests.py`, no arguments needed (it will take around 4 hours on a decently fast machine). The overall results are saved in .txt and .csv files inside the 'Cross_Site_Number_of_Requests_Results/' folder.

#### 2e. Compute Direct Timing Attacks With Load Balancing Results

Execute `launch_model_direct_load_balancing.py`, no arguments needed (it will take around 4 hours on a decently fast machine). The overall results are saved in .txt and .csv files inside the 'Direct_Timing_Load_Balancing_Results/hotcrp/' folder.

#### 2f. Compute Direct Timing Attacks With Simulated RTT Noise Results

Execute `launch_model_direct_rtt_noise.py` (it will take around 4 hours on a decently fast machine), with the following arguments:
   - `distribution` is the distribution used to simulate the RTT noise (either norm or log-norm)
   - `stddev` is the standard deviation of the distribution (either 0.3 or 7 or 21)

So the commands needed to reproduce the paper's results are:
```
python3 launch_model_direct_rtt_noise.py --distribution norm --stddev 0.3
python3 launch_model_direct_rtt_noise.py --distribution norm --stddev 7
python3 launch_model_direct_rtt_noise.py --distribution norm --stddev 21
python3 launch_model_direct_rtt_noise.py --distribution log-norm --stddev 0.3
python3 launch_model_direct_rtt_noise.py --distribution log-norm --stddev 7
python3 launch_model_direct_rtt_noise.py --distribution log-norm --stddev 21
```
The overall results are saved in .txt and .csv files inside the 'Direct_Timing_&lt;distribution&gt;_&lt;stddev&gt;_Results/hotcrp/' folder.

---

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

The data collection phase has no strict time constraints, though the recommended duration is predefined in the current version of the scripts. Processing the provided datasets to generate the paper's results takes approximately 5 hours on a modern CPU. Storage requirements are minimal, only a few megabytes. For a complete list of dependencies and installation instructions, please refer to the 'Dependencies/Installation instructions' section.

### Hardware Requirements
None

### Software Requirements
Please refer to the 'Dependencies/Installation instructions' section for a complete list of dependencies and installation instructions. In addition to the required software, collecting response time data from real-world websites requires creating an account on those websites. Alternatively, the provided datasets can be used instead.

### Estimated Time and Storage Consumption
Processing the provided datasets to generate the paper's results takes approximately 5 hours on a modern CPU. Storage requirements are minimal, only a few megabytes.

## Environment
Please refer to the 'Dependencies/Installation instructions' and 'References to the paper's pseudo-code and Execution instructions' sections for a complete list of dependencies, installation, and execution instructions.

### Accessibility (All badges)
https://github.com/Asterius27/SecPerf-Artifacts/tree/e2f8d5368ab50931f18bd41d8500ee47fbd02219

### Set up the environment (Only for Functional and Reproduced badges)
Please refer to the 'Dependencies/Installation instructions' section for a complete list of dependencies and installation instructions. Open the HTML file from Chrome if you want to collect data, all other scripts can be run simply by invoking python (python \<script\>.py).

### Testing the Environment (Only for Functional and Reproduced badges)
The scripts should run without any errors, except for the payload.js script, where there will be errors that can safely be ignored. Please refer to the 'Dependencies/Installation instructions' section for a complete list of instructions to test whether the dependencies were successfully installed.

## Artifact Evaluation (Only for Functional and Reproduced badges)

### Main Results and Claims

#### Main Result 1: Experiments in a Controlled Setting
Our attack outperforms the box test on key performance metrics (true positive rate, true negative rate and abstention rate) using the response times collected in a controlled setting (HotCRP and WordPress) in a direct timing attack scenario. Section 6.2, specifically Table 2.
To generate the results presented in the table use the launch_model_direct.py script (Section 2a of this file).

#### Main Result 2: Experiments in the Wild
Our attack outperforms BakingTimer on key performance metrics (true positive rate, true negative rate and abstention rate) using the response times collected in real-world websites in a cross-site timing attack scenario. Section 6.3, specifically Table 3.
To generate the results presented in the table use the launch_model_cross_site.py script (Section 2b of this file).

#### Main Result 3: Number of Requests
Our attack outperforms the box test and BakingTimer on key performance metrics (true positive rate, true negative rate and abstention rate) using the same number of requests required by our attack to reach a conclusion. This experiment reuses the same data collected for the previous two experiments and the same scripts, with the only difference being that the arrays passed to the box test and BakingTimer are sliced. Section 6.4, specifically Tables 4 and 5.
To generate the results presented in the tables use the launch_model_direct_n_requests.py and launch_model_cross_site_n_requests.py scripts (Sections 2c and 2d of this file).

#### Main Result 4: Robustness Analysis
Our attack is robust against RTT variations and different web application architectures. This experiment reuses the same data collected for the experiments in a controlled setting and the same script used for the experiments in a controlled setting, with the only difference being random noise added to the measurements (when testing robustness against RTT variations) and the dataset (when testing robustness against load balancing). Section 6.5, specifically Tables 6 and 7.
To generate the results presented in the tables use the launch_model_direct_load_balancing.py and launch_model_direct_rtt_noise.py scripts (Sections 2e and 2f of this file).

### Experiments 

#### Experiment 1: Experiments in a Controlled Setting
Simply launch the launch_model_direct.py script (```python launch_model_direct.py```) and change the ```site``` argument to compute results for HotCRP and WordPress in a direct timing scenario. By doing so you should be able to recompute the results presented in Table 2. It will take 3-4 hours (depending also on how powerful the CPU is) and just a couple of megabytes of space. This script uses the response times collected in our controlled setting with varying loads and computes the results for both our model and the box test. The results are saved in a csv file. Please refer to section 2a of this file for a complete list of instructions for this experiment.

#### Experiment 2: Experiments in the Wild
Simply launch the launch_model_cross_site.py script (```python launch_model_cross_site.py```) to compute results for real-world websites in a cross-site timing scenario. By doing so you should be able to recompute the results presented in Table 3. It will take 3-4 hours (depending also on how powerful the CPU is) and just a couple of megabytes of space. This script uses the response times collected in the wild on Tranco's top 20 analyzed websites, and computes the results for both our model and BakingTimer. The results are saved in a csv file. Please refer to section 2b of this file for a complete list of instructions for this experiment.

#### Experiment 3: Number of Requests
Simply launch the launch_model_direct_n_requests.py and launch_model_cross_site_n_requests.py scripts (```python launch_model_direct_n_requests.py``` and ```python launch_model_cross_site_n_requests.py```). For the launch_model_direct_n_requests.py script change the ```site``` argument to compute results for HotCRP and WordPress in a direct timing scenario. By doing so you should be able to recompute the results presented in Tables 4 and 5. It will take 3-4 hours (depending also on how powerful the CPU is) for each execution and just a couple of megabytes of space. Use the same datasets as before as this is only a study on the performance degradation of BakingTimer and the box test compared to the previous two experiments. The results are saved in a csv file. Please refer to sections 2c and 2d of this file for a complete list of instructions for this experiment.

#### Experiment 4: Robustness Analysis
When testing for robustness against RTT variations launch the launch_model_direct_rtt_noise.py script (```python launch_model_direct_rtt_noise.py```) and change the ```distribution``` and ```stddev``` arguments to compute results for the different distributions and standard variations that are presented in the paper. The results in Table 6 cannot be reproduced exactly, as the noise added to the measurements is randomly sampled from a distribution each time the script is executed. It will take 3-4 hours (depending also on how powerful the CPU is) for each execution and just a couple of megabytes of space. Here we are only testing for performance degradation based on RTT variability in a controlled setting and this was done on the HotCRP dataset. The results are saved in a csv file.

When testing for robustness against load balancing, use the launch_model_direct_load_balancing.py script (```python launch_model_direct_load_balancing.py```). The only difference between this script and the launch_model_direct.py script is that this script loads the response times measured for our HotCRP installation with a load balancer ("Direct_Timing_Load_Balancer_Data" folder). By doing so you should be able to recompute the results presented in Table 7. It will take 3-4 hours (depending also on how powerful the CPU is) and just a couple of megabytes of space. Here we are only testing for performance degradation based on the presence of a load balancer in a controlled setting. The results are saved in a csv file.

Please refer to sections 2e and 2f of this file for a complete list of instructions for this experiment.

## Limitations (Only for Functional and Reproduced badges)
The results in Table 6 cannot be reproduced exactly, as the noise added to the measurements is randomly sampled from a distribution each time the script is executed. Since the datasets include response times from real-world servers, any new measurements will (slightly) differ, making it impossible to exactly reproduce the original datasets.

## Notes on Reusability (Only for Functional and Reproduced badges)
The MATLAB scripts that correspond to the model can be reused to implement any kind of remote timing attack, the required inputs are described throughout the paper and in the comments of the python scripts. The other scripts are just general scripts that collect response time data and process it before feeding it to the model, as well as processing the model's output in order to compute the presented results.
