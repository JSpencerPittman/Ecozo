const back_button = document.getElementById('back-button').querySelector('button');
back_button.onclick = function () { location.href = '/'; };

let data;
fetch('../static/contact/data.json')
    .then((response) => response.json())
    .then((json) => data = json);

const linkedin_bttn = document.querySelector('#linkedin-bttn > button');
const portfolio_bttn = document.querySelector('#portfolio-bttn > button');
const github_bttn = document.querySelector('#github-bttn > button');

linkedin_bttn.onclick = function () { location.href = data["linkedin"]; }
portfolio_bttn.onclick = function () { location.href = data["portfolio"]; }
github_bttn.onclick = function () { location.href = data["github"]; }