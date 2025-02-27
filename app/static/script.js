document.addEventListener("DOMContentLoaded", function () {
    const analyzeBtn = document.getElementById("analyzeBtn");
    const resultBox = document.getElementById("analysisResult");
    const dreamTitle = document.getElementById("dreamTitle");
    const dreamImage = document.getElementById("dreamImage");
    const spotifyPlaylist = document.getElementById("spotifyPlaylist");
    const dreamAnalysis = document.getElementById("dreamAnalysis");

    resultBox.style.display = "none";

    analyzeBtn.addEventListener("click", function () {
        console.log("🔹 Analyse button clicked!");

        const userInput = document.getElementById("dreamContent").value.trim();
        const dreamDate = document.getElementById("dreamDate").value;

        if (!userInput || !dreamDate) {
            alert("Please enter a dream description and select a date!");
            return;
        }

        resultBox.style.display = "block";
        dreamTitle.innerHTML = '<p class="analysing-text">Analysing...</p>';
        dreamAnalysis.innerHTML = "";
        dreamImage.style.display = "none";
        spotifyPlaylist.style.display = "none";

        const requestData = {
            date: dreamDate,
            type: document.getElementById("type").value,
            characters: document.getElementById("characters").value,
            environment: document.getElementById("environment").value,
            emotion: document.getElementById("emotion").value,
            text: userInput
        };

        console.log("🔹 Sending Data:", requestData);

        fetch("/analyze", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(requestData)
        })
        .then(response => response.json())
        .then(data => {
            console.log("🔹 AI Title:", data.title);
            console.log("🔹 AI Analysis Result:", data.analysis);
            console.log("🔹 Image URL:", data.image_url);
            console.log("🔹 Spotify Playlist URL:", data.playlist_url);

            dreamTitle.innerHTML = `<h2>${data.title || "Dream Analysis"}</h2>`;

            dreamAnalysis.innerHTML = data.analysis;

            if (data.image_url) {
                dreamImage.src = data.image_url;
                dreamImage.style.display = "block";
            }

            if (data.playlist_url) {
                spotifyPlaylist.src = `https://open.spotify.com/embed/playlist/${data.playlist_url.split('/playlist/')[1]}`;
                spotifyPlaylist.style.display = "block";
            }

            resultBox.style.display = "flex";
        })
        .catch(error => {
            console.error("Request Failed:", error);
            resultBox.innerHTML = `<p style="color:red;">Error: ${error.message}</p>`;
            resultBox.style.display = "block";
        });
    });
});
