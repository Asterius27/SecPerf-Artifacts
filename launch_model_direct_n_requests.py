import subprocess
import re
import os
import json
import numpy as np
import csv
import pandas as pd
import shutil

SITE = 'hotcrp'
EXECUTE_MATLAB = True

results_path = "Direct_Timing_Number_of_Requests_Results/" + SITE + "/"
direct_times_path = f'Direct_Timing_Data/{SITE}/'
th = 15
nbins = 4
thresh = 0.90

try:
    shutil.rmtree("Direct_Timing_Number_of_Requests_Results/" + SITE + "/")
except FileNotFoundError:
    pass
except Exception as e:
    pass

# Return True if qj1 < qi2 (indicating arr1 is entirely to the left of arr2), else return False
def box_test_aux(arr1, arr2, i, j):
    qi1 = np.quantile(arr1, i)
    qj1 = np.quantile(arr1, j)
    qi2 = np.quantile(arr2, i)
    qj2 = np.quantile(arr2, j)
    if qj1 < qi2 or qj2 < qi1:
        if qj1 < qi2:
            return True
        else:
            return False
    else:
        return False

# Implementation of the state-of-the-art attack: Box Test
def box_test(wrong_email, wrong_pw, attack, expected_result, tp_count_bt, fp_count_bt, tn_count_bt, fn_count_bt, unk_count_bt, tp_count_bt_load, fp_count_bt_load, tn_count_bt_load, fn_count_bt_load, unk_count_bt_load, load):
    i = 0.03  # first percentile
    j = 0.05  # second percentile

    if np.mean(wrong_pw) < np.mean(wrong_email):
        vuln = box_test_aux(wrong_pw, wrong_email, i, j)
    else:
        vuln = box_test_aux(wrong_email, wrong_pw, i, j)

    if vuln:
        if np.mean(wrong_pw) < np.mean(attack):
            account_not_exists = box_test_aux(wrong_pw, attack, i, j)
        else:
            account_not_exists = box_test_aux(attack, wrong_pw, i, j)
        if np.mean(wrong_email) < np.mean(attack):
            account_exists = box_test_aux(wrong_email, attack, i, j)
        else:
            account_exists = box_test_aux(attack, wrong_email, i, j)
        if (account_exists and not account_not_exists) or (account_not_exists and not account_exists):
            if account_exists:
                if expected_result == 'wrong_email':
                    fp_count_bt[0] += 1
                    fp_count_bt_load[load] += 1
                if expected_result == 'wrong_pw':
                    tp_count_bt[0] += 1
                    tp_count_bt_load[load] += 1
            if account_not_exists:
                if expected_result == 'wrong_email':
                    tn_count_bt[0] += 1
                    tn_count_bt_load[load] += 1
                if expected_result == 'wrong_pw':
                    fn_count_bt[0] += 1
                    fn_count_bt_load[load] += 1
        else:
            unk_count_bt[0] += 1
            unk_count_bt_load[load] += 1
    else:
        unk_count_bt[0] += 1
        unk_count_bt_load[load] += 1

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

