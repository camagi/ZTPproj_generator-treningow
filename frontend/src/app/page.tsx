"use client";

import { useState, useEffect } from "react";

const API_URL = "http://127.0.0.1:8000/api";
const STATIC_URL = "http://127.0.0.1:8000/exercises-static";
const MUSCLES = ["Klatka", "Plecy", "Nogi", "Barki", "Biceps", "Triceps", "Brzuch"];

const TRANSLATIONS = {
  pl: {
    title: "Generator Planu Treningowego",
    weight: "Waga (kg)",
    height: "Wzrost (cm)",
    days: "Dni w tygodniu",
    experience: "Poziom zaawansowania",
    goal: "Cel treningowy",
    equipment: "Dostępny sprzęt",
    duration: "Czas trwania",
    generate: "Generuj Plan",
    generating: "Generowanie...",
    beginner: "Początkujący",
    intermediate: "Średniozaawansowany",
    advanced: "Zaawansowany",
    reduction: "Redukcja",
    hypertrophy: "Hipertrofia (Masa)",
    strength: "Siła",
    gym: "Siłownia",
    dumbbells: "Hantle",
    bodyweight: "Ciężar ciała",
    bands: "Gumy oporowe",
    short: "Krótki (45 min)",
    medium: "Średni (60 min)",
    long: "Długi (90 min)",
    auto: "Automatyczny dobór",
    replace: "Wymień",
    show: "Pokaż",
    hide: "Ukryj",
    instructions: "Instrukcja",
    no_instructions: "Brak szczegółowych instrukcji.",
    sets: "Serie",
    reps: "Powt.",
    rest: "Przerwa",
    nutrition: "Sugerowane Makroskładniki",
    calories: "Kalorie",
    protein: "Białko",
    fat: "Tłuszcz",
    carbs: "Węglowodany",
    day: "Dzień",
    workout_type: "Preferowany typ",
    blocked_parts: "Zablokowane partie (kontuzje)",
    blocked_desc: "Zaznacz partie, których NIE MOŻESZ trenować.",
    personalization: "Twoja Personalizacja",
    workout_plan: "Plan Treningowy",
    no_results: "Brak wyników do wyświetlenia z powodu podanych przeciwskazań.",
    no_exercises_day: "Brak dostępnych ćwiczeń dla tego dnia.",
    nutrition_desc: "Obliczone dla przeciętnej osoby dorosłej (~30 lat) na podstawie Twoich danych. Dla precyzyjnych wyników skonsultuj się z dietetykiem.",
    approx_values: "Wartości orientacyjne",
  },
  en: {
    title: "Workout Plan Generator",
    weight: "Weight (kg)",
    height: "Height (cm)",
    days: "Days per week",
    experience: "Experience level",
    goal: "Training goal",
    equipment: "Available equipment",
    duration: "Duration",
    generate: "Generate Plan",
    generating: "Generating...",
    beginner: "Beginner",
    intermediate: "Intermediate",
    advanced: "Advanced",
    reduction: "Reduction",
    hypertrophy: "Hypertrophy",
    strength: "Strength",
    gym: "Gym",
    dumbbells: "Dumbbells",
    bodyweight: "Bodyweight",
    bands: "Bands",
    short: "Short (45 min)",
    medium: "Medium (60 min)",
    long: "Long (90 min)",
    auto: "Auto selection",
    replace: "Replace",
    show: "Show",
    hide: "Hide",
    instructions: "Instructions",
    no_instructions: "No detailed instructions.",
    sets: "Sets",
    reps: "Reps",
    rest: "Rest",
    nutrition: "Suggested Nutrition",
    calories: "Calories",
    protein: "Protein",
    fat: "Fat",
    carbs: "Carbs",
    day: "Day",
    workout_type: "Workout Type",
    blocked_parts: "Blocked parts (injuries)",
    blocked_desc: "Select parts you CANNOT train.",
    personalization: "Your Personalization",
    workout_plan: "Workout Plan",
    no_results: "No results to display due to provided contraindications.",
    no_exercises_day: "No exercises available for this day.",
    nutrition_desc: "Calculated for an average adult (~30 years old) based on your data. For precise results, consult a nutritionist.",
    approx_values: "Approximate values",
  }
};

