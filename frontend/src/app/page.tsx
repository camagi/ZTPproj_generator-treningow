"use client";

import { useState, useEffect } from "react";

const API_URL = "http://127.0.0.1:8000/api";
const STATIC_URL = "http://127.0.0.1:8000/exercises-static";
const MUSCLES = ["Klatka", "Plecy", "Nogi", "Barki", "Biceps", "Triceps", "Brzuch"];

type Exercise = {
  id: number;
  name: string;
  muscle_group: string;
  category: string | null;
  description: string | null;
  sets: number | null;
  reps: string | null;
  rest_time: string | null;
  images?: string[];
  instructions?: string[];
};

function ExerciseMedia({ images, name }: { images: string[], name: string }) {
  const [currentIdx, setCurrentIdx] = useState(0);
  
  useEffect(() => {
    if (!images || images.length <= 1) return;
    const interval = setInterval(() => {
      setCurrentIdx((prev) => (prev + 1) % images.length);
    }, 1000);
    return () => clearInterval(interval);
  }, [images]);

  if (!images || images.length === 0) return (
    <div className="w-full h-48 bg-gray-100 flex items-center justify-center rounded-xl border border-dashed border-gray-300">
        <span className="text-gray-400 text-xs italic">Brak podglądu</span>
    </div>
  );

  return (
    <div className="relative w-full h-48 bg-white rounded-xl overflow-hidden border border-gray-200 shadow-inner group-hover:border-blue-300 transition-colors">
      <img 
        src={`${STATIC_URL}/${images[currentIdx]}`} 
        alt={name} 
        className="w-full h-full object-contain p-2"
        onError={(e) => {
          (e.target as HTMLImageElement).src = "https://via.placeholder.com/400x400?text=Podgląd+niedostępny";
        }}
      />
      {images.length > 1 && (
        <div className="absolute bottom-2 right-2 flex gap-1">
          {images.map((_, i) => (
            <div key={i} className={`w-1.5 h-1.5 rounded-full transition-all ${i === currentIdx ? 'bg-blue-600 w-3' : 'bg-gray-300'}`} />
          ))}
        </div>
      )}
    </div>
  );
}

