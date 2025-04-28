import subprocess
import re
import os
import json
import numpy as np
import csv
from datetime import datetime
from scipy import stats
import pandas as pd
import shutil

EXECUTE_MATLAB = True

resp_times_path = 'Cross_Site_Exploration_Phase_Data/'
attack_times_path = 'Cross_Site_Exploitation_Phase_Data/'
results_path = "Cross_Site_Results/"
th = 15
nbins = 4
thresh = 0.90 # alpha

try:
    shutil.rmtree(results_path)
except FileNotFoundError:
    pass
except Exception as e:
    pass

# Implementation of the state-of-the-art attack: BakingTimer
def baking_timer(include_not_logged, omit_not_logged, include_logged, omit_logged, include_attack, omit_attack, key, expected_result, tp_count_bt, fp_count_bt, tn_count_bt, fn_count_bt, unk_count_bt):
    alpha = 0.05  # Significance level

    baseline_logged = [a - b for a, b in zip(include_logged, omit_logged)]
    baseline_not_logged = [a - b for a, b in zip(include_not_logged, omit_not_logged)]
    attack_deltas = [a - b for a, b in zip(include_attack, omit_attack)]
    
    t_statistic, p_value = stats.ttest_ind(baseline_logged, baseline_not_logged)

    vuln = False
    if p_value < alpha:
        vuln = True

    if vuln:
        logged_t_statistic, logged_p_value = stats.ttest_ind(baseline_logged, attack_deltas)
        not_logged_t_statistic, not_logged_p_value = stats.ttest_ind(baseline_not_logged, attack_deltas)

        if (logged_p_value < alpha and not not_logged_p_value < alpha) or (not_logged_p_value < alpha and not logged_p_value < alpha):
            if logged_p_value < alpha:
                if expected_result == 'with_cookies':
                    fn_count_bt[key] += 1
                if expected_result == 'without_cookies':
                    tn_count_bt[key] += 1
            if not_logged_p_value < alpha:
                if expected_result == 'with_cookies':
                    tp_count_bt[key] += 1
                if expected_result == 'without_cookies':
                    fp_count_bt[key] += 1
        else:
            unk_count_bt[key] += 1
    else:
        unk_count_bt[key] += 1

def parse_date_string(date_str):
    return datetime.strptime(date_str, "%Y_%m_%dT%H_%M_%S_%fZ")

# Recursively remove outliers from a dataset by filtering values more than 2 standard deviations away from the mean.
def delete_outliers(arr):
    arrr = np.array(arr)
    mean = np.mean(arrr)
    std_dev = np.std(arrr)
    threshold = 2 * std_dev
    filtered_arr = arrr[np.abs(arrr - mean) <= threshold]

    if len(filtered_arr) == len(arrr):
        return filtered_arr
    else:
        return delete_outliers(filtered_arr)

# Load exploration phase data for the specified user state (e.g., 'with_cookies' or 'without_cookies'). Compute the X^0 and X^1 arrays.
def load_expl_phase(state):
    files = [e for e in os.listdir(resp_times_path) if not e.startswith('.')]
    min_include_mean = {}
    min_omit_mean = {}
    min_include_dt = {}
    min_omit_dt = {}
    expl_resp_times = {}
    expl_network_latencies = {}
    expl_network_latencies_arr = {}
    for file in files:
        if not file.startswith('old_') and file.endswith('.json'):
            dt = "_".join(file.split('_')[3:]).split(".")[0]
            file_path = os.path.join(resp_times_path, file)
            with open(file_path, 'r') as f:
                data = json.load(f)
                for key in data:
                    if data[key]['user_state'] == state:
                        min_include_mean.setdefault(key, float('inf'))
                        min_omit_mean.setdefault(key, float('inf'))
                        min_include_dt.setdefault(key, '')
                        min_omit_dt.setdefault(key, '')

                        # Process include and omit means, filtering outliers
                        include_mean = np.mean(delete_outliers([float(i) for i in data[key]['include']]))
                        omit_mean = np.mean(delete_outliers([float(i) for i in data[key]['omit']]))

                        # Update minimum means and associated timestamps
                        if include_mean is not None and include_mean < min_include_mean[key]:
                            min_include_mean[key] = include_mean
                            min_include_dt[key] = dt
                        if omit_mean is not None and omit_mean < min_omit_mean[key]:
                            min_omit_mean[key] = omit_mean
                            min_omit_dt[key] = dt
                        
                        expl_resp_times.setdefault(key, {})
                        expl_resp_times[key].setdefault(dt, {})
                        expl_resp_times[key][dt]['include'] = data[key]['include']
                        expl_resp_times[key][dt]['omit'] = data[key]['omit']
                        expl_resp_times[key][dt]['redirect_omit'] = data[key]['redirect_omit']
                        expl_network_latencies.setdefault(key, {})
                        expl_network_latencies_arr.setdefault(key, {})
                        expl_network_latencies[key][dt] = min(delete_outliers([float(i) for i in data[key]['redirect_omit']]))
                        expl_network_latencies_arr[key][dt] = delete_outliers([float(i) for i in data[key]['redirect_omit']])
    return expl_resp_times, expl_network_latencies, min_include_mean, min_omit_mean, min_include_dt, min_omit_dt, expl_network_latencies_arr

