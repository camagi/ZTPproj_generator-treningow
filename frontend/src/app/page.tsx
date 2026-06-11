"use client";

import { useState, useEffect } from "react";

const API_URL = "http://127.0.0.1:8000/api";
const STATIC_URL = "http://127.0.0.1:8000/exercises-static";
const MUSCLES = ["Klatka", "Plecy", "Nogi", "Barki", "Biceps", "Triceps", "Brzuch"];

const TRANSLATIONS = {
  pl: {
    title: "Workout Designer",
    weight: "Waga (kg)",
    height: "Wzrost (cm)",
    days: "Dni w tygodniu",
    experience: "Poziom zaawansowania",
    goal: "Cel treningowy",
    equipment: "Dostępny sprzęt",
    duration: "Czas trwania",
    generate: "Generuj Plan",
    generating: "Tworzenie...",
    beginner: "Początkujący",
    intermediate: "Średniozaawansowany",
    advanced: "Zaawansowany",
    reduction: "Redukcja",
    hypertrophy: "Hipertrofia",
    strength: "Siła",
    gym: "Siłownia",
    dumbbells: "Hantle",
    bodyweight: "Masa ciała",
    bands: "Gumy",
    short: "Krótki (45 min)",
    medium: "Średni (60 min)",
    long: "Długi (90 min)",
    auto: "Automatyczny",
    replace: "Wymień",
    show: "Pokaż",
    hide: "Ukryj",
    instructions: "Instrukcja",
    no_instructions: "Brak szczegółowych instrukcji.",
    sets: "Serie",
    reps: "Powt.",
    rest: "Przerwa",
    nutrition: "Makroskładniki",
    calories: "Kalorie",
    protein: "Białko",
    fat: "Tłuszcz",
    carbs: "Węglowodany",
    day: "Dzień",
    workout_type: "Typ treningu",
    blocked_parts: "Zablokowane partie",
    blocked_desc: "Zaznacz partie, których nie możesz trenować.",
    personalization: "Twój Plan",
    workout_plan: "Harmonogram Treningowy",
    no_results: "Brak wyników dla podanych parametrów.",
    no_exercises_day: "Brak ćwiczeń.",
    nutrition_desc: "Wartości obliczone dla przeciętnej osoby dorosłej na podstawie Twoich danych.",
    approx_values: "Szacunkowe",
    include_warmup: "Dodaj rozgrzewkę",
    warmup_desc: "Osobna sekcja z ćwiczeniami mobilizacyjnymi przed treningiem.",
  },
  en: {
    title: "Workout Designer",
    weight: "Weight (kg)",
    height: "Height (cm)",
    days: "Days per week",
    experience: "Level",
    goal: "Goal",
    equipment: "Equipment",
    duration: "Duration",
    generate: "Generate Plan",
    generating: "Creating...",
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
    auto: "Automatic",
    replace: "Replace",
    show: "Show",
    hide: "Hide",
    instructions: "Instructions",
    no_instructions: "No instructions available.",
    sets: "Sets",
    reps: "Reps",
    rest: "Rest",
    nutrition: "Nutrition",
    calories: "Calories",
    protein: "Protein",
    fat: "Fat",
    carbs: "Carbs",
    day: "Day",
    workout_type: "Workout Type",
    blocked_parts: "Blocked parts",
    blocked_desc: "Select parts you cannot train.",
    personalization: "Your Plan",
    workout_plan: "Workout Schedule",
    no_results: "No results for given parameters.",
    no_exercises_day: "No exercises.",
    nutrition_desc: "Calculated based on your input for an average adult.",
    approx_values: "Approximate",
    include_warmup: "Add warm-up",
    warmup_desc: "A separate section with mobility exercises before workout.",
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

const SUB_MUSCLE_MAP: Record<string, {pl: string, en: string}> = {
    "Góra klatki": { pl: "Góra klatki", en: "Upper Chest" },
    "Dół klatki": { pl: "Dół klatki", en: "Lower Chest" },
    "Środek klatki": { pl: "Środek klatki", en: "Middle Chest" },
    "Szerokość pleców": { pl: "Szerokość pleców", en: "Lats / Back Width" },
    "Grubość i górny grzbiet": { pl: "Grubość i górny grzbiet", en: "Upper Back & Thickness" },
    "Dół pleców": { pl: "Dół pleców", en: "Lower Back" },
    "Przód uda": { pl: "Przód uda", en: "Quads" },
    "Tył uda": { pl: "Tył uda", en: "Hamstrings" },
    "Pośladki": { pl: "Pośladki", en: "Glutes" },
    "Łydki - górna część": { pl: "Łydki - górna", en: "Upper Calves" },
    "Łydki - dolna część": { pl: "Łydki - dolna", en: "Lower Calves" },
    "Wewnętrzna strona ud": { pl: "Wewnętrzna strona ud", en: "Inner Thighs" },
    "Zewnętrzna strona ud": { pl: "Zewnętrzna strona ud", en: "Outer Thighs" },
    "Przedni akton": { pl: "Przód barku", en: "Front Delts" },
    "Boczny akton": { pl: "Bok barku", en: "Side Delts" },
    "Tylny akton": { pl: "Tył barku", en: "Rear Delts" },
    "Biceps - głowa długa": { pl: "Biceps (gł. długa)", en: "Biceps (Long Head)" },
    "Biceps - głowa krótka": { pl: "Biceps (gł. krótka)", en: "Biceps (Short Head)" },
    "Triceps - głowa długa": { pl: "Triceps (gł. długa)", en: "Triceps (Long Head)" },
    "Triceps - głowa boczna i przyśrodkowa": { pl: "Triceps (boczny/przyśr.)", en: "Triceps (Lateral/Medial)" },
    "Góra przedramienia": { pl: "Góra przedramienia", en: "Upper Forearms" },
    "Dół przedramienia": { pl: "Dół przedramienia", en: "Lower Forearms" },
    "Góra brzucha": { pl: "Góra brzucha", en: "Upper Abs" },
    "Dół brzucha": { pl: "Dół brzucha", en: "Lower Abs" },
    "Boki brzucha": { pl: "Boki brzucha", en: "Obliques" },
    "Głęboka stabilizacja": { pl: "Głęboka stabilizacja", en: "Core Stabilization" },
    "Biceps - ogólnie": { pl: "Biceps - ogólnie", en: "Biceps (General)" },
};

type Exercise = {
  id: number;
  name: string;
  name_pl: string;
  muscle_group: string;
  sub_muscle: string | null;
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

type NutritionResponse = {
  target_calories: number;
  protein_g: number;
  fat_g: number;
  carbs_g: number;
};

type WorkoutDayResponse = {
  day: number;
  focus: string;
  exercises: Exercise[];
};

type PlanResponse = {
  days: WorkoutDayResponse[];
  nutrition: NutritionResponse | null;
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
      <div className="relative w-full h-64 bg-white rounded-3xl overflow-hidden shadow-inner border border-white/10">
        <img 
          src={`${STATIC_URL}/${gif_url}`} 
          alt={name} 
          className="w-full h-full object-contain p-2"
          onError={(e) => {
            (e.target as HTMLImageElement).src = "https://via.placeholder.com/400x400?text=Preview+Not+Available";
          }}
        />
      </div>
    );
  }

  if (!images || images.length === 0) return (
    <div className="w-full h-64 bg-white/5 flex items-center justify-center rounded-3xl border border-dashed border-white/10">
        <span className="text-gray-500 text-sm italic font-medium">Brak podglądu</span>
    </div>
  );

  return (
    <div className="relative w-full h-64 bg-white rounded-3xl overflow-hidden shadow-inner border border-white/10">
      <img 
        src={`${STATIC_URL}/${images[currentIdx]}`} 
        alt={name} 
        className="w-full h-full object-contain p-2"
        onError={(e) => {
          (e.target as HTMLImageElement).src = "https://via.placeholder.com/400x400?text=Preview+Not+Available";
        }}
      />
      {images.length > 1 && (
        <div className="absolute bottom-4 right-4 flex gap-1.5">
          {images.map((_, i) => (
            <div key={i} className={`w-2 h-2 rounded-full transition-all ${i === currentIdx ? 'bg-orange-500 w-4' : 'bg-white/30'}`} />
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

      if (!res.ok) throw new Error("Replace failed");

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
      alert(lang === 'pl' ? "Nie znaleziono alternatywy." : "No alternative found.");
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
      include_warmup: formData.get("include_warmup") === "on",
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
      }, 200);
      
    } catch (err: any) {
      console.error(err);
      setError(lang === 'pl' ? "Błąd połączenia z serwerem." : "Server connection error.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen p-4 sm:p-12 md:p-24 font-[family-name:var(--font-geist-sans)] bg-[#0B0F19] text-white selection:bg-orange-500/30">
      <main className="max-w-6xl mx-auto space-y-24">
        
        {/* Header */}
        <header className="relative flex flex-col items-center justify-center space-y-6 pt-6">
          <button 
            onClick={toggleLang}
            className="absolute top-0 right-0 px-4 py-2 bg-white/5 border border-white/10 rounded-full shadow-lg hover:bg-white/10 backdrop-blur-xl font-black text-[9px] tracking-[0.2em] transition-all active:scale-90"
          >
            {lang === 'pl' ? "ENGLISH" : "POLSKI"}
          </button>
          
          <div className="flex flex-col items-center space-y-4">
            <div className="w-16 h-1 bg-gradient-to-r from-orange-500 to-red-600 rounded-full mb-2"></div>
            <h1 className="text-4xl sm:text-6xl md:text-8xl font-black text-transparent bg-clip-text bg-gradient-to-b from-white via-white to-white/50 tracking-tighter text-center leading-none">
              {t.title}
            </h1>
            <p className="text-gray-500 max-w-md mx-auto text-center text-lg sm:text-xl font-medium tracking-tight leading-relaxed px-4">
              {lang === 'pl' ? "Elitarny system projektowania siły i sylwetki." : "Elite strength and physique engineering system."}
            </p>
          </div>
        </header>

        {/* Glass Form Container */}
        <section className="bg-white/[0.03] p-6 sm:p-12 md:p-16 rounded-[40px] sm:rounded-[60px] shadow-2xl border border-white/10 backdrop-blur-3xl relative overflow-hidden group">
          <div className="absolute -top-24 -right-24 w-96 h-96 bg-orange-600/10 rounded-full blur-[100px] group-hover:bg-orange-600/20 transition-all duration-1000"></div>
          
          <form onSubmit={handleSubmit} className="space-y-10 relative z-10">
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 sm:gap-12">
              <div className="space-y-3">
                <label className="text-[10px] font-black uppercase tracking-[0.3em] text-gray-500 ml-2">{t.weight}</label>
                <input type="number" name="weight" step="0.1" required placeholder="75"
                  className="w-full p-6 sm:p-8 bg-white/5 border border-white/5 rounded-[24px] sm:rounded-[32px] text-white text-2xl sm:text-3xl font-black focus:bg-white/10 focus:border-orange-500/50 outline-none transition-all placeholder:text-gray-800 shadow-2xl" />
              </div>
              <div className="space-y-3">
                <label className="text-[10px] font-black uppercase tracking-[0.3em] text-gray-500 ml-2">{t.height}</label>
                <input type="number" name="height" required placeholder="180"
                  className="w-full p-6 sm:p-8 bg-white/5 border border-white/5 rounded-[24px] sm:rounded-[32px] text-white text-2xl sm:text-3xl font-black focus:bg-white/10 focus:border-orange-500/50 outline-none transition-all placeholder:text-gray-800 shadow-2xl" />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 sm:gap-12">
              <div className="space-y-3">
                <label className="text-[10px] font-black uppercase tracking-[0.3em] text-gray-500 ml-2">{t.experience}</label>
                <select name="experience_level" defaultValue="intermediate" required
                    className="w-full p-6 sm:p-8 bg-white/5 border border-white/5 rounded-[24px] sm:rounded-[32px] text-white text-xl sm:text-2xl font-black focus:bg-white/10 outline-none transition-all appearance-none cursor-pointer shadow-2xl">
                    <option value="beginner" className="bg-[#131B2B]">{t.beginner}</option>
                    <option value="intermediate" className="bg-[#131B2B]">{t.intermediate}</option>
                    <option value="advanced" className="bg-[#131B2B]">{t.advanced}</option>
                </select>
              </div>
              <div className="space-y-3">
                <label className="text-[10px] font-black uppercase tracking-[0.3em] text-gray-500 ml-2">{t.goal}</label>
                <select name="goal" defaultValue="hypertrophy" required
                    className="w-full p-6 sm:p-8 bg-white/5 border border-white/5 rounded-[24px] sm:rounded-[32px] text-white text-xl sm:text-2xl font-black focus:bg-white/10 outline-none transition-all appearance-none cursor-pointer shadow-2xl">
                    <option value="reduction" className="bg-[#131B2B]">{t.reduction}</option>
                    <option value="hypertrophy" className="bg-[#131B2B]">{t.hypertrophy}</option>
                    <option value="strength" className="bg-[#131B2B]">{t.strength}</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 sm:gap-8">
              {[ {n:'equipment', t:t.equipment, d:'gym', opts:[{v:'gym', l:t.gym},{v:'dumbbells', l:t.dumbbells},{v:'bodyweight', l:t.bodyweight},{v:'bands', l:t.bands}]},
                 {n:'duration', t:t.duration, d:'medium', opts:[{v:'short', l:t.short},{v:'medium', l:t.medium},{v:'long', l:t.long}]},
                 {n:'days', t:t.days, type:'number', min:1, max:5, p:'3'}
              ].map((f:any) => (
                <div key={f.n} className="space-y-3">
                  <label className="text-[10px] font-black uppercase tracking-[0.3em] text-gray-500 ml-2">{f.t}</label>
                  {f.opts ? (
                    <select name={f.n} defaultValue={f.d} required
                      className="w-full p-5 sm:p-6 bg-white/5 border border-white/5 rounded-[24px] text-white text-lg sm:text-xl font-black focus:bg-white/10 outline-none transition-all appearance-none cursor-pointer">
                      {f.opts.map((o:any)=><option key={o.v} value={o.v} className="bg-[#131B2B]">{o.l}</option>)}
                    </select>
                  ) : (
                    <input type={f.type} name={f.n} min={f.min} max={f.max} required placeholder={f.p}
                      className="w-full p-5 sm:p-6 bg-white/5 border border-white/5 rounded-[24px] text-white text-lg sm:text-xl font-black focus:bg-white/10 outline-none transition-all shadow-2xl" />
                  )}
                </div>
              ))}
            </div>

            <div className="space-y-4 pt-8 border-t border-white/5">
              <label className="text-[10px] font-black uppercase tracking-[0.3em] text-gray-500 ml-2">{t.blocked_parts}</label>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                {MUSCLES.map(m => (
                  <label key={m} className="relative flex items-center justify-center p-5 bg-white/5 border border-white/5 rounded-[24px] cursor-pointer hover:bg-white/10 transition-all active:scale-95 group overflow-hidden">
                    <input type="checkbox" name="contraindicated_muscles" value={m} className="peer hidden" />
                    <div className="absolute inset-0 bg-gradient-to-br from-orange-500 to-red-600 opacity-0 peer-checked:opacity-20 transition-opacity"></div>
                    <span className="relative z-10 text-[11px] font-black text-gray-500 peer-checked:text-white transition-colors tracking-widest uppercase text-center leading-tight">
                      {MUSCLE_GROUPS_MAP[m]?.[lang] || m}
                    </span>
                  </label>
                ))}
              </div>
            </div>

            <div className="pt-6">
              <button type="submit" disabled={loading}
                className="w-full py-8 sm:py-10 px-8 sm:px-12 bg-gradient-to-r from-[#FF512F] to-[#DD2476] hover:from-[#ff6242] hover:to-[#eb358a] text-white text-2xl sm:text-3xl font-black rounded-[32px] sm:rounded-[40px] transition-all disabled:opacity-50 shadow-[0_40px_80px_-15px_rgba(255,81,47,0.4)] hover:shadow-[0_50px_100px_-12px_rgba(255,81,47,0.6)] active:scale-[0.97] tracking-tighter uppercase leading-none">
                {loading ? (
                  <div className="flex items-center justify-center gap-4 sm:gap-6">
                    <div className="w-8 h-8 border-4 border-white/30 border-t-white rounded-full animate-spin"></div>
                    {t.generating}
                  </div>
                ) : t.generate}
              </button>
            </div>
            
            {error && <div className="p-6 bg-red-900/40 border border-red-500/30 text-red-200 rounded-[24px] text-base font-bold text-center">{error}</div>}
          </form>
        </section>

        {/* Results */}
        {plan && (
          <section id="results" className="space-y-24 sm:space-y-32 animate-in fade-in slide-in-from-bottom-20 duration-1000">
            
            {/* Nutrition Glass Card */}
            {plan.nutrition && (
              <div className="bg-white/[0.02] p-8 sm:p-16 rounded-[48px] sm:rounded-[60px] border border-white/10 backdrop-blur-3xl shadow-2xl relative overflow-hidden group">
                <div className="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-orange-500 to-red-600 opacity-50"></div>
                <div className="flex flex-col md:flex-row justify-between items-center gap-8 sm:gap-12 mb-12 sm:mb-16 border-b border-white/5 pb-12 px-4">
                  <div className="text-center md:text-left space-y-2">
                    <h3 className="text-4xl sm:text-5xl font-black tracking-tighter uppercase">{t.nutrition}</h3>
                    <p className="text-gray-500 font-bold text-base sm:text-lg max-w-xs sm:max-w-none">{t.nutrition_desc}</p>
                  </div>
                  <div className="px-8 py-4 bg-orange-500/10 border border-orange-500/20 rounded-full text-orange-500 font-black text-[10px] tracking-[0.3em] uppercase">
                    {t.approx_values}
                  </div>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 sm:gap-8">
                  {[ {l:t.calories, v:plan.nutrition.target_calories, u:'kcal', g:true},
                     {l:t.protein, v:plan.nutrition.protein_g, u:'g'},
                     {l:t.fat, v:plan.nutrition.fat_g, u:'g'},
                     {l:t.carbs, v:plan.nutrition.carbs_g, u:'g'}
                  ].map((s:any)=>(
                    <div key={s.l} className={`p-8 sm:p-10 rounded-[32px] sm:rounded-[40px] text-center border transition-all duration-500 shadow-xl ${s.g ? 'bg-gradient-to-br from-[#FF512F] to-[#DD2476] border-none' : 'bg-white/5 border-white/5 hover:bg-white/10'}`}>
                      <span className={`block text-[10px] font-black uppercase tracking-[0.3em] mb-4 ${s.g ? 'text-white/70' : 'text-gray-500'}`}>{s.l}</span>
                      <span className="text-4xl sm:text-5xl font-black tracking-tighter">{s.v}</span>
                      <span className={`block text-xs font-black mt-2 tracking-widest ${s.g ? 'text-white/50' : 'text-gray-600'}`}>{s.u}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Workout List - Large Glass Tiles */}
            <div className="space-y-24 sm:space-y-32 px-2">
              <h3 className="text-4xl sm:text-6xl font-black text-center tracking-tighter uppercase leading-tight">
                {t.workout_plan}
              </h3>
              
              <div className="space-y-32 sm:space-y-40">
                  {plan.days.map((day) => (
                  <div key={day.day} className="space-y-12 sm:space-y-16">
                    <div className="flex flex-col items-center gap-4 sm:gap-6 px-4">
                      <div className="w-20 h-20 sm:w-24 h-24 bg-gradient-to-br from-[#FF512F] to-[#DD2476] rounded-[28px] sm:rounded-[32px] flex items-center justify-center text-3xl sm:text-4xl font-black shadow-2xl">
                        {day.day}
                      </div>
                      <div className="text-center">
                        <h3 className="text-4xl sm:text-5xl font-black tracking-tighter uppercase">{t.day} {day.day}</h3>
                        <span className="text-orange-500 font-black uppercase tracking-[0.3em] sm:tracking-[0.5em] text-xs sm:text-sm mt-2 block leading-relaxed">{day.focus}</span>
                      </div>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 lg:gap-12">
                      {/* Warm-up Section */}
                      {day.warmup && day.warmup.length > 0 && (
                        <div className="col-span-full space-y-8">
                          <div className="flex items-center gap-4 px-6">
                             <div className="h-px flex-1 bg-white/10"></div>
                             <span className="text-xs font-black text-gray-500 uppercase tracking-[0.5em]">{lang === 'pl' ? 'ROZGRZEWKA' : 'WARM-UP'}</span>
                             <div className="h-px flex-1 bg-white/10"></div>
                          </div>
                          <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
                            {day.warmup.map((ex, w_idx) => (
                              <button 
                                key={`warmup-${ex.id}-${w_idx}`}
                                onClick={() => toggleMedia(ex.id)}
                                className={`group relative w-full text-left p-6 rounded-[32px] border transition-all duration-500 backdrop-blur-3xl overflow-hidden active:scale-[0.98] ${
                                  showMedia[ex.id] 
                                  ? 'bg-orange-500/10 border-orange-500/30 ring-1 ring-orange-500/20' 
                                  : 'bg-white/[0.02] border-white/5 hover:border-white/10 shadow-lg'
                                }`}
                              >
                                <div className="relative z-10 flex flex-col gap-4">
                                  <div className="flex justify-between items-start gap-4">
                                    <h4 className="text-lg font-black leading-tight text-white group-hover:text-orange-400 transition-colors">
                                      {lang === 'pl' ? ex.name_pl : ex.name}
                                    </h4>
                                    <div className="p-2 bg-white/5 rounded-xl group-hover:bg-orange-500/10 transition-all text-gray-700">
                                      {showMedia[ex.id] ? (
                                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round"><path d="m18 15-6-6-6 6"/></svg>
                                      ) : (
                                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round"><path d="m6 9 6 6 6-6"/></svg>
                                      )}
                                    </div>
                                  </div>
                                  <div className="flex items-center justify-between text-[10px] font-black text-gray-500 uppercase tracking-widest border-t border-white/5 pt-3">
                                    <span>{ex.sets} {t.sets}</span>
                                    <span className="text-orange-500/80">{ex.reps} {t.reps}</span>
                                  </div>
                                </div>
                                {showMedia[ex.id] && (
                                  <div className="mt-6 pt-6 border-t border-white/10 animate-in fade-in slide-in-from-top-4 duration-500">
                                     <div className="bg-white rounded-2xl p-1 mb-4 shadow-xl">
                                        <ExerciseMedia images={ex.images || []} gif_url={ex.gif_url} name={ex.name} />
                                     </div>
                                     <p className="text-sm text-gray-400 leading-relaxed italic">{lang === 'pl' ? ex.instructions_pl?.[0] : ex.instructions?.[0]}</p>
                                  </div>
                                )}
                              </button>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Main Exercises Section */}
                      {day.exercises.map((ex, idx) => (
                        <div key={`main-${ex.id}-${idx}`} className="flex flex-col px-1">
                          <button 
                            onClick={() => toggleMedia(ex.id)}
                            className={`group relative w-full text-left p-8 sm:p-12 rounded-[40px] sm:rounded-[50px] border transition-all duration-700 backdrop-blur-3xl overflow-hidden active:scale-[0.98] ${
                              showMedia[ex.id] 
                              ? 'bg-white/10 border-white/30 shadow-[0_50px_100px_-20px_rgba(0,0,0,0.5)] ring-2 ring-orange-500/50' 
                              : 'bg-white/[0.04] border-white/5 hover:bg-white/[0.08] hover:border-white/20 shadow-2xl'
                            }`}
                          >
                            <div className="absolute -top-32 -left-32 w-64 h-64 bg-orange-500/5 rounded-full blur-[80px] group-hover:bg-orange-500/10 transition-colors duration-700"></div>

                            <div className="relative z-10 flex flex-col h-full gap-8 sm:gap-12">
                              <div className="flex justify-between items-start gap-4">
                                <h4 className="text-2xl sm:text-4xl font-black leading-[1.1] tracking-tighter text-white group-hover:text-orange-400 transition-colors duration-500 pr-2">
                                  {lang === 'pl' ? ex.name_pl : ex.name}
                                </h4>
                                <div className="mt-1 shrink-0 p-3 sm:p-4 bg-white/5 rounded-2xl sm:rounded-3xl group-hover:bg-orange-500/20 group-hover:text-orange-400 transition-all text-gray-600 border border-white/5">
                                  {showMedia[ex.id] ? (
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round" className="sm:w-8 sm:h-8"><path d="m18 15-6-6-6 6"/></svg>
                                  ) : (
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round" className="sm:w-8 sm:h-8"><path d="m6 9 6 6 6-6"/></svg>
                                  )}
                                </div>
                              </div>

                              <div className="flex flex-wrap gap-2 sm:gap-3">
                                <span className="px-3 sm:px-5 py-1.5 sm:py-2 bg-white/5 border border-white/5 rounded-xl sm:rounded-2xl text-[9px] sm:text-[10px] font-black uppercase tracking-[0.15em] sm:tracking-[0.2em] text-gray-400">
                                  {MUSCLE_GROUPS_MAP[ex.muscle_group]?.[lang] || ex.muscle_group}
                                </span>
                                {ex.sub_muscle && (
                                  <span className="px-3 sm:px-5 py-1.5 sm:py-2 bg-orange-500/10 border border-orange-500/20 rounded-xl sm:rounded-2xl text-[9px] sm:text-[10px] font-black uppercase tracking-[0.15em] sm:tracking-[0.2em] text-orange-400">
                                    {SUB_MUSCLE_MAP[ex.sub_muscle]?.[lang] || ex.sub_muscle}
                                  </span>
                                )}
                              </div>

                              <div className="grid grid-cols-3 gap-3 sm:gap-4 border-t border-white/5 pt-8 sm:pt-10">
                                {[ {l:t.sets, v:ex.sets}, {l:t.reps, v:ex.reps}, {l:t.rest, v:ex.rest_time, o:true} ].map(m=>(
                                  <div key={m.l} className="flex flex-col items-center p-3 sm:p-4 bg-black/20 rounded-2xl sm:rounded-3xl border border-white/5 shadow-inner transition-transform group-hover:scale-105 duration-500">
                                    <span className="text-[8px] sm:text-[9px] font-black text-gray-500 uppercase tracking-widest mb-1 sm:mb-2 text-center leading-none">{m.l}</span>
                                    <span className={`text-xl sm:text-2xl font-black ${m.o ? 'text-orange-500' : 'text-white'}`}>{m.v}</span>
                                  </div>
                                ))}
                              </div>
                            </div>
                          </button>

                          <div className="relative -mt-8 sm:-mt-10 mx-auto z-20 scale-90 sm:scale-100">
                            <button 
                              onClick={(e) => {
                                  e.stopPropagation();
                                  const equipment = (new FormData(document.querySelector('form')!)).get('equipment') as string;
                                  handleReplaceExercise(plan.days.indexOf(day), idx, ex, equipment);
                              }}
                              disabled={replacingId === ex.id}
                              className="px-8 sm:px-10 py-4 sm:py-5 bg-[#0e1422] border-2 border-white/10 hover:border-orange-500 rounded-full text-[10px] sm:text-xs font-black text-gray-300 hover:text-white transition-all shadow-2xl flex items-center gap-3 sm:gap-4 active:scale-90 group/btn"
                            >
                              {replacingId === ex.id ? (
                                <div className="w-4 h-4 sm:w-5 sm:h-5 border-4 border-white/20 border-t-white rounded-full animate-spin"></div>
                              ) : (
                                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" className="group-hover/btn:rotate-180 transition-transform duration-700 text-orange-500 sm:w-5 sm:h-5"><path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/><path d="M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 6.74-2.74L21 16"/><path d="M16 21v-5h5"/></svg>
                              )}
                              {t.replace.toUpperCase()}
                            </button>
                          </div>

                          {showMedia[ex.id] && (
                            <div className="mt-12 sm:mt-16 px-2 sm:px-6 animate-in fade-in slide-in-from-top-12 duration-1000 space-y-12 sm:space-y-16">
                              <div className="bg-white rounded-[40px] sm:rounded-[60px] p-2 sm:p-3 shadow-[0_100px_150px_-30px_rgba(0,0,0,0.8)] border-4 sm:border-8 border-white/5">
                                <ExerciseMedia images={ex.images || []} gif_url={ex.gif_url} name={ex.name} />
                              </div>
                              <div className="space-y-8 sm:space-y-10 px-2 sm:px-6">
                                <h5 className="text-xl sm:text-2xl font-black uppercase tracking-[0.3em] sm:tracking-[0.4em] flex items-center gap-4 sm:gap-6">
                                  <div className="w-2 h-8 sm:w-3 h-10 bg-orange-500 rounded-full shadow-[0_0_30px_rgba(249,115,22,0.8)]"></div>
                                  {t.instructions}
                                </h5>
                                <ul className="space-y-8 sm:space-y-10">
                                  {(lang === 'pl' ? ex.instructions_pl : ex.instructions || []).map((step, i) => (
                                    <li key={i} className="flex gap-6 sm:gap-10 group/item">
                                      <div className="flex-shrink-0 w-10 h-10 sm:w-16 sm:h-16 rounded-xl sm:rounded-[24px] bg-white/5 flex items-center justify-center text-lg sm:text-2xl font-black text-orange-500 border border-white/5 group-hover/item:bg-orange-500 group-hover/item:text-white transition-all duration-500 shadow-xl">
                                        {i+1}
                                      </div>
                                      <p className="text-lg sm:text-2xl text-gray-300 font-medium leading-[1.5] sm:leading-[1.6] pt-1 sm:pt-2 group-hover/item:text-white transition-colors duration-500">
                                        {step}
                                      </p>
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                  ))}
              </div>
            </div>
          </section>
        )}
        
        <footer className="pt-40 pb-20 text-center opacity-30">
          <p className="text-[10px] font-black uppercase tracking-[0.8em]">Elite Fitness Intelligence System</p>
        </footer>
      </main>
    </div>
  );
}
