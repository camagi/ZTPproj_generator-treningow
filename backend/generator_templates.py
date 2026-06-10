import schemas

TEMPLATES = {
    schemas.WorkoutType.fbw: {
        schemas.ExperienceLevel.beginner: [
            {"focus": "Full Body Workout", "slots": [
                {"muscle": "Nogi", "kw": ["squat", "goblet", "przysiad"], "comp": True},
                {"muscle": "Plecy", "kw": ["pulldown", "pull-up", "chin-up", "ściąganie", "podciąganie"]},
                {"muscle": "Klatka", "kw": ["bench press", "płaska", "płasko", "floor press"]},
                {"muscle": "Plecy", "kw": ["row", "wiosłowanie"]},
                {"muscle": "Barki", "kw": ["shoulder press", "military", "overhead", "nad głowę"]},
                {"muscle": "Biceps", "kw": ["curl", "uginanie"]},
                {"muscle": "Triceps", "kw": ["extension", "pushdown", "prostowanie"]},
                {"muscle": "Brzuch", "kw": ["plank", "deska"]}
            ]}
        ],
        schemas.ExperienceLevel.intermediate: [
            {"focus": "Plan A (Przód i Szerokość)", "slots": [
                {"muscle": "Nogi", "kw": ["squat", "przysiad"]},
                {"muscle": "Klatka", "kw": ["incline", "skos", "góra"]},
                {"muscle": "Plecy", "kw": ["pull-up", "podciąganie", "pulldown"]},
                {"muscle": "Barki", "kw": ["lateral raise", "bok", "wznosy"]},
                {"muscle": "Biceps", "kw": ["curl", "uginanie"]},
                {"muscle": "Triceps", "kw": ["french", "skull crusher", "francuskie"]},
                {"muscle": "Brzuch", "kw": ["leg raise", "unoszenie nóg", "dół"]}
            ]},
            {"focus": "Plan B (Tył i Grubość)", "slots": [
                {"muscle": "Nogi", "kw": ["deadlift", "romanian", "rdl", "martwy"]},
                {"muscle": "Klatka", "kw": ["fly", "rozpiętki", "cable cross"]},
                {"muscle": "Plecy", "kw": ["t-bar", "row", "wiosłowanie"]},
                {"muscle": "Barki", "kw": ["face pull", "rear delt", "tył"]},
                {"muscle": "Nogi", "kw": ["calf", "łydki", "wspięcia"]},
                {"muscle": "Biceps", "kw": ["hammer", "młotk"]},
                {"muscle": "Brzuch", "kw": ["pallof", "twist", "skośn"]}
            ]}
        ],
        schemas.ExperienceLevel.advanced: [
            {"focus": "Plan A (Zaawansowany FBW)", "slots": [
                {"muscle": "Nogi", "kw": ["deadlift", "rdl", "romanian", "martwy"]},
                {"muscle": "Klatka", "kw": ["fly", "rozpiętki", "brama"]},
                {"muscle": "Plecy", "kw": ["t-bar", "row", "wiosłowanie"]},
                {"muscle": "Barki", "kw": ["face pull", "rear", "tył"]},
                {"muscle": "Nogi", "kw": ["calf", "łydki", "wspięcia"]},
                {"muscle": "Biceps", "kw": ["hammer", "młotk"]},
                {"muscle": "Brzuch", "kw": ["pallof", "twist", "core"]}
            ]},
            {"focus": "Plan B (Zaawansowany FBW)", "slots": [
                {"muscle": "Nogi", "kw": ["front squat", "przysiad przedni", "hack"]},
                {"muscle": "Klatka", "kw": ["incline", "skos", "góra"]},
                {"muscle": "Plecy", "kw": ["pull-up", "podciąganie"]},
                {"muscle": "Barki", "kw": ["lateral raise", "bok"]},
                {"muscle": "Triceps", "kw": ["dip", "pompki"]},
                {"muscle": "Biceps", "kw": ["preacher", "modlitewnik"]},
                {"muscle": "Nogi", "kw": ["leg curl", "uginanie nóg"]}
            ]}
        ]
    },
    schemas.WorkoutType.ppl: {
        schemas.ExperienceLevel.beginner: [
            {"focus": "PUSH", "slots": [
                {"muscle": "Klatka", "kw": ["bench press", "płaska", "płasko"]},
                {"muscle": "Barki", "kw": ["military", "ohp", "żołnierskie", "shoulder press"]},
                {"muscle": "Klatka", "kw": ["dip", "push-up", "pompki"]},
                {"muscle": "Triceps", "kw": ["pushdown", "extension", "wyciąg"]}
            ]},
            {"focus": "PULL", "slots": [
                {"muscle": "Plecy", "kw": ["pulldown", "ściąganie"]},
                {"muscle": "Plecy", "kw": ["row", "wiosłowanie"]},
                {"muscle": "Barki", "kw": ["rear", "opad", "tył"]},
                {"muscle": "Biceps", "kw": ["curl", "uginanie"]}
            ]},
            {"focus": "LEGS", "slots": [
                {"muscle": "Nogi", "kw": ["squat", "przysiad"]},
                {"muscle": "Nogi", "kw": ["leg curl", "uginanie"]},
                {"muscle": "Nogi", "kw": ["calf raise", "wspięcia", "stojąc"]},
                {"muscle": "Brzuch", "kw": ["crunch", "brzuszki", "góra"]}
            ]}
        ],
        schemas.ExperienceLevel.intermediate: [
            {"focus": "PUSH", "slots": [
                {"muscle": "Klatka", "kw": ["incline", "skos"]},
                {"muscle": "Barki", "kw": ["shoulder press", "siedząc"]},
                {"muscle": "Klatka", "kw": ["fly", "rozpiętki"]},
                {"muscle": "Barki", "kw": ["lateral raise", "bok"]},
                {"muscle": "Triceps", "kw": ["french", "francuskie", "siedząc", "overhead"]}
            ]},
            {"focus": "PULL", "slots": [
                {"muscle": "Plecy", "kw": ["pull-up", "podciąganie"]},
                {"muscle": "Plecy", "kw": ["row one", "jednorącz", "hantl"]},
                {"muscle": "Plecy", "kw": ["pullover", "straight arm", "prostymi"]},
                {"muscle": "Barki", "kw": ["face pull", "tył"]},
                {"muscle": "Biceps", "kw": ["preacher", "modlitewnik"]}
            ]},
            {"focus": "LEGS", "slots": [
                {"muscle": "Nogi", "kw": ["front squat", "hack"]},
                {"muscle": "Nogi", "kw": ["romanian", "rdl", "martwy"]},
                {"muscle": "Nogi", "kw": ["leg press", "wypychanie", "suwnic"]},
                {"muscle": "Nogi", "kw": ["calf raise seated", "siedząc", "łyd"]},
                {"muscle": "Brzuch", "kw": ["leg raise", "unoszenie", "dół"]}
            ]}
        ],
        schemas.ExperienceLevel.advanced: [
            {"focus": "PUSH", "slots": [
                {"muscle": "Klatka", "kw": ["hammer", "skos", "machine", "maszyn"]},
                {"muscle": "Klatka", "kw": ["dip weighted", "poręcz"]},
                {"muscle": "Barki", "kw": ["lateral cable", "wyciąg", "bok"]},
                {"muscle": "Klatka", "kw": ["guillotine", "bench press", "płask"]},
                {"muscle": "Triceps", "kw": ["close grip", "wąsk"]},
                {"muscle": "Triceps", "kw": ["overhead", "zza głowy", "french"]}
            ]},
            {"focus": "PULL", "slots": [
                {"muscle": "Plecy", "kw": ["deadlift", "martwy"]},
                {"muscle": "Plecy", "kw": ["t-bar", "półsztang"]},
                {"muscle": "Plecy", "kw": ["pulldown single", "jednorącz"]},
                {"muscle": "Barki", "kw": ["reverse fly", "odwrotn"]},
                {"muscle": "Biceps", "kw": ["incline curl", "skos"]},
                {"muscle": "Biceps", "kw": ["hammer", "młotk"]}
            ]},
            {"focus": "LEGS", "slots": [
                {"muscle": "Nogi", "kw": ["hip thrust", "bioder"]},
                {"muscle": "Nogi", "kw": ["leg extension", "prostowanie"]},
                {"muscle": "Nogi", "kw": ["leg curl seated", "siedząc", "jednorącz"]},
                {"muscle": "Nogi", "kw": ["adductor", "abductor", "przywodziciele"]},
                {"muscle": "Nogi", "kw": ["calf standing", "stojąc"]},
                {"muscle": "Brzuch", "kw": ["crunch", "twist", "allachy", "cable"]}
            ]}
        ]
    },
    schemas.WorkoutType.split: {
        schemas.ExperienceLevel.beginner: [
            {"focus": "Dzień 1: Klatka + Biceps", "slots": [
                {"muscle": "Klatka", "kw": ["bench press", "płask"]},
                {"muscle": "Klatka", "kw": ["incline", "skos", "hantl"]},
                {"muscle": "Klatka", "kw": ["fly", "rozpiętk", "płask"]},
                {"muscle": "Biceps", "kw": ["curl barbell", "sztang", "stojąc"]},
                {"muscle": "Biceps", "kw": ["curl dumbbell", "hantl", "supin"]}
            ]},
            {"focus": "Dzień 2: Plecy + Triceps", "slots": [
                {"muscle": "Plecy", "kw": ["pulldown", "ściąganie", "klatk"]},
                {"muscle": "Plecy", "kw": ["row underhand", "podchwyt", "sztang", "row"]},
                {"muscle": "Plecy", "kw": ["hyperextension", "prostownik"]},
                {"muscle": "Triceps", "kw": ["pushdown", "prostowanie", "wyciąg"]},
                {"muscle": "Triceps", "kw": ["french", "francuskie", "leżąc"]}
            ]},
            {"focus": "Dzień 3: Nogi + Barki", "slots": [
                {"muscle": "Nogi", "kw": ["goblet", "squat", "przysiad"]},
                {"muscle": "Nogi", "kw": ["leg extension", "prostowanie"]},
                {"muscle": "Nogi", "kw": ["leg curl", "uginanie"]},
                {"muscle": "Nogi", "kw": ["calf", "wspięcia", "stojąc"]},
                {"muscle": "Barki", "kw": ["shoulder press", "siedząc", "hantl"]},
                {"muscle": "Barki", "kw": ["lateral raise", "bok"]}
            ]}
        ],
        schemas.ExperienceLevel.intermediate: [
            {"focus": "Dzień 1: Klatka + Barki", "slots": [
                {"muscle": "Klatka", "kw": ["incline barbell", "sztang", "skos"]},
                {"muscle": "Klatka", "kw": ["bench press dumbbell", "hantl", "płask"]},
                {"muscle": "Klatka", "kw": ["dip", "poręcz", "push-up"]},
                {"muscle": "Barki", "kw": ["military", "ohp", "żołnierskie"]},
                {"muscle": "Barki", "kw": ["lateral raise", "bok"]}
            ]},
            {"focus": "Dzień 2: Plecy + Tył barku + Brzuch", "slots": [
                {"muscle": "Plecy", "kw": ["deadlift", "martwy"]},
                {"muscle": "Plecy", "kw": ["row dumbbell", "hantl", "wiosło"]},
                {"muscle": "Plecy", "kw": ["seated row", "przyciąganie", "poziom"]},
                {"muscle": "Barki", "kw": ["face pull", "tył"]},
                {"muscle": "Brzuch", "kw": ["leg raise", "unoszenie nóg", "zwis"]}
            ]},
            {"focus": "Dzień 3: Nogi", "slots": [
                {"muscle": "Nogi", "kw": ["squat", "przysiad tylny", "sztang"]},
                {"muscle": "Nogi", "kw": ["romanian", "rdl", "martwy"]},
                {"muscle": "Nogi", "kw": ["lunge", "wykroki"]},
                {"muscle": "Nogi", "kw": ["calf standing", "wspięcia", "stojąc"]},
                {"muscle": "Nogi", "kw": ["calf seated", "wspięcia", "siedząc"]}
            ]},
            {"focus": "Dzień 4: Ramiona", "slots": [
                {"muscle": "Triceps", "kw": ["close grip", "wąsk"]},
                {"muscle": "Biceps", "kw": ["curl barbell", "sztang", "łaman"]},
                {"muscle": "Triceps", "kw": ["pushdown", "link"]},
                {"muscle": "Biceps", "kw": ["incline", "skos", "hantl"]},
                {"muscle": "Biceps", "kw": ["wrist", "nadgarst"]}
            ]}
        ],
        schemas.ExperienceLevel.advanced: [
            {"focus": "Dzień 1: Klatka", "slots": [
                {"muscle": "Klatka", "kw": ["incline dumbbell", "skos", "hantl"]},
                {"muscle": "Klatka", "kw": ["hammer", "maszyn", "dół", "decline"]},
                {"muscle": "Klatka", "kw": ["cable fly", "brama", "dół"]},
                {"muscle": "Klatka", "kw": ["fly", "poziom", "rozpiętk"]},
                {"muscle": "Klatka", "kw": ["push-up", "pompki"]}
            ]},
            {"focus": "Dzień 2: Plecy", "slots": [
                {"muscle": "Plecy", "kw": ["pull-up", "podciąganie", "ciężar"]},
                {"muscle": "Plecy", "kw": ["t-bar", "szerok", "wiosło"]},
                {"muscle": "Plecy", "kw": ["pulldown single", "jednorącz", "pion"]},
                {"muscle": "Plecy", "kw": ["row dumbbell", "hantl", "oparcie"]},
                {"muscle": "Plecy", "kw": ["hyperextension", "prostownik", "obciążen"]}
            ]},
            {"focus": "Dzień 3: Barki", "slots": [
                {"muscle": "Barki", "kw": ["shoulder press", "siedząc", "hantl"]},
                {"muscle": "Barki", "kw": ["lateral cable", "bok", "wyciąg"]},
                {"muscle": "Barki", "kw": ["lateral dumbbell", "bok", "hantl"]},
                {"muscle": "Barki", "kw": ["reverse fly", "odwrotn", "maszyn"]},
                {"muscle": "Plecy", "kw": ["shrug", "szrugsy", "kaptur"]}
            ]},
            {"focus": "Dzień 4: Nogi", "slots": [
                {"muscle": "Nogi", "kw": ["squat", "przysiad", "głębok"]},
                {"muscle": "Nogi", "kw": ["hack", "maszyn"]},
                {"muscle": "Nogi", "kw": ["romanian", "rdl", "hantl"]},
                {"muscle": "Nogi", "kw": ["leg curl seated", "siedząc"]},
                {"muscle": "Nogi", "kw": ["adductor", "przywodziciele"]},
                {"muscle": "Nogi", "kw": ["calf press", "suwnic"]}
            ]},
            {"focus": "Dzień 5: Ramiona + Brzuch", "slots": [
                {"muscle": "Triceps", "kw": ["overhead", "francuskie", "wyciąg", "zza"]},
                {"muscle": "Biceps", "kw": ["preacher single", "modlitewnik", "jednorącz", "preacher"]},
                {"muscle": "Triceps", "kw": ["pushdown rope", "prostowanie", "link"]},
                {"muscle": "Biceps", "kw": ["incline curl", "skos", "hantl"]},
                {"muscle": "Biceps", "kw": ["hammer cable", "młotk", "lin", "hammer"]},
                {"muscle": "Brzuch", "kw": ["crunch cable", "allachy", "skłon"]}
            ]}
        ]
    }
}