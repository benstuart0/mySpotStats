function onSubmit() {
    console.log("HI BEN");
}

function createPlaylist() {
    var txt;
    if(confirm("Would you like to create a playlist with these songs?")) {
        txt = "Playlist is being created...";
        document.getElementById("playlist-button-response").innerHTML = txt;
    }
}