# Load exploration phase data for the specified account. Compute the X^0 and X^1 arrays.
def load_expl_phase(account):
    dirs = os.listdir(direct_times_path)
    expl_resp_times = {}
    loads = {}
    min_user_wrong_pw_mean = float('inf')
    min_email_wrong_pw_mean = float('inf')
    min_user_wrong_user_mean = float('inf')
    min_email_wrong_email_mean = float('inf')
    min_user_wrong_pw_dt = ''
    min_email_wrong_pw_dt = ''
    min_user_wrong_user_dt = ''
    min_email_wrong_email_dt = ''
    for dir in dirs:
        dir_path = os.path.join(direct_times_path, dir)
        for file in os.listdir(dir_path):
            if not file.startswith('old_') and file.endswith('.json'):
                dt = file.split('_')[5] + '_' + file.split('_')[6].split(".")[0]
                load = file.split('_')[0]
                file_path = os.path.join(dir_path, file)
                with open(file_path, 'r') as f:
                    data = json.load(f)

                    # Process X^0 and X^1 means, filtering outliers
                    email_wrong_pw_mean = np.mean(delete_outliers([float(i) for i in data['wrong_pw_times_' + account]]))
                    email_wrong_email_mean = np.mean(delete_outliers([float(i) for i in data['wrong_email_times_' + account]]))

                    # Update minimum means and associated timestamps
                    if email_wrong_pw_mean is not None and email_wrong_pw_mean < min_email_wrong_pw_mean:
                        min_email_wrong_pw_mean = email_wrong_pw_mean
                        min_email_wrong_pw_dt = dt
                    if email_wrong_email_mean is not None and email_wrong_email_mean < min_email_wrong_email_mean:
                        min_email_wrong_email_mean = email_wrong_email_mean
                        min_email_wrong_email_dt = dt
                    expl_resp_times.setdefault(dt, {})

                    expl_resp_times[dt]['email_wrong_pw'] = data['wrong_pw_times_' + account]
                    expl_resp_times[dt]['email_wrong_email'] = data['wrong_email_times_' + account]
                    loads[dt] = load
    return expl_resp_times, loads, min_user_wrong_pw_mean, min_email_wrong_pw_mean, min_user_wrong_user_mean, min_email_wrong_email_mean, min_user_wrong_pw_dt, min_email_wrong_pw_dt, min_user_wrong_user_dt, min_email_wrong_email_dt

# Load both exploration phase data and attack phase data 
expl_resp_times, loads, min_user_wrong_pw_mean, min_email_wrong_pw_mean, min_user_wrong_user_mean, min_email_wrong_email_mean, min_user_wrong_pw_dt, min_email_wrong_pw_dt, min_user_wrong_user_dt, min_email_wrong_email_dt = load_expl_phase('account1')
attack_resp_times, attack_loads, _, _, _, _, _, _, _, _ = load_expl_phase('account2')

tp_count = [0]
fp_count = [0]
tn_count = [0]
fn_count = [0]
unk_count = [0]
tp_count_load = {}
fp_count_load = {}
tn_count_load = {}
fn_count_load = {}
unk_count_load = {}

tp_count_bt = [0]
fp_count_bt = [0]
tn_count_bt = [0]
fn_count_bt = [0]
unk_count_bt = [0]
tp_count_bt_load = {}
fp_count_bt_load = {}
tn_count_bt_load = {}
fn_count_bt_load = {}
unk_count_bt_load = {}

total_load = {}
total_all = [0]

