function onSubmit() {
    console.log("HI BEN");
}

function createPlaylist() {
    var txt;
    var current_url = window.location;
    if(confirm("Would you like to create a playlist with these songs?")) {
        txt = "Playlist is being created...";
    }
    else {
        txt = "Alas, cancel doesn't work so we're making a playlist anyways!"
    }
    document.getElementById("playlist-button-response").innerHTML = txt;
}

function createRecommendedPlaylist() {
    var txt;
    var current_url = window.location;
    if(confirm("Would you like to create a playlist of recommended songs?")) {
        txt = "Playlist is being created...";
    }
    else {
        txt = "Alas, cancel doesn't work so we're making a playlist anyways!"
    }
    document.getElementById("playlist-button-response").innerHTML = txt;
}