const MUSCLE_GROUPS_MAP: Record<string, { pl: string, en: string }> = {
  "Klatka": { pl: "Klatka", en: "Chest" },
  "Plecy": { pl: "Plecy", en: "Back" },
  "Nogi": { pl: "Nogi", en: "Legs" },
  "Barki": { pl: "Barki", en: "Shoulders" },
  "Biceps": { pl: "Biceps", en: "Biceps" },
  "Triceps": { pl: "Triceps", en: "Triceps" },
  "Brzuch": { pl: "Brzuch", en: "Abs" },
  "Inne": { pl: "Inne", en: "Other" }
};

const CATEGORIES_MAP: Record<string, { pl: string, en: string }> = {
  "Złożone": { pl: "Złożone", en: "Compound" },
  "Izolowane": { pl: "Izolowane", en: "Isolation" }
};

type Exercise = {
  id: number;
  name: string;
  name_pl: string;
  muscle_group: string;
  category: string | null;
  description: string | null;
  sets: number | null;
  reps: string | null;
  rest_time: string | null;
  images?: string[];
  gif_url?: string | null;
  instructions?: string[];
  instructions_pl?: string[];
};

function ExerciseMedia({ images, gif_url, name }: { images: string[], gif_url?: string | null, name: string }) {
  const [currentIdx, setCurrentIdx] = useState(0);
  
  useEffect(() => {
    if (gif_url) return;
    if (!images || images.length <= 1) return;
    const interval = setInterval(() => {
      setCurrentIdx((prev) => (prev + 1) % images.length);
    }, 1000);
    return () => clearInterval(interval);
  }, [images, gif_url]);

  if (gif_url) {
    return (
      <div className="relative w-full h-48 bg-white rounded-xl overflow-hidden border border-gray-200 shadow-inner group-hover:border-blue-300 transition-colors">
        <img 
          src={`${STATIC_URL}/${gif_url}`} 
          alt={name} 
          className="w-full h-full object-contain p-2"
          onError={(e) => {
            (e.target as HTMLImageElement).src = "https://via.placeholder.com/400x400?text=Podgląd+niedostępny";
          }}
        />
      </div>
    );
  }

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
  const [lang, setLang] = useState<'pl' | 'en'>('pl');
  const t = TRANSLATIONS[lang];
  const [loading, setLoading] = useState(false);
  const [plan, setPlan] = useState<PlanResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [replacingId, setReplacingId] = useState<number | null>(null);
  const [showMedia, setShowMedia] = useState<Record<number, boolean>>({});

  const toggleLang = () => {
    setLang(prev => prev === 'pl' ? 'en' : 'pl');
  };

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
      alert(lang === 'pl' ? "Nie znaleziono alternatywnego ćwiczenia." : "No alternative exercise found.");
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

      if (!res.ok) throw new Error("API Error");

      const data = await res.json();
      setPlan(data);
      
      setTimeout(() => {
          document.getElementById("results")?.scrollIntoView({ behavior: "smooth" });
      }, 100);
      
    } catch (err: any) {
      console.error(err);
      setError(lang === 'pl' ? "Błąd połączenia z serwerem." : "Server connection error.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen p-8 sm:p-20 font-[family-name:var(--font-geist-sans)] bg-gray-50 text-gray-900">
      <main className="max-w-3xl mx-auto space-y-12">
        <header className="relative text-center space-y-4">
          <button 
            onClick={toggleLang}
            className="absolute top-0 right-0 p-2 bg-white border border-gray-200 rounded-lg shadow-sm hover:bg-gray-50 font-bold text-sm transition-all"
          >
            {lang === 'pl' ? "🇬🇧 EN" : "🇵🇱 PL"}
          </button>
          <h1 className="text-4xl font-extrabold text-blue-600 tracking-tight">{t.title}</h1>
        </header>

        <section className="bg-white p-6 sm:p-8 rounded-2xl shadow-md border border-gray-100">
          <form onSubmit={handleSubmit} className="space-y-6">
            
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
              <div className="space-y-2">
                <label htmlFor="weight" className="block font-semibold text-gray-700">{t.weight}:</label>
                <input type="number" id="weight" name="weight" step="0.1" required placeholder="75"
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all" />
              </div>

              <div className="space-y-2">
                <label htmlFor="height" className="block font-semibold text-gray-700">{t.height}:</label>
                <input type="number" id="height" name="height" required placeholder="180"
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all" />
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                <div className="space-y-2">
                    <label htmlFor="experience_level" className="block font-semibold text-gray-700">{t.experience}:</label>
                    <select id="experience_level" name="experience_level" defaultValue="intermediate" required
                        className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all bg-white">
                        <option value="beginner">{t.beginner}</option>
                        <option value="intermediate">{t.intermediate}</option>
                        <option value="advanced">{t.advanced}</option>
                    </select>
                </div>
                
                <div className="space-y-2">
                    <label htmlFor="goal" className="block font-semibold text-gray-700">{t.goal}:</label>
                    <select id="goal" name="goal" defaultValue="hypertrophy" required
                        className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all bg-white">
                        <option value="reduction">{t.reduction}</option>
                        <option value="hypertrophy">{t.hypertrophy}</option>
                        <option value="strength">{t.strength}</option>
                    </select>
                </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                <div className="space-y-2">
                    <label htmlFor="equipment" className="block font-semibold text-gray-700">{t.equipment}:</label>
                    <select id="equipment" name="equipment" defaultValue="gym" required
                        className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all bg-white">
                        <option value="gym">{t.gym}</option>
                        <option value="dumbbells">{t.dumbbells}</option>
                        <option value="bodyweight">{t.bodyweight}</option>
                        <option value="bands">{t.bands}</option>
                    </select>
                </div>

                <div className="space-y-2">
                    <label htmlFor="duration" className="block font-semibold text-gray-700">{t.duration}:</label>
                    <select id="duration" name="duration" defaultValue="medium" required
                        className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all bg-white">
                        <option value="short">{t.short}</option>
                        <option value="medium">{t.medium}</option>
                        <option value="long">{t.long}</option>
                    </select>
                </div>

                <div className="space-y-2">
                    <label htmlFor="days" className="block font-semibold text-gray-700">{t.days} (1-5):</label>
                    <input type="number" id="days" name="days" min="1" max="5" required placeholder="3"
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all" />
                </div>
            </div>

            <div className="space-y-2">
                <label htmlFor="workout_type" className="block font-semibold text-gray-700">{t.workout_type}:</label>
                <select id="workout_type" name="workout_type" defaultValue="auto"
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all bg-white">
                    <option value="auto">{t.auto}</option>
                    <option value="FBW">FBW</option>
                    <option value="PPL">PPL</option>
                    <option value="Split">Split</option>
                </select>
            </div>

            <div className="space-y-3 pt-2 border-t border-gray-100">
              <div>
                  <label className="block font-semibold text-gray-700">{t.blocked_parts}:</label>
                  <p className="text-sm text-gray-500">{t.blocked_desc}</p>
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
                {MUSCLES.map(m => (
                  <label key={m} className="flex items-center space-x-2 p-3 bg-gray-50 border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-100 transition-all">
                    <input type="checkbox" name="contraindicated_muscles" value={m} className="w-4 h-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500" />
                    <span className="text-sm font-medium">{MUSCLE_GROUPS_MAP[m]?.[lang] || m}</span>
                  </label>
                ))}
              </div>
            </div>

            <button type="submit" disabled={loading}
              className="w-full py-4 px-6 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-xl transition-all disabled:opacity-50 shadow-md hover:shadow-lg transform hover:-translate-y-0.5 active:translate-y-0">
              {loading ? t.generating : t.generate}
            </button>
            
            {error && <div className="p-4 bg-red-50 text-red-700 rounded-lg text-sm">{error}</div>}
          </form>
        </section>

        {plan && (
          <section id="results" className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <h2 className="text-3xl font-bold text-center text-gray-800">{t.personalization}</h2>
            
            {plan.nutrition && (
              <div className="bg-white p-6 sm:p-8 rounded-2xl shadow-md border border-blue-100 space-y-6">
                <div className="flex items-center justify-between border-b border-gray-100 pb-4">
                  <h3 className="text-xl font-bold text-gray-800 flex items-center gap-2">
                    <span className="text-2xl">🥗</span> {t.nutrition}
                  </h3>
                  <span className="text-xs font-medium text-blue-600 bg-blue-50 px-3 py-1 rounded-full uppercase tracking-wider">{t.approx_values}</span>
                </div>
                
                <p className="text-sm text-gray-500 italic">
                  {t.nutrition_desc}
                </p>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="p-4 bg-blue-600 text-white rounded-xl shadow-sm text-center">
                    <span className="block text-[10px] uppercase font-bold opacity-80 mb-1">{t.calories}</span>
                    <span className="text-2xl font-black">{plan.nutrition.target_calories}</span>
                    <span className="text-[10px] block font-bold">kcal / {lang === 'pl' ? 'dzień' : 'day'}</span>
                  </div>
                  <div className="p-4 bg-gray-50 border border-gray-100 rounded-xl text-center">
                    <span className="block text-[10px] uppercase font-bold text-gray-400 mb-1">{t.protein}</span>
                    <span className="text-2xl font-black text-gray-800">{plan.nutrition.protein_g}g</span>
                  </div>
                  <div className="p-4 bg-gray-50 border border-gray-100 rounded-xl text-center">
                    <span className="block text-[10px] uppercase font-bold text-gray-400 mb-1">{t.fat}</span>
                    <span className="text-2xl font-black text-gray-800">{plan.nutrition.fat_g}g</span>
                  </div>
                  <div className="p-4 bg-gray-50 border border-gray-100 rounded-xl text-center">
                    <span className="block text-[10px] uppercase font-bold text-gray-400 mb-1">{t.carbs}</span>
                    <span className="text-2xl font-black text-gray-800">{plan.nutrition.carbs_g}g</span>
                  </div>
                </div>
              </div>
            )}

            <div className="pt-4">
              <h3 className="text-2xl font-bold text-gray-800 mb-6 text-center">{t.workout_plan}</h3>
              
              {plan.days.length === 0 ? (
                  <div className="text-center p-8 bg-white rounded-2xl shadow-sm">
                      <p className="text-gray-500">{t.no_results}</p>
                  </div>
              ) : (
                  <div className="space-y-6">
                      {plan.days.map((day) => (
                      <div key={day.day} className="bg-white rounded-2xl shadow-md border border-gray-100 overflow-hidden">
                        <div className="bg-blue-50 px-6 py-4 border-b border-gray-200 flex justify-between items-center">
                        <h3 className="text-xl font-bold text-blue-800">{t.day} {day.day}</h3>
                        <span className="bg-blue-100 text-blue-800 text-sm font-semibold px-3 py-1 rounded-full">{day.focus}</span>
                        </div>
                        
                        <div className="p-6">
                        {day.exercises.length === 0 ? (
                            <p className="text-gray-500 italic">{t.no_exercises_day}</p>
                        ) : (
                            <ul className="space-y-3">
                            {day.exercises.map((ex, idx) => (
                                <li key={ex.id || idx} className="flex flex-col p-4 rounded-xl bg-gray-50 border border-gray-100 hover:border-blue-200 hover:shadow-sm transition-all group">
                                <div className="flex flex-col sm:flex-row sm:items-center justify-between">
                                <div className="flex flex-col flex-1">
                                    <div className="flex items-center gap-2">
                                        <span className="font-semibold text-gray-800">{lang === 'pl' ? ex.name_pl : ex.name}</span>
                                        <div className="flex gap-1">
                                            <button 
                                                onClick={() => {
                                                    const equipment = (new FormData(document.querySelector('form')!)).get('equipment') as string;
                                                    handleReplaceExercise(plan.days.indexOf(day), idx, ex, equipment);
                                                }}
                                                disabled={replacingId === ex.id}
                                                title={t.replace}
                                                className="opacity-0 group-hover:opacity-100 transition-opacity p-1.5 hover:bg-blue-100 text-blue-600 rounded-lg text-xs font-bold flex items-center gap-1"
                                            >
                                                {replacingId === ex.id ? "⌛" : `🔄 ${t.replace}`}
                                            </button>
                                            <button 
                                                onClick={() => toggleMedia(ex.id)}
                                                className="opacity-0 group-hover:opacity-100 transition-opacity p-1.5 hover:bg-green-100 text-green-600 rounded-lg text-xs font-bold flex items-center gap-1"
                                            >
                                                {showMedia[ex.id] ? `👁️ ${t.hide}` : `👁️ ${t.show}`}
                                            </button>
                                        </div>
                                    </div>
                                    <div className="flex gap-2 mt-1">
                                        <span className="text-[10px] uppercase tracking-wider font-bold text-gray-500">
                                          {MUSCLE_GROUPS_MAP[ex.muscle_group]?.[lang] || ex.muscle_group}
                                        </span>
                                        {ex.category && (
                                          <span className="text-[10px] uppercase tracking-wider font-bold text-blue-500">
                                            {CATEGORIES_MAP[ex.category]?.[lang] || ex.category}
                                          </span>
                                        )}
                                    </div>
                                </div>
                                <div className="flex items-center gap-4 mt-3 sm:mt-0">
                                    <div className="text-center px-3 py-1 bg-white border border-gray-200 rounded-lg shadow-sm">
                                        <span className="block text-[10px] text-gray-400 font-bold uppercase">{t.sets}</span>
                                        <span className="text-lg font-bold text-blue-600">{ex.sets}</span>
                                    </div>
                                    <div className="text-center px-3 py-1 bg-white border border-gray-200 rounded-lg shadow-sm">
                                        <span className="block text-[10px] text-gray-400 font-bold uppercase">{t.reps}</span>
                                        <span className="text-lg font-bold text-blue-600">{ex.reps}</span>
                                    </div>
                                    <div className="text-center px-3 py-1 bg-white border border-gray-200 rounded-lg shadow-sm min-w-[70px]">
                                        <span className="block text-[10px] text-gray-400 font-bold uppercase">{t.rest}</span>
                                        <span className="text-lg font-bold text-blue-600">{ex.rest_time}</span>
                                    </div>
                                </div>
                                </div>
                                
                                {showMedia[ex.id] && (
                                    <div className="mt-4 pt-4 border-t border-gray-200 animate-in fade-in slide-in-from-top-2 duration-300">
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                            <ExerciseMedia images={ex.images || []} gif_url={ex.gif_url} name={ex.name} />
                                            <div className="space-y-2">
                                                <h4 className="text-xs font-bold text-gray-400 uppercase tracking-widest">{t.instructions}</h4>
                                                <ul className="text-sm text-gray-600 space-y-1.5 list-disc list-inside">
                                                    {(lang === 'pl' ? ex.instructions_pl : ex.instructions || []).map((step, i) => (
                                                        <li key={i} className="leading-relaxed">{step}</li>
                                                    ))}
                                                    {((lang === 'pl' ? !ex.instructions_pl || ex.instructions_pl.length === 0 : !ex.instructions || ex.instructions.length === 0)) && (
                                                        <li className="italic text-gray-400">{t.no_instructions}</li>
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
