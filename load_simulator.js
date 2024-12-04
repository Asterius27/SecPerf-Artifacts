import http from 'k6/http';
import { sleep } from 'k6';
import { randomIntBetween } from 'https://jslib.k6.io/k6-utils/1.2.0/index.js';

// Uncomment this if you want to load cookies in an object, so that you can attach them to requests
// const sessionCookie = JSON.parse(open('./session_cookie.json'));

const baseURL = ""
// const baseURL = ""

const paths = [
  "",
  "wp-admin/",
  "wp-admin/update-core.php",
  "wp-admin/edit.php",
  "wp-admin/edit-tags.php?taxonomy=category",
  "wp-admin/upload.php",
  "wp-admin/edit.php?post_type=page",
  "wp-admin/edit-comments.php",
  "wp-admin/themes.php",
  "wp-admin/theme-install.php?browse=popular",
  "wp-admin/plugins.php",
  "wp-admin/plugin-install.php",
  "wp-admin/users.php",
  "wp-admin/user-new.php",
  "wp-admin/import.php",
  "wp-admin/options-general.php",
  "wp-admin/options-reading.php",
  "wp-admin/options-discussion.php",
  "wp-admin/options-permalink.php",
  "wp-admin/profile.php",
  "wp-login.php?loggedout=true&wp_lang=en_US",
  "?page_id=2",
  "?page_id=1",
  "?page_id=3",
  "wp-admin/post.php?post=2&action=edit"
]
// const paths = [
//   "",
//   "deadlines",
//   "users/pc",
//   "forgotpassword",
//   "newaccount",
//   "signin"
// ]

export const options = {
  stages: [
    { duration: '5m', target: 800 }, // Ramp-up to 800 users over 5 minutes
    { duration: '17h57m', target: 800 },  // Stay at 800 users for 18 hours
    { duration: '2m', target: 0 },  // Ramp-down to 0 users over 2 minutes
  ],
};

export default function() {
  const cookiesObject = {
    cookies: sessionCookie.cookies.reduce((acc, cookie) => {
      acc[cookie.name] = cookie.value;
      return acc;
    }, {})
  };

  while(true) {
    for (let i = 0; i < paths.length; i++) {
      // http.get(baseURL + paths[i], cookiesObject); // Use this if you want to send cookies with you requests
      http.get(baseURL + paths[i]);
      sleep(randomIntBetween(7, 15)); // sleep between 7 and 15 seconds (randomly)
    }
  }
}
