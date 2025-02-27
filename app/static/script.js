document.addEventListener("DOMContentLoaded", function () {
    const analyzeBtn = document.getElementById("analyzeBtn");
    const resultBox = document.getElementById("analysisResult");

    resultBox.style.display = "none"; // Hide result initially

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

            let resultHTML = `
                <!-- Top Section: Title & Date -->
                <div class="result-header">
                    <h2 class="result-title">${data.title || "Dream Analysis"}</h2>
                    <p class="result-date">📅 Date: ${dreamDate}</p>
                </div>

                <!-- Playlist on Top -->
                ${data.playlist_url ? `
                    <div class="spotify-container">
                        <iframe class="spotify-iframe" src="https://open.spotify.com/embed/playlist/${data.playlist_url.split('/playlist/')[1]}" 
                            width="400" height="100" frameborder="0" allowtransparency="true" allow="encrypted-media">
                        </iframe>
                    </div>
                ` : ""}

                <!-- Image + Dream Text -->
                <div class="result-container">
                    <!-- Image on the left -->
                    ${data.image_url ? `<img src="${data.image_url}" alt="Dream Visualization" class="dream-image">` : ""}
                    
                    <!-- Dream analysis text -->
                    <div class="dream-text">
                        ${marked.parse(data.analysis)}
                    </div>
                </div>
            `;

            resultBox.innerHTML = resultHTML;
            resultBox.style.display = "block";  // Show result
        })
        .catch(error => {
            console.error("❌ Request Failed:", error);
            resultBox.innerHTML = `<p style="color:red;">Error: ${error.message}</p>`;
            resultBox.style.display = "block";
        });
    });
});
