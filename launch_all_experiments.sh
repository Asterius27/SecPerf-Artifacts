#!/bin/bash
set -ex

echo "=== 2a. Direct Timing (hotcrp) ==="
python3 launch_model_direct.py --site hotcrp --th 15

echo "=== 2a. Direct Timing (wordpress) ==="
python3 launch_model_direct.py --site wordpress --th 5

echo "=== 2b. Cross-Site Timing ==="
python3 launch_model_cross_site.py

echo "=== 2c. Direct Timing w/ # Requests (hotcrp) ===" python3 launch_model_direct_n_requests.py --site hotcrp --th 15

echo "=== 2c. Direct Timing w/ # Requests (wordpress) ===" python3 launch_model_direct_n_requests.py --site wordpress --th 5

echo "=== 2d. Cross-Site Timing w/ # Requests ===" python3 launch_model_cross_site_n_requests.py

echo "=== 2e. Direct Timing w/ Load Balancing ===" python3 launch_model_direct_load_balancing.py

echo "=== 2f. Direct Timing w/ RTT Noise (norm 0.3) ===" python3 launch_model_direct_rtt_noise.py --distribution norm --stddev 0.3

echo "=== 2f. Direct Timing w/ RTT Noise (norm 7) ===" python3 launch_model_direct_rtt_noise.py --distribution norm --stddev 7

echo "=== 2f. Direct Timing w/ RTT Noise (norm 21) ===" python3 launch_model_direct_rtt_noise.py --distribution norm --stddev 21

echo "=== 2f. Direct Timing w/ RTT Noise (log-norm 0.3) ===" python3 launch_model_direct_rtt_noise.py --distribution log-norm --stddev 0.3

echo "=== 2f. Direct Timing w/ RTT Noise (log-norm 7) ===" python3 launch_model_direct_rtt_noise.py --distribution log-norm --stddev 7

echo "=== 2f. Direct Timing w/ RTT Noise (log-norm 21) ===" python3 launch_model_direct_rtt_noise.py --distribution log-norm --stddev 21