# Load exploration phase data for both states (with and without cookies)
expl_resp_times, expl_network_latencies, min_include_mean, min_omit_mean, min_include_dt, min_omit_dt, expl_network_latencies_arr = load_expl_phase('with_cookies')
expl_resp_times_nl, expl_network_latencies_nl, min_include_mean_nl, min_omit_mean_nl, min_include_dt_nl, min_omit_dt_nl, expl_network_latencies_arr_nl = load_expl_phase('without_cookies')

total_all = {}

tp_count = {}
fp_count = {}
tn_count = {}
fn_count = {}
unk_count = {}

tp_count_bt = {}
fp_count_bt = {}
tn_count_bt = {}
fn_count_bt = {}
unk_count_bt = {}

# Process attack phase files to compute metrics
filess = [e for e in os.listdir(attack_times_path) if not e.startswith('.')]
for file in filess:
    dt = "_".join(file.split('_')[3:]).split(".")[0]
    if not file.startswith('old_') and file.endswith('.json'):
        file_path = os.path.join(attack_times_path, file)
        with open(file_path, 'r') as f:
            data = json.load(f)
            for key in data:
                found = False

                # Gather X^0, X^1, X^R (BuildModel)

                attack_network_latency = min(delete_outliers([float(i) for i in data[key]['redirect_measured_response_times']]))
                
                # Get the batch of requests (done in the exploration phase) that were gathered at the closest date & time
                closest_date_string = min(expl_resp_times[key].keys(), key=lambda s: abs(parse_date_string(s) - parse_date_string(dt)))
                closest_date_string_nl = min(expl_resp_times_nl[key].keys(), key=lambda s: abs(parse_date_string(s) - parse_date_string(dt)))
                
                filt_resp_times_omit_low_load = delete_outliers([max(x - expl_network_latencies[key][min_omit_dt[key]], 0.1) for x in expl_resp_times[key][min_omit_dt[key]]['omit']]).tolist()  # X^0
                filt_resp_times_include_low_load = delete_outliers([max(x - expl_network_latencies[key][min_include_dt[key]], 0.1) for x in expl_resp_times[key][min_include_dt[key]]['include']]).tolist()  # X^1
                filt_resp_times_expl = delete_outliers([max(x - expl_network_latencies[key][closest_date_string], 0.1) for x in expl_resp_times[key][closest_date_string]['omit']]).tolist()  # X^R
                filt_resp_times_attack = delete_outliers([float(i) for i in data[key]['measured_response_times']])
                resp_times_attack = [float(i) for i in data[key]['measured_response_times']]
                resp_times_attack_omit = [float(i) for i in data[key]['measured_response_times_omit']]

                tp_count_bt.setdefault(key, 0)
                fp_count_bt.setdefault(key, 0)
                tn_count_bt.setdefault(key, 0)
                fn_count_bt.setdefault(key, 0)
                unk_count_bt.setdefault(key, 0)

                # Execute BakingTimer for comparison
                baking_timer(expl_resp_times_nl[key][closest_date_string_nl]['include'], expl_resp_times_nl[key][closest_date_string_nl]['omit'], expl_resp_times[key][closest_date_string]['include'],
                                expl_resp_times[key][closest_date_string]['omit'], resp_times_attack, resp_times_attack_omit, key, data[key]['expected_result'], tp_count_bt, fp_count_bt, tn_count_bt, fn_count_bt, unk_count_bt)

                resp_times_omit_low_load_str = "[" + ", ".join(map(str, filt_resp_times_omit_low_load)) + "]"
                resp_times_include_low_load_str = "[" + ", ".join(map(str, filt_resp_times_include_low_load)) + "]"
                resp_times_expl_str = "[" + ", ".join(map(str, filt_resp_times_expl)) + "]"

                resp_times_attack_str = "[" + ", ".join(map(str, filt_resp_times_attack)) + "]"
                
                if EXECUTE_MATLAB:
                    # Launch the model (EstimateProba)
                    command = 'matlab -batch "cd(\'Model\'); getProbs(' + resp_times_omit_low_load_str + ', ' + resp_times_include_low_load_str + ', ' + resp_times_expl_str + ', ' + resp_times_attack_str + ', ' + str(th) + ', ' + str(nbins) + ', ' + str(attack_network_latency) + ');"'
                    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                else:
                    results = []
                    with open(results_path + key + "/" + key + "_results_" + dt + '.csv', mode='r') as results_file:
                        reader = csv.reader(results_file)
                        next(reader)
                        for row in reader:
                            results.append(row)

                i = 0
                total_all.setdefault(key, 0)

                tp_count.setdefault(key, 0)
                fp_count.setdefault(key, 0)
                tn_count.setdefault(key, 0)
                fn_count.setdefault(key, 0)
                unk_count.setdefault(key, 0)

                lastl = []
                os.makedirs(f'Cross_Site_Results/{key}', exist_ok=True)
                if EXECUTE_MATLAB:
                    liness = process.stdout
                else:
                    liness = results
                    
                empty = True

                # Process results from MATLAB and update metrics
                for line in liness:
                    empty = False
                    i += 1
                    if EXECUTE_MATLAB:
                        output = line.decode('utf-8').replace(' ', '')
                        output_arr = re.split('=|\n', output.replace("\\n", "\n"))
                    else:
                        output_arr = ["Pr(Omit)=", str(line[1]), "Pr(Include)=", str(line[2]), "Lamda=", '0' if line[14] == '?' else str(line[14]), "Mu=", '1', 'Pi0_1=', '?', 'Pi0_2=', '?', 'Pi0_3=', '?', 'Pi0_4=', '?']

                    lastl = output_arr
                    if output_arr[1] == "NaN" or output_arr[3] == "NaN":
                        pass
                    else:
                        if data[key]['expected_result'] == 'with_cookies' and float(output_arr[3]) > float(output_arr[1]):
                            if not found and float(output_arr[3]) >= thresh:
                                tp_count[key] += 1
                                found = True
                        if data[key]['expected_result'] == 'with_cookies' and float(output_arr[3]) <= float(output_arr[1]):
                            if not found and float(output_arr[1]) >= thresh:
                                fn_count[key] += 1
                                found = True
                        if data[key]['expected_result'] == 'without_cookies' and float(output_arr[3]) > float(output_arr[1]):
                            if not found and float(output_arr[3]) >= thresh:
                                fp_count[key] += 1
                                found = True
                        if data[key]['expected_result'] == 'without_cookies' and float(output_arr[3]) <= float(output_arr[1]):
                            if not found and float(output_arr[1]) >= thresh:
                                tn_count[key] += 1
                                found = True

                    with open(f'Cross_Site_Results/{key}/{key}_results_{dt}.csv', 'a', newline='') as csv_file:
                        writer = csv.writer(csv_file)
                        if i == 1:
                            writer.writerow(['num_attack_obs', 'pr_omit', 'pr_include', 'expected_result', 'last_attack_resp_added', 'th'])
                        writer.writerow([i, output_arr[1], output_arr[3], data[key]['expected_result'], round(filt_resp_times_attack[i - 1], 3), th])

                if empty:
                    raise Exception("MATLAB is not running properly... have you added MATLAB to the PATH environment variable? Are you able to execute the 'matlab' command without any errors from any directory?")
                print(f"Finished computing results for {key} ({dt})")

                total_all[key] += 1
                if lastl[1] == "NaN" or lastl[3] == "NaN":
                    if not found:
                        unk_count[key] += 1
                else:
                    if data[key]['expected_result'] == 'with_cookies' and float(lastl[3]) > float(lastl[1]):
                        if not found:
                            unk_count[key] += 1
                    if data[key]['expected_result'] == 'with_cookies' and float(lastl[3]) <= float(lastl[1]):
                        if not found:
                            unk_count[key] += 1
                    if data[key]['expected_result'] == 'without_cookies' and float(lastl[3]) > float(lastl[1]):
                        if not found:
                            unk_count[key] += 1
                    if data[key]['expected_result'] == 'without_cookies' and float(lastl[3]) <= float(lastl[1]):
                        if not found:
                            unk_count[key] += 1

