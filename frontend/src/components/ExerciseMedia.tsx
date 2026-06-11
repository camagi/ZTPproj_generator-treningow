"use client";

/* eslint-disable @next/next/no-img-element */
import { useEffect, useState } from "react";
import { STATIC_URL } from "../lib/config";

function MissingMedia() {
  return (
    <div className="w-full h-64 bg-white/5 flex items-center justify-center rounded-3xl border border-dashed border-white/10">
      <span className="text-gray-500 text-sm italic font-medium">Brak podglądu</span>
    </div>
  );
}

export default function ExerciseMedia({ images, gif_url, name }: { images: string[]; gif_url?: string | null; name: string }) {
  const [currentIdx, setCurrentIdx] = useState(0);
  const [failedSource, setFailedSource] = useState<string | null>(null);

  useEffect(() => {
    if (gif_url || !images || images.length <= 1) return;
    const interval = setInterval(() => {
      setCurrentIdx((prev) => (prev + 1) % images.length);
    }, 1000);
    return () => clearInterval(interval);
  }, [images, gif_url]);

  if (!gif_url && (!images || images.length === 0)) {
    return <MissingMedia />;
  }

  const imageIndex = images.length > 0 ? currentIdx % images.length : 0;
  const source = gif_url ? `${STATIC_URL}/${gif_url}` : `${STATIC_URL}/${images[imageIndex]}`;

  if (failedSource === source) {
    return <MissingMedia />;
  }

  return (
    <div className="relative w-full h-64 bg-white rounded-3xl overflow-hidden shadow-inner border border-white/10">
      <img
        src={source}
        alt={name}
        className="w-full h-full object-contain p-2"
        onError={() => setFailedSource(source)}
      />
      {!gif_url && images.length > 1 && (
        <div className="absolute bottom-4 right-4 flex gap-1.5">
          {images.map((_, i) => (
            <div key={i} className={`w-2 h-2 rounded-full transition-all ${i === imageIndex ? "bg-orange-500 w-4" : "bg-white/30"}`} />
          ))}
        </div>
      )}
    </div>
  );
}
