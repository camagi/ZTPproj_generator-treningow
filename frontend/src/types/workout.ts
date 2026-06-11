export type Exercise = {
  id: number;
  instance_key?: string;
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

export type NutritionResponse = {
  target_calories: number;
  protein_g: number;
  fat_g: number;
  carbs_g: number;
};

export type WorkoutDayResponse = {
  day: number;
  focus: string;
  exercises: Exercise[];
  warmup: Exercise[];
};

export type PlanResponse = {
  days: WorkoutDayResponse[];
  nutrition: NutritionResponse | null;
};

export type PlanRequestPayload = {
  weight: number;
  height: number;
  days_per_week: number;
  experience_level: string;
  goal: string;
  equipment: string;
  duration: string;
  include_warmup: boolean;
  contraindicated_muscles: string[];
  workout_type?: string;
};

export type GeneratedExercise = Exercise & {
  instance_key: string;
};

export type GeneratedWorkoutDay = Omit<WorkoutDayResponse, "exercises" | "warmup"> & {
  exercises: GeneratedExercise[];
  warmup: GeneratedExercise[];
};

export type FormSelectField = {
  n: string;
  t: string;
  d: string;
  opts: { v: string; l: string }[];
  type?: never;
  min?: never;
  max?: never;
  p?: never;
};

export type FormNumberField = {
  n: string;
  t: string;
  type: "number";
  min: number;
  max: number;
  p: string;
  d?: never;
  opts?: never;
};

export type NutritionStat = {
  l: string;
  v: number;
  u: string;
  g?: boolean;
};


