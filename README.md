# Stochastic Models for Remote Timing Attacks Artifacts

## Dependencies/Installation instructions

### Model

1. Install MATLAB
2. Install the symbolic math toolbox add-on

### Load Simulator

1. Install k6 (https://grafana.com/docs/k6/latest/set-up/install-k6/)
2. (Optional) Launch with k6 run load_simulator.js

### Python

Install numpy, pandas, scipy and playwright

## References to the paper's pseudo-code

Because we had to run our tests using previously collected data, due to reasons such as reproducibility and testing, we split the two algorithms presented in the paper. The process involves two main phases: data collection and data processing. Here's how these steps are organized:

### 1. Data Collection  
We first collect response time data for **cross-site timing** and **direct timing attacks** using the following scripts:  
- **Cross-site timing attacks:** `payload.html` (and `payload.js`)  
- **Direct timing attacks:** `measure_direct_timings_response_times.py` (and `measure_direct_timings_aux.py`)  

These scripts execute both the exploration and exploitation phases but only collect raw response time data without processing. For this step, you need to configure:

- The number of samples per batch for the exploration phase
- The number of batches for the exploration phase
- The endtime for the exploration phase
- The number of samples for the exploitation phase

---

### 2. Data Processing  
After collecting the data, we process it using the following scripts:  
- **Cross-site timing attacks:** `launch_model_cross_site.py`  
- **Direct timing attacks:** `launch_model_direct.py`  

Both scripts handle processing for the exploration and exploitation phases. The workflow is as follows:

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

---
