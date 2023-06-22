const backBttn = document.getElementById('back-button').querySelector('button');
const linkedinBttn = document.querySelector('#linkedin-bttn > button');
const portfolioBttn = document.querySelector('#portfolio-bttn > button');
const githubBttn = document.querySelector('#github-bttn > button');

let data;
fetch('../static/contact/data.json')
    .then((response) => response.json())
    .then((json) => data = json);

backBttn.onclick = function () { location.href = '/'; };
linkedinBttn.onclick = function () { location.href = data["linkedin"]; }
portfolioBttn.onclick = function () { location.href = data["portfolio"]; }
githubBttn.onclick = function () { location.href = data["github"]; }