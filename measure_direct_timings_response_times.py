import time
import json
from datetime import datetime
import os
import signal
import subprocess
from measure_direct_timings_aux import measure_signin_response, generate_random_string
import argparse

parser = argparse.ArgumentParser(description="Data collection script used to measure response times for the direct timing attack.")
parser.add_argument('--url', type=str, help='URL of the login page of the local wordpress or hotcrp installation (e.g. http://localhost:9006/signin)', required=True)
parser.add_argument('--site', type=str, help='Name of the site to analyze (either wordpress or hotcrp)', required=True)
parser.add_argument('--nusers', type=int, help='Number of users set in the load simulator', required=True)
parser.add_argument('--skip', type=int, help='Number of users that will be subtracted at every cycle', required=True)
args = parser.parse_args()

url = args.url + "/?rand=" # Login page URL
site = args.site # Web application name
results_dir = "Direct_Timing_Data_Not_From_Paper/" + site

# Function used to modify the number of users in the load_simulator.js script 
def modify_line_in_file(file_path, line_number, old_content, new_line_content):
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
        lines[line_number] = lines[line_number].replace(old_content, new_line_content)
        with open(file_path, 'w') as file:
            file.writelines(lines)
    except Exception as e:
        print(f"An error occurred: {e}")

def main_playwright():
    number_of_users = args.nusers  # Starting number of users. Should correspond to the one in the load_simulator.js script
    skip = args.skip
    while number_of_users > 0:
        print(f"{datetime.now().strftime("%Y_%m_%d-%H_%M_%S")}: Starting measurements for {str(number_of_users)}...")
        # Launch load simulator
        proc = subprocess.Popen(
            ["k6", "run", "load_simulator.js", "--insecure-skip-tls-verify"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid
        )

        # Wait for warmup to end
        time.sleep(1200)
        # Start measurements
        for i in range(10):  # endtime
            wrong_email_times_account1 = [] 
            wrong_email_times_account2 = []
            wrong_pw_times_account1 = []
            wrong_pw_times_account2 = []
            # Repeat the measurements more than once for each batch
            for j in range(50):  # samples
                if site == 'wordpress':
                    wrong_email_times_account1.append(measure_signin_response(url + generate_random_string(), "fakealice@gmail.com", "wrong", "log", "pwd", "input", "wp-login", False))
                    wrong_pw_times_account1.append(measure_signin_response(url + generate_random_string(), "alice@gmail.com", "wrong", "log", "pwd", "input", "wp-login", False))
                    wrong_email_times_account2.append(measure_signin_response(url + generate_random_string(), "fakebob@gmail.com", "wrong", "log", "pwd", "input", "wp-login", False))
                    wrong_pw_times_account2.append(measure_signin_response(url + generate_random_string(), "bob@gmail.com", "wrong", "log", "pwd", "input", "wp-login", False))
                
                elif site == 'hotcrp':
                    wrong_email_times_account1.append(measure_signin_response(url + generate_random_string(), "fakealice@gmail.com", "wrong", "email", "password", "button", "signin", False))
                    wrong_pw_times_account1.append(measure_signin_response(url + generate_random_string(), "alice@gmail.com", "wrong", "email", "password", "button", "signin", False))
                    wrong_email_times_account2.append(measure_signin_response(url + generate_random_string(), "fakebob@gmail.com", "wrong", "email", "password", "button", "signin", False))
                    wrong_pw_times_account2.append(measure_signin_response(url + generate_random_string(), "bob@gmail.com", "wrong", "email", "password", "button", "signin", False))
                
                else:
                    raise Exception("Only wordpress and hotcrp are supported, please provide a valid site name.")

                time.sleep(4)
            
            data = {
                "wrong_email_times_account1": wrong_email_times_account1,
                "wrong_pw_times_account1": wrong_pw_times_account1,
                "wrong_email_times_account2": wrong_email_times_account2,
                "wrong_pw_times_account2": wrong_pw_times_account2,
            }

            # Save results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{str(number_of_users)}_users_{i}_iteration_results_{timestamp}.json"
            os.makedirs(f'{results_dir}/{number_of_users}', exist_ok=True)
            with open(f'{results_dir}/{number_of_users}/{filename}', 'a') as json_file:
                json.dump(data, json_file, indent=4)
            time.sleep(240)  # Wait before starting the next batch (tick)

        # Kill load simulator and decrease number of users
        os.killpg(os.getpgid(proc.pid), signal.SIGINT)
        modify_line_in_file('load_simulator.js', 48, str(number_of_users), str(number_of_users - skip))
        modify_line_in_file('load_simulator.js', 49, str(number_of_users), str(number_of_users - skip))
        number_of_users = number_of_users - skip
        time.sleep(120)

if __name__ == "__main__":
    main_playwright()