# Process attack phase data to compute metrics
for dt in attack_resp_times:

    # Simulate the attack in the case where the target account does not exists

    found = False

    tp_count_load.setdefault(loads[dt], 0)
    fp_count_load.setdefault(loads[dt], 0)
    tn_count_load.setdefault(loads[dt], 0)
    fn_count_load.setdefault(loads[dt], 0)
    unk_count_load.setdefault(loads[dt], 0)
    tp_count_bt_load.setdefault(loads[dt], 0)
    fp_count_bt_load.setdefault(loads[dt], 0)
    tn_count_bt_load.setdefault(loads[dt], 0)
    fn_count_bt_load.setdefault(loads[dt], 0)
    unk_count_bt_load.setdefault(loads[dt], 0)
    total_load.setdefault(loads[dt], 0)
    
    # Gather X^0, X^1, X^R (BuildModel)
    filt_resp_times_wrong_email_low_load = delete_outliers([float(x) for x in expl_resp_times[min_email_wrong_email_dt]['email_wrong_email']]).tolist()  # X^0
    filt_resp_times_wrong_pw_low_load = delete_outliers([float(x) for x in expl_resp_times[min_email_wrong_pw_dt]['email_wrong_pw']]).tolist()  # X^1
    filt_resp_times_expl = delete_outliers([float(x) for x in expl_resp_times[dt]['email_wrong_email']]).tolist()  # X^R
    
    filt_resp_times_attack_wrong_email = delete_outliers([float(x) for x in attack_resp_times[dt]['email_wrong_email']]).tolist()
    filt_resp_times_attack_wrong_pw = delete_outliers([float(x) for x in attack_resp_times[dt]['email_wrong_pw']]).tolist()
    
    resp_times_wrong_email_low_load_str = "[" + ", ".join(map(str, filt_resp_times_wrong_email_low_load)) + "]"
    resp_times_wrong_pw_low_load_str = "[" + ", ".join(map(str, filt_resp_times_wrong_pw_low_load)) + "]"
    resp_times_expl_str = "[" + ", ".join(map(str, filt_resp_times_expl)) + "]"
    resp_times_attack_wrong_email_str = "[" + ", ".join(map(str, filt_resp_times_attack_wrong_email)) + "]"
    resp_times_attack_wrong_pw_str = "[" + ", ".join(map(str, filt_resp_times_attack_wrong_pw)) + "]"
    
    if EXECUTE_MATLAB:
        # Launch the model (EstimateProba)
        command_wrong_email = 'matlab -batch "cd(\'Model\'); getProbs(' + resp_times_wrong_email_low_load_str + ', ' + resp_times_wrong_pw_low_load_str + ', ' + resp_times_expl_str + ', ' + resp_times_attack_wrong_email_str + ', ' + str(th) + ', ' + str(nbins) + ', ' + str(0) + ');"'
        process = subprocess.Popen(command_wrong_email, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        results = []
        with open(results_path + loads[dt] + "/" + loads[dt] + "_users_results_a_" + dt + '.csv', mode='r') as results_file:
            reader = csv.reader(results_file)
            next(reader)
            for row in reader:
                results.append(row)

    i = 0
    attack_length = 0
    lastl = []
    os.makedirs(f'Direct_Timing_Number_of_Requests_Results/{SITE}/{loads[dt]}', exist_ok=True)
    if EXECUTE_MATLAB:
        liness = process.stdout
    else:
        liness = results

    # Process results from MATLAB and update metrics
    for line in liness:
        i += 1
        if EXECUTE_MATLAB:
            output = line.decode('utf-8').replace(' ', '')
            output_arr = re.split('=|\n', output.replace("\\n", "\n"))
        else:
            output_arr = ["Pr(Omit)=", str(line[1]), "Pr(Include)=", str(line[2]), "Lamda=", '0' if line[14] == '?' else str(line[14]), "Mu=", '1']

        lastl = output_arr
        if output_arr[1] == "NaN" or output_arr[3] == "NaN":
            pass
        else:
            if float(output_arr[1]) > float(output_arr[3]):
                if not found and float(output_arr[1]) >= thresh:
                    tn_count[0] += 1
                    tn_count_load[loads[dt]] += 1
                    found = True
                    attack_length = i
            else:
                if not found and float(output_arr[3]) >= thresh:
                    fp_count[0] += 1
                    fp_count_load[loads[dt]] += 1
                    found = True
                    attack_length = i

        with open(f'Direct_Timing_Number_of_Requests_Results/{SITE}/{loads[dt]}/{loads[dt]}_users_results_a_{dt}.csv', 'a', newline='') as csv_file:
            writer = csv.writer(csv_file)
            if i == 1:
                writer.writerow(['num_attack_obs', 'pr_wrong_email', 'pr_wrong_pw', 'expected_result', 'last_attack_resp_added', 'th'])
            writer.writerow([i, output_arr[1], output_arr[3], 'wrong_email', round(filt_resp_times_attack_wrong_email[i - 1], 3), th])

    total_all[0] += 1
    total_load[loads[dt]] += 1
    if lastl[1] == "NaN" or lastl[3] == "NaN":
        if not found:
            unk_count[0] += 1
            unk_count_load[loads[dt]] += 1
            attack_length = i
    else:
        if float(lastl[1]) > float(lastl[3]):
            if not found:
                unk_count[0] += 1
                unk_count_load[loads[dt]] += 1
                attack_length = i
        else:
            if not found:
                unk_count[0] += 1
                unk_count_load[loads[dt]] += 1
                attack_length = i

    # Execute Box Test for comparison
    box_test(expl_resp_times[dt]['email_wrong_email'], expl_resp_times[dt]['email_wrong_pw'], attack_resp_times[dt]['email_wrong_email'][:attack_length], 
             'wrong_email', tp_count_bt, fp_count_bt, tn_count_bt, fn_count_bt, unk_count_bt,
             tp_count_bt_load, fp_count_bt_load, tn_count_bt_load, fn_count_bt_load, unk_count_bt_load, loads[dt])




    # Now simulate the attack in the case where the target account exists

    found = False

    if EXECUTE_MATLAB:
        # Launch the model (EstimateProba)
        command_wrong_pw = 'matlab -batch "cd(\'Model\'); getProbs(' + resp_times_wrong_email_low_load_str + ', ' + resp_times_wrong_pw_low_load_str + ', ' + resp_times_expl_str + ', ' + resp_times_attack_wrong_pw_str + ', ' + str(th) + ', ' + str(nbins) + ', ' + str(0) + ');"'
        process = subprocess.Popen(command_wrong_pw, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        results = []
        with open(results_path + loads[dt] + "/" + loads[dt] + "_users_results_b_" + dt + '.csv', mode='r') as results_file:
            reader = csv.reader(results_file)
            next(reader)
            for row in reader:
                results.append(row)

    i = 0
    attack_length = 0
    lastl = []
    os.makedirs(f'Direct_Timing_Number_of_Requests_Results/{SITE}/{loads[dt]}', exist_ok=True)
    if EXECUTE_MATLAB:
        liness = process.stdout
    else:
        liness = results

    # Process results from MATLAB and update metrics
    for line in liness:
        i += 1
        if EXECUTE_MATLAB:
            output = line.decode('utf-8').replace(' ', '')
            output_arr = re.split('=|\n', output.replace("\\n", "\n"))
        else:
            output_arr = ["Pr(Omit)=", str(line[1]), "Pr(Include)=", str(line[2]), "Lamda=", '0' if line[14] == '?' else str(line[14]), "Mu=", '1']

        lastl = output_arr
        if output_arr[1] == "NaN" or output_arr[3] == "NaN":
            pass
        else:
            if float(output_arr[1]) <= float(output_arr[3]):
                if not found and float(output_arr[3]) >= thresh:
                    tp_count[0] += 1
                    tp_count_load[loads[dt]] += 1
                    found = True
                    attack_length = i
            else:
                if not found and float(output_arr[1]) >= thresh:
                    fn_count[0] += 1
                    fn_count_load[loads[dt]] += 1
                    found = True
                    attack_length = i

        with open(f'Direct_Timing_Number_of_Requests_Results/{SITE}/{loads[dt]}/{loads[dt]}_users_results_b_{dt}.csv', 'a', newline='') as csv_file:
            writer = csv.writer(csv_file)
            if i == 1:
                writer.writerow(['num_attack_obs', 'pr_wrong_email', 'pr_wrong_pw', 'expected_result', 'last_attack_resp_added', 'th'])
            writer.writerow([i, output_arr[1], output_arr[3], 'wrong_pw', round(filt_resp_times_attack_wrong_pw[i - 1], 3), th])

    total_all[0] += 1
    total_load[loads[dt]] += 1
    if lastl[1] == "NaN" or lastl[3] == "NaN":
        if not found:
            unk_count[0] += 1
            unk_count_load[loads[dt]] += 1
            attack_length = i
    else:
        if float(lastl[1]) <= float(lastl[3]):
            if not found:
                unk_count[0] += 1
                unk_count_load[loads[dt]] += 1
                attack_length = i
        else:
            if not found:
                unk_count[0] += 1
                unk_count_load[loads[dt]] += 1
                attack_length = i
    
        # Execute Box Test for comparison
    box_test(expl_resp_times[dt]['email_wrong_email'], expl_resp_times[dt]['email_wrong_pw'], attack_resp_times[dt]['email_wrong_pw'][:attack_length], 
             'wrong_pw', tp_count_bt, fp_count_bt, tn_count_bt, fn_count_bt, unk_count_bt,
             tp_count_bt_load, fp_count_bt_load, tn_count_bt_load, fn_count_bt_load, unk_count_bt_load, loads[dt])



# Create confusion matrices and save results to file
confusion_matrix = [[tn_count[0], fp_count[0]], [fn_count[0], tp_count[0]]]
confusion_matrix_bt = [[tn_count_bt[0], fp_count_bt[0]], [fn_count_bt[0], tp_count_bt[0]]]
labels = ["Negative", "Positive"]
df_cm = pd.DataFrame(confusion_matrix, index=[f"Actual {label}" for label in labels], columns=[f"Predicted {label}" for label in labels])
df_cm.to_csv("Direct_Timing_Number_of_Requests_Results/" + SITE + "/confusion_matrix.csv", index=True)
df_cm = pd.DataFrame(confusion_matrix_bt, index=[f"Actual {label}" for label in labels], columns=[f"Predicted {label}" for label in labels])
df_cm.to_csv("Direct_Timing_Number_of_Requests_Results/" + SITE + "/confusion_matrix_bt.csv", index=True)
with open("Direct_Timing_Number_of_Requests_Results/" + SITE + "/confusion_matrices_unknown.txt", "a") as file:
    file.write("Unknown Count: " + str(unk_count[0]) + "\n")
    file.write("Baking Timer Unknown Count: " + str(unk_count_bt[0]) + "\n")
    file.write("Total (fp, tp, fn, tn, unk): " + str(total_all[0]) + "\n")
with open("Direct_Timing_Number_of_Requests_Results/" + SITE + "/confusion_matrices_rates.txt", "a") as file:
    file.write("True Positive Rate: " + str(tp_count[0] / (tp_count[0] + fn_count[0]) if (tp_count[0] + fn_count[0]) > 0 else 0) + "\n")
    file.write("True Negative Rate: " + str(tn_count[0] / (tn_count[0] + fp_count[0]) if (tn_count[0] + fp_count[0]) > 0 else 0) + "\n")
    file.write("Abstention Rate: " + str(unk_count[0] / total_all[0]) + "\n\n")
    file.write("True Positive Rate BT: " + str(tp_count_bt[0] / (tp_count_bt[0] + fn_count_bt[0]) if (tp_count_bt[0] + fn_count_bt[0]) > 0 else 0) + "\n")
    file.write("True Negative Rate BT: " + str(tn_count_bt[0] / (tn_count_bt[0] + fp_count_bt[0]) if (tn_count_bt[0] + fp_count_bt[0]) > 0 else 0) + "\n")
    file.write("Abstention Rate BT: " + str(unk_count_bt[0] / total_all[0]) + "\n")

for key in tp_count_load:
    confusion_matrix = [[tn_count_load[key], fp_count_load[key]], [fn_count_load[key], tp_count_load[key]]]
    confusion_matrix_bt = [[tn_count_bt_load[key], fp_count_bt_load[key]], [fn_count_bt_load[key], tp_count_bt_load[key]]]
    labels = ["Negative", "Positive"]
    df_cm = pd.DataFrame(confusion_matrix, index=[f"Actual {label}" for label in labels], columns=[f"Predicted {label}" for label in labels])
    df_cm.to_csv("Direct_Timing_Number_of_Requests_Results/" + SITE + "/" + key + "/confusion_matrix.csv", index=True)
    df_cm = pd.DataFrame(confusion_matrix_bt, index=[f"Actual {label}" for label in labels], columns=[f"Predicted {label}" for label in labels])
    df_cm.to_csv("Direct_Timing_Number_of_Requests_Results/" + SITE + "/" + key + "/confusion_matrix_bt.csv", index=True)
    with open("Direct_Timing_Number_of_Requests_Results/" + SITE + "/" + key + "/confusion_matrices_rates.txt", "a") as file:
        file.write("True Positive Rate: " + str(tp_count_load[key] / (tp_count_load[key] + fn_count_load[key]) if (tp_count_load[key] + fn_count_load[key]) > 0 else 0) + "\n")
        file.write("True Negative Rate: " + str(tn_count_load[key] / (tn_count_load[key] + fp_count_load[key]) if (tn_count_load[key] + fp_count_load[key]) > 0 else 0) + "\n")
        file.write("Abstention Rate: " + str(unk_count_load[key] / total_load[key]) + "\n\n")
        file.write("True Positive Rate BT: " + str(tp_count_bt_load[key] / (tp_count_bt_load[key] + fn_count_bt_load[key]) if (tp_count_bt_load[key] + fn_count_bt_load[key]) > 0 else 0) + "\n")
        file.write("True Negative Rate BT: " + str(tn_count_bt_load[key] / (tn_count_bt_load[key] + fp_count_bt_load[key]) if (tn_count_bt_load[key] + fp_count_bt_load[key]) > 0 else 0) + "\n")
        file.write("Abstention Rate BT: " + str(unk_count_bt_load[key] / total_load[key]) + "\n")
