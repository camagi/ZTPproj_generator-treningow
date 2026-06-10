"use client";

import { useState } from "react";

const API_URL = "http://127.0.0.1:8000/api";
const MUSCLES = ["Klatka", "Plecy", "Nogi", "Barki", "Biceps", "Triceps", "Brzuch"];

type Exercise = {
  id: number;
  name: string;
  muscle_group: string;
  category: string | null;
  description: string | null;
  sets: number | null;
  reps: string | null;
};

type WorkoutDay = {
  day: number;
  focus: string;
  exercises: Exercise[];
};

type PlanResponse = {
  days: WorkoutDay[];
};

export default function Home() {
  const [loading, setLoading] = useState(false);
  const [plan, setPlan] = useState<PlanResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setPlan(null);

    const formData = new FormData(e.currentTarget);
    const contraindicated_muscles = formData.getAll("contraindicated_muscles") as string[];
    
    // Ustaw payload z uwzględnieniem opcjonalnego workout_type
    const payload: any = {
      weight: parseFloat(formData.get("weight") as string),
      height: parseFloat(formData.get("height") as string),
      days_per_week: parseInt(formData.get("days") as string),
      experience_level: formData.get("experience_level") as string,
      goal: formData.get("goal") as string,
      equipment: formData.get("equipment") as string,
      contraindicated_muscles,
    };

    const workoutType = formData.get("workout_type");
    if (workoutType !== "auto") {
        payload.workout_type = workoutType;
    }

    try {
      const res = await fetch(`${API_URL}/generate-plan`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        throw new Error("Błąd podczas generowania planu API.");
      }

      const data = await res.json();
      setPlan(data);
      
      // Scroll to results after a short delay to allow render
      setTimeout(() => {
          document.getElementById("results")?.scrollIntoView({ behavior: "smooth" });
      }, 100);
      
    } catch (err: any) {
      console.error(err);
      setError("Wystąpił błąd podczas łączenia z serwerem. Upewnij się, że backend (FastAPI) jest włączony.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen p-8 sm:p-20 font-[family-name:var(--font-geist-sans)] bg-gray-50 text-gray-900">
      <main className="max-w-3xl mx-auto space-y-12">
        <header className="text-center space-y-4">
          <h1 className="text-4xl font-extrabold text-blue-600 tracking-tight">Generator Planów Treningowych</h1>
          <p className="text-gray-600 max-w-xl mx-auto">Stwórz swój spersonalizowany plan treningowy dopasowany do Twojego poziomu i celów!</p>
        </header>

        <section className="bg-white p-6 sm:p-8 rounded-2xl shadow-md border border-gray-100">
          <form onSubmit={handleSubmit} className="space-y-6">
            
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
              <div className="space-y-2">
                <label htmlFor="weight" className="block font-semibold text-gray-700">Masa ciała (kg):</label>
                <input type="number" id="weight" name="weight" step="0.1" required placeholder="np. 75"
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all" />
              </div>

              <div className="space-y-2">
                <label htmlFor="height" className="block font-semibold text-gray-700">Wzrost (cm):</label>
                <input type="number" id="height" name="height" required placeholder="np. 180"
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all" />
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                <div className="space-y-2">
                    <label htmlFor="experience_level" className="block font-semibold text-gray-700">Poziom zaawansowania:</label>
                    <select id="experience_level" name="experience_level" defaultValue="intermediate" required
                        className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all bg-white">
                        <option value="beginner">Początkujący</option>
                        <option value="intermediate">Średniozaawansowany</option>
                        <option value="advanced">Zaawansowany</option>
                    </select>
                </div>
                
                <div className="space-y-2">
                    <label htmlFor="goal" className="block font-semibold text-gray-700">Cel treningowy:</label>
                    <select id="goal" name="goal" defaultValue="hypertrophy" required
                        className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all bg-white">
                        <option value="reduction">Redukcja (Utrata wagi)</option>
                        <option value="hypertrophy">Hipertrofia (Budowa masy)</option>
                        <option value="strength">Siła (Maksymalna siła)</option>
                    </select>
                </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                <div className="space-y-2">
                    <label htmlFor="equipment" className="block font-semibold text-gray-700">Dostępny sprzęt:</label>
                    <select id="equipment" name="equipment" defaultValue="gym" required
                        className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all bg-white">
                        <option value="gym">Pełna siłownia</option>
                        <option value="dumbbells">Tylko hantle</option>
                        <option value="bodyweight">Kalistenika (Masa własna)</option>
                        <option value="bands">Gumy oporowe</option>
                    </select>
                </div>

                <div className="space-y-2">
                    <label htmlFor="days" className="block font-semibold text-gray-700">Ilość dni w tygodniu (1-5):</label>
                    <input type="number" id="days" name="days" min="1" max="5" required placeholder="np. 3"
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all" />
                </div>
            </div>

            <div className="space-y-2">
                <label htmlFor="workout_type" className="block font-semibold text-gray-700">Preferowany typ treningu:</label>
                <select id="workout_type" name="workout_type" defaultValue="auto"
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all bg-white">
                    <option value="auto">Automatyczny dobór</option>
                    <option value="FBW">Full Body Workout (FBW)</option>
                    <option value="PPL">Push / Pull / Legs</option>
                    <option value="Split">Split (Partie rozdzielone)</option>
                </select>
            </div>

            <div className="space-y-3 pt-2 border-t border-gray-100">
              <div>
                  <label className="block font-semibold text-gray-700">Zablokowane partie (kontuzje):</label>
                  <p className="text-sm text-gray-500">Zaznacz partie, których NIE MOŻESZ trenować.</p>
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
                {MUSCLES.map(m => (
                  <label key={m} className="flex items-center space-x-2 p-3 bg-gray-50 border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-100 transition-colors">
                    <input type="checkbox" name="contraindicated_muscles" value={m} className="w-4 h-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500" />
                    <span className="text-sm font-medium">{m}</span>
                  </label>
                ))}
              </div>
            </div>

            <button type="submit" disabled={loading}
              className="w-full py-4 px-6 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-xl transition-all disabled:opacity-50 shadow-md hover:shadow-lg transform hover:-translate-y-0.5 active:translate-y-0">
              {loading ? "Generowanie..." : "Generuj Plan Treningowy"}
            </button>
            
            {error && <div className="p-4 bg-red-50 text-red-700 rounded-lg text-sm">{error}</div>}
          </form>
        </section>

        {plan && (
          <section id="results" className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <h2 className="text-3xl font-bold text-center text-gray-800">Twój Plan Treningowy</h2>
            
            {plan.days.length === 0 ? (
                <div className="text-center p-8 bg-white rounded-2xl shadow-sm">
                    <p className="text-gray-500">Brak wyników do wyświetlenia z powodu podanych przeciwskazań.</p>
                </div>
            ) : (
                <div className="space-y-6">
                    {plan.days.map((day) => (
                    <div key={day.day} className="bg-white rounded-2xl shadow-md border border-gray-100 overflow-hidden">
                        <div className="bg-blue-50 px-6 py-4 border-b border-gray-200 flex justify-between items-center">
                        <h3 className="text-xl font-bold text-blue-800">Dzień {day.day}</h3>
                        <span className="bg-blue-100 text-blue-800 text-sm font-semibold px-3 py-1 rounded-full">{day.focus}</span>
                        </div>
                        
                        <div className="p-6">
                        {day.exercises.length === 0 ? (
                            <p className="text-gray-500 italic">Brak dostępnych ćwiczeń dla tego dnia.</p>
                        ) : (
                            <ul className="space-y-3">
                            {day.exercises.map((ex, idx) => (
                                <li key={ex.id || idx} className="flex flex-col sm:flex-row sm:items-center justify-between p-4 rounded-xl bg-gray-50 border border-gray-100 hover:border-blue-200 hover:shadow-sm transition-all">
                                <div className="flex flex-col">
                                    <span className="font-semibold text-gray-800">{ex.name}</span>
                                    <div className="flex gap-2 mt-1">
                                        <span className="text-[10px] uppercase tracking-wider font-bold text-gray-500">{ex.muscle_group}</span>
                                        {ex.category && <span className="text-[10px] uppercase tracking-wider font-bold text-blue-500">{ex.category}</span>}
                                    </div>
                                </div>
                                <div className="flex items-center gap-4 mt-3 sm:mt-0">
                                    <div className="text-center px-3 py-1 bg-white border border-gray-200 rounded-lg shadow-sm">
                                        <span className="block text-[10px] text-gray-400 font-bold uppercase">Serie</span>
                                        <span className="text-lg font-bold text-blue-600">{ex.sets}</span>
                                    </div>
                                    <div className="text-center px-3 py-1 bg-white border border-gray-200 rounded-lg shadow-sm">
                                        <span className="block text-[10px] text-gray-400 font-bold uppercase">Powt.</span>
                                        <span className="text-lg font-bold text-blue-600">{ex.reps}</span>
                                    </div>
                                </div>
                                </li>
                            ))}
                            </ul>
                        )}
                        </div>
                    </div>
                    ))}
                </div>
            )}
          </section>
        )}
      </main>
    </div>
  );
}
