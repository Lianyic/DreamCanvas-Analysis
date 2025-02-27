document.addEventListener("DOMContentLoaded", function () {
    const analyzeBtn = document.getElementById("analyzeBtn");
    const resultBox = document.getElementById("analysisResult");
    const dreamText = document.getElementById("dreamAnalysis");
    const dreamImage = document.getElementById("dreamImage");
    const spotifyPlaylist = document.getElementById("spotifyPlaylist");

    analyzeBtn.addEventListener("click", function () {
        console.log("Analyse button clicked!");

        const userInput = document.getElementById("dreamContent").value.trim();
        const dreamDate = document.getElementById("dreamDate").value;

        if (!userInput || !dreamDate) {
            alert("Please enter a dream description and select a date!");
            return;
        }

        const requestData = {
            date: dreamDate,
            type: document.getElementById("type").value,
            characters: document.getElementById("characters").value,
            environment: document.getElementById("environment").value,
            emotion: document.getElementById("emotion").value,
            text: userInput
        };

        resultBox.style.display = "flex";
        dreamText.innerHTML = "<p>Analysing...</p>";
        dreamImage.style.display = "none";
        spotifyPlaylist.style.display = "none";

        fetch("/analyze", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(requestData)
        })
        .then(response => response.json())
        .then(data => {
            console.log("🔹 AI Analysis Result:", data.analysis);
            console.log("🔹 Image URL:", data.image_url);
            console.log("🔹 Spotify Playlist URL:", data.playlist_url);

            if (dreamText) {
                dreamText.innerHTML = marked.parse(data.analysis);
            }

            if (dreamImage && data.image_url) {
                dreamImage.src = data.image_url;
                dreamImage.style.display = "block";
            } else if (dreamImage) {
                dreamImage.style.display = "none";
            }

            if (spotifyPlaylist && data.playlist_url) {
                spotifyPlaylist.src = `https://open.spotify.com/embed/playlist/${data.playlist_url.split('/playlist/')[1]}`;
                spotifyPlaylist.style.display = "block";
            } else if (spotifyPlaylist) {
                spotifyPlaylist.style.display = "none";
            }
        })
        .catch(error => {
            console.error("Request Failed:", error);
            if (resultBox) {
                dreamText.innerHTML = `<p style="color:red;">Error: ${error.message}</p>`;
            }
        });
    });
});
