const API_URL = "http://127.0.0.1:8000/api";
const MUSCLES = ["Klatka", "Plecy", "Nogi", "Barki", "Biceps", "Triceps", "Brzuch"];

document.addEventListener("DOMContentLoaded", () => {
    const musclesContainer = document.getElementById("muscles-container");
    
    // Generowanie checkboxów z partiami mięśniowymi
    MUSCLES.forEach(muscle => {
        const label = document.createElement("label");
        label.className = "checkbox-label";
        
        const checkbox = document.createElement("input");
        checkbox.type = "checkbox";
        checkbox.name = "contraindicated_muscles";
        checkbox.value = muscle;
        
        label.appendChild(checkbox);
        label.appendChild(document.createTextNode(muscle));
        musclesContainer.appendChild(label);
    });

    // Obsługa formularza
    const form = document.getElementById("plan-form");
    const submitBtn = form.querySelector('button[type="submit"]');

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        
        submitBtn.disabled = true;
        submitBtn.textContent = "Generowanie...";
        
        const formData = new FormData(form);
        const weight = parseFloat(formData.get("weight"));
        const height = parseFloat(formData.get("height"));
        const days = parseInt(formData.get("days"));
        
        const contraindicated_muscles = [];
        document.querySelectorAll('input[name="contraindicated_muscles"]:checked').forEach(cb => {
            contraindicated_muscles.push(cb.value);
        });

        const requestData = {
            weight: weight,
            height: height,
            days_per_week: days,
            contraindicated_muscles: contraindicated_muscles
        };

        try {
            const response = await fetch(`${API_URL}/generate-plan`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(requestData)
            });

            if (!response.ok) {
                throw new Error("Błąd podczas generowania planu API");
            }

            const data = await response.json();
            displayPlan(data);
        } catch (error) {
            console.error(error);
            alert("Wystąpił błąd podczas łączenia z API. Upewnij się, że backend jest uruchomiony.");
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = "Generuj Plan";
        }
    });
});

function displayPlan(data) {
    const resultsSection = document.getElementById("results");
    const planContainer = document.getElementById("plan-container");
    
    planContainer.innerHTML = ""; 
    
    if (data.days.length === 0) {
        planContainer.innerHTML = "<p>Brak wyników do wyświetlenia.</p>";
    }

    data.days.forEach(day => {
        const dayCard = document.createElement("div");
        dayCard.className = "day-card";
        
        const dayHeader = document.createElement("div");
        dayHeader.className = "day-header";
        dayHeader.innerHTML = `<h3>Dzień ${day.day}</h3> <strong>${day.focus}</strong>`;
        dayCard.appendChild(dayHeader);
        
        const exerciseList = document.createElement("ul");
        exerciseList.className = "exercise-list";
        
        if (day.exercises.length === 0) {
            exerciseList.innerHTML = "<p>Brak dostępnych ćwiczeń dla tego dnia z powodu przeciwskazań.</p>";
        } else {
            day.exercises.forEach(ex => {
                const li = document.createElement("li");
                li.className = "exercise-item";
                li.innerHTML = `
                    <span class="exercise-name">${ex.name}</span>
                    <span class="exercise-meta">${ex.muscle_group} ${ex.category ? '| ' + ex.category : ''}</span>
                `;
                exerciseList.appendChild(li);
            });
        }
        
        dayCard.appendChild(exerciseList);
        planContainer.appendChild(dayCard);
    });
    
    resultsSection.classList.remove("hidden");
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}
