document.addEventListener("DOMContentLoaded", () => {
    const debounce = (callback, wait) => {
        let timeoutId;

        return (...args) => {
            window.clearTimeout(timeoutId);
            timeoutId = window.setTimeout(() => callback(...args), wait);
        };
    };

    const requestSuggestion = async (text, context, target) => {
        if (!target) {
            return;
        }

        if (!text || text.trim().length < 12) {
            target.classList.add("d-none");
            return;
        }

        target.classList.remove("d-none");
        target.textContent = "Getting OpenAI suggestion...";

        try {
            const response = await fetch("/ai_suggestion", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    question: text,
                    context,
                }),
            });
            const data = await response.json();

            target.textContent = data.suggestion || "No suggestion returned.";
            target.classList.toggle("alert-danger", !data.success);
            target.classList.toggle("alert-info", data.success);
        } catch (error) {
            target.textContent = "Unable to fetch OpenAI suggestion right now.";
            target.classList.remove("alert-info");
            target.classList.add("alert-danger");
        }
    };

    const bindSuggestion = (inputId, targetId, context) => {
        const input = document.getElementById(inputId);
        const target = document.getElementById(targetId);

        if (!input || !target) {
            return;
        }

        input.addEventListener(
            "input",
            debounce(() => requestSuggestion(input.value, context, target), 900)
        );
    };

    bindSuggestion(
        "chatbotQuestion",
        "chatbotAiSuggestion",
        "real-time healthcare chatbot suggestion"
    );

    bindSuggestion(
        "appointmentSymptoms",
        "appointmentAiSuggestion",
        "appointment symptom triage and suitable doctor suggestion"
    );
});
