let csrftoken = '{{ csrf_token }}';

const back_button = document.getElementById("hd-button");
back_button.onclick = function () { location.href = '/' }

function getLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(submitPosition);
    } else {
        console.log("Geolocation is not supported by this browser.");
    }
}

function submitPosition(position) {
    const latitude = position.coords.latitude;
    const longitude = position.coords.longitude;
    let data = {
        latitude: latitude,
        longitude: longitude
    };
    let json_data = JSON.stringify(data);

    const url = "/solar/geo"
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: json_data
    }).then(response => {
        if(response.ok) {
            window.location.reload();
        }
    });
}

function submitSolarPanel() {
    const area_value = document.getElementById("area-input").value;
    const efficiency_value = document.getElementById("efficiency-input").value;
    const pr_value = document.getElementById("pr-input").value;
    const capacity_value = document.getElementById("capacity-input").value;

    const data = {
        area: area_value,
        efficiency: efficiency_value,
        pr: pr_value,
        capacity: capacity_value
    };

    const json_data = JSON.stringify(data);
    const url = "/solar/solar-panel";

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: json_data
    }).then(response => {
        if(response.ok) {
            window.location.reload();
        }
    });
}