export default function Home() {
  const [loading, setLoading] = useState(false);
  const [plan, setPlan] = useState<PlanResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [replacingId, setReplacingId] = useState<number | null>(null);
  const [showMedia, setShowMedia] = useState<Record<number, boolean>>({});

  const toggleMedia = (id: number) => {
    setShowMedia(prev => ({ ...prev, [id]: !prev[id] }));
  };

  async function handleReplaceExercise(dayIdx: number, exIdx: number, exercise: Exercise, equipment: string) {
    if (replacingId !== null) return;
    setReplacingId(exercise.id);

    try {
      const res = await fetch(`${API_URL}/exercises/replace`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          current_exercise_id: exercise.id,
          muscle_group: exercise.muscle_group,
          category: exercise.category,
          equipment: equipment,
        }),
      });

      if (!res.ok) throw new Error("Błąd podczas wymiany ćwiczenia.");

      const newEx = await res.json();
      
      // Zachowaj parametry (serie, powtórzenia, przerwa) ze starego ćwiczenia
      const updatedEx = {
        ...newEx,
        sets: exercise.sets,
        reps: exercise.reps,
        rest_time: exercise.rest_time
      };

      setPlan((prev) => {
        if (!prev) return prev;
        const newDays = [...prev.days];
        newDays[dayIdx].exercises[exIdx] = updatedEx;
        return { ...prev, days: newDays };
      });

    } catch (err) {
      console.error(err);
      alert("Nie znaleziono alternatywnego ćwiczenia o podobnym wzorcu.");
    } finally {
      setReplacingId(null);
    }
  }

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
      duration: formData.get("duration") as string,
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
                    <label htmlFor="duration" className="block font-semibold text-gray-700">Czas trwania treningu:</label>
                    <select id="duration" name="duration" defaultValue="medium" required
                        className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all bg-white">
                        <option value="short">45 minut (Krótki)</option>
                        <option value="medium">60 minut (Standardowy)</option>
                        <option value="long">90 minut (Długi)</option>
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
            <h2 className="text-3xl font-bold text-center text-gray-800">Twoja Personalizacja</h2>
            
            {plan.nutrition && (
              <div className="bg-white p-6 sm:p-8 rounded-2xl shadow-md border border-blue-100 space-y-6">
                <div className="flex items-center justify-between border-b border-gray-100 pb-4">
                  <h3 className="text-xl font-bold text-gray-800 flex items-center gap-2">
                    <span className="text-2xl">🥗</span> Sugerowane Zalecenia Dietetyczne
                  </h3>
                  <span className="text-xs font-medium text-blue-600 bg-blue-50 px-3 py-1 rounded-full uppercase tracking-wider">Wartości orientacyjne</span>
                </div>
                
                <p className="text-sm text-gray-500 italic">
                  Obliczone dla przeciętnej osoby dorosłej (~30 lat) na podstawie Twoich danych. Dla precyzyjnych wyników skonsultuj się z dietetykiem.
                </p>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="p-4 bg-blue-600 text-white rounded-xl shadow-sm text-center">
                    <span className="block text-[10px] uppercase font-bold opacity-80 mb-1">Cel Kaloryczny</span>
                    <span className="text-2xl font-black">{plan.nutrition.target_calories}</span>
                    <span className="text-[10px] block font-bold">kcal / dzień</span>
                  </div>
                  <div className="p-4 bg-gray-50 border border-gray-100 rounded-xl text-center">
                    <span className="block text-[10px] uppercase font-bold text-gray-400 mb-1">Białko</span>
                    <span className="text-2xl font-black text-gray-800">{plan.nutrition.protein_g}g</span>
                  </div>
                  <div className="p-4 bg-gray-50 border border-gray-100 rounded-xl text-center">
                    <span className="block text-[10px] uppercase font-bold text-gray-400 mb-1">Tłuszcze</span>
                    <span className="text-2xl font-black text-gray-800">{plan.nutrition.fat_g}g</span>
                  </div>
                  <div className="p-4 bg-gray-50 border border-gray-100 rounded-xl text-center">
                    <span className="block text-[10px] uppercase font-bold text-gray-400 mb-1">Węglowodany</span>
                    <span className="text-2xl font-black text-gray-800">{plan.nutrition.carbs_g}g</span>
                  </div>
                </div>
              </div>
            )}

            <div className="pt-4">
              <h3 className="text-2xl font-bold text-gray-800 mb-6 text-center">Plan Treningowy</h3>
              
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
                                <li key={ex.id || idx} className="flex flex-col p-4 rounded-xl bg-gray-50 border border-gray-100 hover:border-blue-200 hover:shadow-sm transition-all group">
                                <div className="flex flex-col sm:flex-row sm:items-center justify-between">
                                <div className="flex flex-col flex-1">
                                    <div className="flex items-center gap-2">
                                        <span className="font-semibold text-gray-800">{ex.name}</span>
                                        <div className="flex gap-1">
                                            <button 
                                                onClick={() => {
                                                    const equipment = (new FormData(document.querySelector('form')!)).get('equipment') as string;
                                                    handleReplaceExercise(plan.days.indexOf(day), idx, ex, equipment);
                                                }}
                                                disabled={replacingId === ex.id}
                                                title="Wymień na inne"
                                                className="opacity-0 group-hover:opacity-100 transition-opacity p-1.5 hover:bg-blue-100 text-blue-600 rounded-lg text-xs font-bold flex items-center gap-1"
                                            >
                                                {replacingId === ex.id ? "⌛" : "🔄 Wymień"}
                                            </button>
                                            <button 
                                                onClick={() => toggleMedia(ex.id)}
                                                className="opacity-0 group-hover:opacity-100 transition-opacity p-1.5 hover:bg-green-100 text-green-600 rounded-lg text-xs font-bold flex items-center gap-1"
                                            >
                                                {showMedia[ex.id] ? "👁️ Ukryj" : "👁️ Pokaż"}
                                            </button>
                                        </div>
                                    </div>
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
                                    <div className="text-center px-3 py-1 bg-white border border-gray-200 rounded-lg shadow-sm min-w-[70px]">
                                        <span className="block text-[10px] text-gray-400 font-bold uppercase">Przerwa</span>
                                        <span className="text-lg font-bold text-blue-600">{ex.rest_time}</span>
                                    </div>
                                </div>
                                </div>
                                
                                {showMedia[ex.id] && (
                                    <div className="mt-4 pt-4 border-t border-gray-200 animate-in fade-in slide-in-from-top-2 duration-300">
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                            <ExerciseMedia images={ex.images || []} name={ex.name} />
                                            <div className="space-y-2">
                                                <h4 className="text-xs font-bold text-gray-400 uppercase tracking-widest">Instrukcja</h4>
                                                <ul className="text-sm text-gray-600 space-y-1.5 list-disc list-inside">
                                                    {(ex.instructions || []).map((step, i) => (
                                                        <li key={i} className="leading-relaxed">{step}</li>
                                                    ))}
                                                    {(!ex.instructions || ex.instructions.length === 0) && (
                                                        <li className="italic text-gray-400">Brak szczegółowych instrukcji.</li>
                                                    )}
                                                </ul>
                                            </div>
                                        </div>
                                    </div>
                                )}
                                </li>
                            ))}
                            </ul>
                        )}
                        </div>
                    </div>
                    ))}
                  </div>
              )}
            </div>
          </section>
        )}
      </main>
    </div>
  );
}