tpr_acc = 0
tnr_acc = 0
ar_acc = 0
tpr_bt_acc = 0
tnr_bt_acc = 0
ar_bt_acc = 0
total_sites = 0

# Create confusion matrices and save results to file
for key in total_all:
    confusion_matrix = [[tn_count[key], fp_count[key]], [fn_count[key], tp_count[key]]]
    confusion_matrix_bt = [[tn_count_bt[key], fp_count_bt[key]], [fn_count_bt[key], tp_count_bt[key]]]
    labels = ["Negative", "Positive"]
    df_cm = pd.DataFrame(confusion_matrix, index=[f"Actual {label}" for label in labels], columns=[f"Predicted {label}" for label in labels])
    df_cm.to_csv("Cross_Site_Results/" + key + "/" + key + "_confusion_matrix.csv", index=True)
    df_cm = pd.DataFrame(confusion_matrix_bt, index=[f"Actual {label}" for label in labels], columns=[f"Predicted {label}" for label in labels])
    df_cm.to_csv("Cross_Site_Results/" + key + "/" + key + "_confusion_matrix_bt.csv", index=True)
    with open("Cross_Site_Results/" + key + "/" + key + "_confusion_matrices_unknown.txt", "a") as file:
        file.write("Unknown Count: " + str(unk_count[key]) + "\n")
        file.write("Baking Timer Unknown Count: " + str(unk_count_bt[key]) + "\n")
        file.write("Total (fp, tp, fn, tn, unk): " + str(total_all[key]) + "\n")
    with open("Cross_Site_Results/" + key + "/" + key + "_confusion_matrices_rates.txt", "a") as file:
        file.write("True Positive Rate: " + str(tp_count[key] / (tp_count[key] + fn_count[key]) if (tp_count[key] + fn_count[key]) > 0 else 0) + "\n")
        file.write("True Negative Rate: " + str(tn_count[key] / (tn_count[key] + fp_count[key]) if (tn_count[key] + fp_count[key]) > 0 else 0) + "\n")
        file.write("Abstention Rate: " + str(unk_count[key] / total_all[key]) + "\n\n")
        file.write("True Positive Rate BT: " + str(tp_count_bt[key] / (tp_count_bt[key] + fn_count_bt[key]) if (tp_count_bt[key] + fn_count_bt[key]) > 0 else 0) + "\n")
        file.write("True Negative Rate BT: " + str(tn_count_bt[key] / (tn_count_bt[key] + fp_count_bt[key]) if (tn_count_bt[key] + fp_count_bt[key]) > 0 else 0) + "\n")
        file.write("Abstention Rate BT: " + str(unk_count_bt[key] / total_all[key]) + "\n")
        if not ((unk_count[key] / total_all[key]) >= 0.50 and (unk_count_bt[key] / total_all[key]) >= 0.50):
            tpr_acc += (tp_count[key] / (tp_count[key] + fn_count[key]) if (tp_count[key] + fn_count[key]) > 0 else 0)
            tnr_acc += (tn_count[key] / (tn_count[key] + fp_count[key]) if (tn_count[key] + fp_count[key]) > 0 else 0)
            ar_acc += (unk_count[key] / total_all[key])
            tpr_bt_acc += (tp_count_bt[key] / (tp_count_bt[key] + fn_count_bt[key]) if (tp_count_bt[key] + fn_count_bt[key]) > 0 else 0)
            tnr_bt_acc += (tn_count_bt[key] / (tn_count_bt[key] + fp_count_bt[key]) if (tn_count_bt[key] + fp_count_bt[key]) > 0 else 0)
            ar_bt_acc += (unk_count_bt[key] / total_all[key])
            total_sites += 1

with open("Cross_Site_Results/overall_confusion_matrices_rates.txt", "a") as file:
    file.write("True Positive Rate: " + str(tpr_acc / total_sites) + "\n")
    file.write("True Negative Rate: " + str(tnr_acc / total_sites) + "\n")
    file.write("Abstention Rate: " + str(ar_acc / total_sites) + "\n\n")
    file.write("True Positive Rate BT: " + str(tpr_bt_acc / total_sites) + "\n")
    file.write("True Negative Rate BT: " + str(tnr_bt_acc / total_sites) + "\n")
    file.write("Abstention Rate BT: " + str(ar_bt_acc / total_sites) + "\n")
