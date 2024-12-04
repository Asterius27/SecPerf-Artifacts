from playwright.sync_api import sync_playwright
import time
import random
import string

def generate_random_string(length=8):
    characters = string.ascii_letters + string.digits
    # Use random.choices to generate a random string
    random_string = ''.join(random.choices(characters, k=length))
    return random_string

def measure_signin_response(url, email, password, input_user_name="email", input_pw_name="password", submit_elem="button", endpoint="signin", headless=True):
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context(ignore_https_errors=True)
        page = context.new_page()

        # Navigate to the sign-in page
        page.goto(url)

        request_start_time = {}
        response_times = {}

        # Event listener for request start
        def handle_request(request):
            if endpoint in request.url:
                request_start_time[request.url] = time.time()

        # Event listener for response
        def handle_response(response):
            if endpoint in response.url and response.url in request_start_time:
                start_time = request_start_time[response.url]
                end_time = time.time()
                response_times[response.url] = (end_time - start_time) * 1000  # ms

        page.on("request", handle_request)
        page.on("response", handle_response)

        page.fill(f'input[name="{input_user_name}"]', email)
        page.fill(f'input[name="{input_pw_name}"]', password)
        page.click(f'{submit_elem}[type="submit"]')

        # Wait for navigation or network activity to settle
        page.wait_for_load_state("networkidle")

        # Output response time
        response_time = 0
        for req_url, resp_time in response_times.items():
            response_time = resp_time

        if not headless:
            time.sleep(1)
        browser.close()
        return response_time
    
if __name__ == "__main__":
    # you can test functions here
    pass
