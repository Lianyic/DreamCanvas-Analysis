document.addEventListener("DOMContentLoaded", function () {
    const analyzeBtn = document.getElementById("analyzeBtn");
    const resultBox = document.getElementById("analysisResult");
    const dreamForm = document.getElementById("dreamForm");

    resultBox.style.display = "none";

    analyzeBtn.addEventListener("click", function () {
        console.log("Analyse button clicked!");

        const userInput = document.getElementById("dreamContent").value.trim();
        const dreamDate = document.getElementById("dreamDate").value; // Get the date

        if (!userInput || !dreamDate) {
            alert("Please enter a dream description and select a date!");
            return;
        }

        const requestData = {
            date: dreamDate,  // Add dream date to request
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
            if (data.analysis) {
                console.log("🔹 AI Analysis Result:", data.analysis);

                resultBox.innerHTML = formatAnalysis(data.analysis);
                resultBox.style.display = "block";
            } else {
                console.error("Server Error:", data.error);
                resultBox.innerHTML = `<p style="color:red;">Error: ${data.error || "Unknown error"}</p>`;
                resultBox.style.display = "block";
            }
        })
        .catch(error => {
            console.error("Request Failed:", error);
            resultBox.innerHTML = `<p style="color:red;">Error: ${error.message}</p>`;
            resultBox.style.display = "block";
        });
    });

    function formatAnalysis(text) {
        return marked.parse(text);
    }
});
